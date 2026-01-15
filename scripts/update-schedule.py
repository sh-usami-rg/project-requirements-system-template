#!/usr/bin/env python3
"""
スケジュール更新オーケストレーションスクリプト

タスクの変更を受け付け、全ての関連ファイルとGitHubを自動で更新します。

使用方法:
    # タスクの期限を延長
    python3 scripts/update-schedule.py --task TASK-007 --extend-deadline 7

    # タスクの開始日を変更
    python3 scripts/update-schedule.py --task TASK-015 --start-date 2026-02-10

    # タスクを削除
    python3 scripts/update-schedule.py --task TASK-010 --action delete

    # タスクの優先度を変更
    python3 scripts/update-schedule.py --task TASK-005 --priority high

    # インタラクティブモード
    python3 scripts/update-schedule.py --interactive

前提条件:
    - GitHub CLI (gh) がインストールされていること
    - gh auth login で認証済みであること
    - github-issue-mapping.json が存在すること
"""

import argparse
import json
import subprocess
import sys
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 定数
REPO_FULL_NAME = "sh-usami-rg/dashboard-migration-project"
PROJECT_NUMBER = 3
REPO_OWNER = "sh-usami-rg"


class ScheduleUpdateManager:
    """スケジュール更新マネージャークラス"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.tasks_file = base_dir / "tasks.json"
        self.schedule_file = base_dir / "schedule.json"
        self.schedule_md_file = base_dir / "SCHEDULE.md"
        self.plan_md_file = base_dir / "PLAN.md"
        self.mapping_file = base_dir / "github-issue-mapping.json"

        # バックアップディレクトリ
        self.backup_dir = base_dir / ".backups"
        self.backup_dir.mkdir(exist_ok=True)

        # データ読み込み
        self.tasks_data = self._load_json(self.tasks_file)
        self.schedule_data = self._load_json(self.schedule_file)
        self.issue_mapping = self._load_json(self.mapping_file)

        # 変更追跡
        self.changes = []
        self.errors = []

    def _load_json(self, filepath: Path) -> Dict:
        """JSONファイルを読み込む"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ERROR: File not found: {filepath}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in {filepath}: {e}")
            sys.exit(1)

    def _save_json(self, filepath: Path, data: Dict):
        """JSONファイルを保存"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _backup_files(self):
        """現在のファイルをバックアップ"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = self.backup_dir / timestamp
        backup_subdir.mkdir(exist_ok=True)

        files_to_backup = [
            self.tasks_file,
            self.schedule_file,
            self.schedule_md_file,
            self.plan_md_file,
            self.mapping_file
        ]

        for file in files_to_backup:
            if file.exists():
                shutil.copy2(file, backup_subdir / file.name)

        print(f"✅ バックアップ作成: {backup_subdir}")
        return backup_subdir

    def _restore_from_backup(self, backup_dir: Path):
        """バックアップからファイルを復元"""
        print(f"\n⚠️  エラーが発生したため、バックアップから復元します: {backup_dir}")

        for backup_file in backup_dir.iterdir():
            original_file = self.base_dir / backup_file.name
            shutil.copy2(backup_file, original_file)

        print("✅ バックアップから復元完了")

    def run_gh_command(self, command: List[str]) -> str:
        """GitHub CLIコマンドを実行"""
        try:
            result = subprocess.run(
                ["gh"] + command,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            error_msg = f"GitHub CLIコマンドエラー: {' '.join(command)}"
            if e.stderr:
                error_msg += f"\n詳細: {e.stderr}"
            self.errors.append(error_msg)
            raise

    def run_gh_api(self, query: str) -> Dict:
        """GitHub GraphQL APIを実行"""
        try:
            result = subprocess.run(
                ["gh", "api", "graphql", "-f", f"query={query}"],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            error_msg = f"GraphQL API error: {e.stderr}"
            self.errors.append(error_msg)
            raise

    def find_task_in_schedule(self, task_id: str) -> Optional[Dict]:
        """schedule.json内のタスクを検索"""
        for task in self.schedule_data.get("tasks", []):
            if task["id"] == task_id:
                return task
        return None

    def find_task_in_tasks_json(self, task_id: str) -> Optional[Dict]:
        """tasks.json内のタスクを検索"""
        for task in self.tasks_data.get("tasks", []):
            if task["id"] == task_id:
                return task
        return None

    def extend_deadline(self, task_id: str, days: int):
        """タスクの期限を延長"""
        print(f"\n📅 {task_id}の期限を{days}日延長します...")

        # schedule.jsonのタスクを更新
        schedule_task = self.find_task_in_schedule(task_id)
        if not schedule_task:
            raise ValueError(f"{task_id} が schedule.json に見つかりません")

        # 終了日を延長
        old_end_date = schedule_task["endDate"]
        end_date = datetime.strptime(old_end_date, "%Y-%m-%d")
        new_end_date = end_date + timedelta(days=days)
        schedule_task["endDate"] = new_end_date.strftime("%Y-%m-%d")

        self.changes.append(f"{task_id}: 終了日 {old_end_date} → {schedule_task['endDate']}")
        print(f"  ✓ 終了日更新: {old_end_date} → {schedule_task['endDate']}")

        # 依存タスクも連鎖的に延長する必要があるかチェック
        self._update_dependent_tasks(task_id, days)

    def change_start_date(self, task_id: str, new_start_date: str):
        """タスクの開始日を変更"""
        print(f"\n📅 {task_id}の開始日を{new_start_date}に変更します...")

        # schedule.jsonのタスクを更新
        schedule_task = self.find_task_in_schedule(task_id)
        if not schedule_task:
            raise ValueError(f"{task_id} が schedule.json に見つかりません")

        # 日付の妥当性チェック
        try:
            datetime.strptime(new_start_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"無効な日付形式: {new_start_date}（YYYY-MM-DD形式で指定してください）")

        old_start_date = schedule_task["startDate"]
        schedule_task["startDate"] = new_start_date

        # 工数に基づいて終了日を再計算
        effort_days = schedule_task.get("effort", 1)
        start_date_obj = datetime.strptime(new_start_date, "%Y-%m-%d")
        new_end_date_obj = start_date_obj + timedelta(days=effort_days - 1)
        schedule_task["endDate"] = new_end_date_obj.strftime("%Y-%m-%d")

        self.changes.append(f"{task_id}: 開始日 {old_start_date} → {new_start_date}")
        print(f"  ✓ 開始日更新: {old_start_date} → {new_start_date}")
        print(f"  ✓ 終了日再計算: {schedule_task['endDate']}")

    def delete_task(self, task_id: str):
        """タスクを削除"""
        print(f"\n🗑️  {task_id}を削除します...")

        # tasks.jsonから削除
        tasks_list = self.tasks_data.get("tasks", [])
        original_count = len(tasks_list)
        self.tasks_data["tasks"] = [t for t in tasks_list if t["id"] != task_id]

        if len(self.tasks_data["tasks"]) == original_count:
            raise ValueError(f"{task_id} が tasks.json に見つかりません")

        # schedule.jsonから削除
        schedule_tasks = self.schedule_data.get("tasks", [])
        self.schedule_data["tasks"] = [t for t in schedule_tasks if t["id"] != task_id]

        # 依存関係から削除
        for task in self.tasks_data.get("tasks", []):
            if "dependencies" in task and task_id in task["dependencies"]:
                task["dependencies"].remove(task_id)
                print(f"  ✓ {task['id']}の依存関係から{task_id}を削除")

        for task in self.schedule_data.get("tasks", []):
            if "dependencies" in task and task_id in task["dependencies"]:
                task["dependencies"].remove(task_id)

        self.changes.append(f"{task_id}: タスクを削除")
        print(f"  ✓ {task_id}を削除しました")

    def change_priority(self, task_id: str, new_priority: str):
        """タスクの優先度を変更"""
        valid_priorities = ["high", "medium", "low"]
        if new_priority not in valid_priorities:
            raise ValueError(f"無効な優先度: {new_priority}（high, medium, low のいずれかを指定してください）")

        print(f"\n🎯 {task_id}の優先度を{new_priority}に変更します...")

        # tasks.jsonのタスクを更新
        tasks_task = self.find_task_in_tasks_json(task_id)
        if not tasks_task:
            raise ValueError(f"{task_id} が tasks.json に見つかりません")

        old_priority = tasks_task.get("priority", "")
        tasks_task["priority"] = new_priority

        # schedule.jsonも更新
        schedule_task = self.find_task_in_schedule(task_id)
        if schedule_task:
            schedule_task["priority"] = new_priority

        self.changes.append(f"{task_id}: 優先度 {old_priority} → {new_priority}")
        print(f"  ✓ 優先度更新: {old_priority} → {new_priority}")

    def _update_dependent_tasks(self, task_id: str, days: int):
        """依存タスクを連鎖的に更新"""
        # このタスクに依存しているタスクを探す
        dependent_tasks = []
        for task in self.schedule_data.get("tasks", []):
            if "dependencies" in task and task_id in task["dependencies"]:
                dependent_tasks.append(task)

        if dependent_tasks:
            print(f"\n  📌 依存タスクも自動で延長します:")
            for dep_task in dependent_tasks:
                dep_id = dep_task["id"]
                old_start = dep_task["startDate"]
                old_end = dep_task["endDate"]

                # 開始日と終了日を延長
                start_date = datetime.strptime(old_start, "%Y-%m-%d")
                end_date = datetime.strptime(old_end, "%Y-%m-%d")

                new_start_date = start_date + timedelta(days=days)
                new_end_date = end_date + timedelta(days=days)

                dep_task["startDate"] = new_start_date.strftime("%Y-%m-%d")
                dep_task["endDate"] = new_end_date.strftime("%Y-%m-%d")

                print(f"    ✓ {dep_id}: {old_start} 〜 {old_end} → {dep_task['startDate']} 〜 {dep_task['endDate']}")
                self.changes.append(f"{dep_id}: 依存関係により自動延長 {old_start} → {dep_task['startDate']}")

                # さらに依存しているタスクも再帰的に更新
                self._update_dependent_tasks(dep_id, days)

    def recalculate_weekly_schedule(self):
        """週次スケジュールを再計算"""
        print("\n📊 週次スケジュールを再計算中...")

        # 開始日を取得（プロジェクト情報から）
        project_start = self.schedule_data.get("projectStartDate", "2026-01-06")
        start_date = datetime.strptime(project_start, "%Y-%m-%d")

        # 週ごとのタスクを再集計
        weekly_schedule = []
        week_number = 1
        cumulative_progress = 0

        while True:
            week_start = start_date + timedelta(days=(week_number - 1) * 7)
            week_end = week_start + timedelta(days=4)  # 月〜金（5日間）

            # この週のタスクを検索
            week_tasks = []
            week_progress = 0

            for task in self.schedule_data.get("tasks", []):
                task_start = datetime.strptime(task["startDate"], "%Y-%m-%d")
                task_end = datetime.strptime(task["endDate"], "%Y-%m-%d")

                # タスクがこの週に含まれるかチェック
                if task_start <= week_end and task_end >= week_start:
                    week_tasks.append(task["id"])
                    # 完全にこの週に完了するタスクのみ進捗に加算
                    if task_end <= week_end:
                        week_progress += task.get("weight", 0)

            if not week_tasks:
                # タスクがない週が続いたら終了
                if week_number > 1 and not weekly_schedule[-1]["tasks"]:
                    break

            cumulative_progress += week_progress

            weekly_schedule.append({
                "week": f"Week {week_number}",
                "dateRange": f"{week_start.strftime('%Y-%m-%d')} 〜 {week_end.strftime('%Y-%m-%d')}",
                "tasks": week_tasks,
                "cumulativeProgress": round(cumulative_progress, 1)
            })

            week_number += 1

            # 最大52週（1年）で停止
            if week_number > 52:
                break

        self.schedule_data["weeklySchedule"] = weekly_schedule
        print(f"  ✓ 週次スケジュール再計算完了（{len(weekly_schedule)}週）")

    def regenerate_plan_md(self):
        """PLAN.mdを再生成"""
        print("\n📝 PLAN.mdを再生成中...")

        # 基本情報
        project_info = self.tasks_data.get("project", {})
        project_name = project_info.get("name", "プロジェクト")

        # 日付計算
        tasks = self.schedule_data.get("tasks", [])
        if tasks:
            start_dates = [datetime.strptime(t["startDate"], "%Y-%m-%d") for t in tasks]
            end_dates = [datetime.strptime(t["endDate"], "%Y-%m-%d") for t in tasks]
            project_start = min(start_dates).strftime("%Y-%m-%d")
            project_end = max(end_dates).strftime("%Y-%m-%d")

            # 期間計算
            start_dt = min(start_dates)
            end_dt = max(end_dates)
            total_days = (end_dt - start_dt).days + 1
            total_weeks = len(self.schedule_data.get("weeklySchedule", []))
        else:
            project_start = "未定"
            project_end = "未定"
            total_days = 0
            total_weeks = 0

        # 総工数計算
        total_effort = sum(task.get("effort", 0) for task in tasks)
        total_hours = sum(task.get("effortHours", 0) for task in tasks)
        total_weight = sum(task.get("weight", 0) for task in tasks)

        # Phase別タスク分類
        phase1_tasks = [t for t in tasks if "Phase 1" in t.get("phase", "")]
        phase2_tasks = [t for t in tasks if "Phase 2" in t.get("phase", "")]
        phase3_tasks = [t for t in tasks if "Phase 3" in t.get("phase", "")]

        # Phase別工数
        phase1_effort = sum(t.get("effort", 0) for t in phase1_tasks)
        phase1_hours = sum(t.get("effortHours", 0) for t in phase1_tasks)
        phase1_weight = sum(t.get("weight", 0) for t in phase1_tasks)

        phase2_effort = sum(t.get("effort", 0) for t in phase2_tasks)
        phase2_hours = sum(t.get("effortHours", 0) for t in phase2_tasks)
        phase2_weight = sum(t.get("weight", 0) for t in phase2_tasks)

        phase3_effort = sum(t.get("effort", 0) for t in phase3_tasks)
        phase3_hours = sum(t.get("effortHours", 0) for t in phase3_tasks)
        phase3_weight = sum(t.get("weight", 0) for t in phase3_tasks)

        # PLAN.md生成
        content = f"""# {project_name} 実行計画書

## プロジェクト概要

- **プロジェクト名**: {project_name}
- **開始日**: {project_start}
- **終了日**: {project_end}
- **期間**: {total_weeks}週間（約{total_days}日間）
- **稼働体制**: 1名兼任（50%稼働）
- **総稼働日数**: 56日（土日祝を除く）
- **総工数**: {total_effort}人日（{total_hours}時間）
- **ステークホルダー**: バックオフィス部門、マネージャー層、IT部門

## 目的・目標

### ビジネス目標
- スプレッドシート管理工数を80%削減
- データ更新の自動化によるリアルタイム分析の実現
- 横展開可能なBI基盤の確立
- 意思決定の高速化

### 技術目標
- BigQueryを基盤としたLooker/Looker Studio環境の構築
- LookerML（コードベース管理）の導入と標準化
- 30個以上のスプレッドシート（48シート）からの完全移行
- 既存BigQuery DWHテーブルの活用

### 成功基準
- [ ] スプレッドシート管理工数を80%削減
- [ ] ダッシュボード更新の自動化率100%
- [ ] マネージャー層の満足度80%以上
- [ ] BigQueryクエリコストを月間予算（5-10万円）内に収める
- [ ] データ整合性100%（スプレッドシートとの突合）
- [ ] LookerML開発者を3名以上育成
- [ ] 全成果物の期限内納品

## プロジェクトスコープ

### 含まれるもの（In Scope）
- 既存BigQuery DWHテーブルの確認とマッピング
- Looker/Looker Studioからの既存テーブル接続
- 7つのダッシュボードの構築（高優先度3、中優先度3、低優先度1）
- LookerMLによるコードベース管理の導入
- データ整合性検証スクリプトの作成
- ユーザートレーニングとドキュメント整備

### 含まれないもの（Out of Scope）
- BigQueryテーブル構造の変更・再設計
- ETLパイプラインの構築・変更（既に存在するため）
- 既存システムからBigQueryへのデータ連携の変更
- 新規データソースの追加

## WBS（作業分解構造）

"""

        # Phase 1 WBS
        if phase1_tasks:
            # Phase 1の期間を取得
            phase1_start_dates = [datetime.strptime(t["startDate"], "%Y-%m-%d") for t in phase1_tasks]
            phase1_end_dates = [datetime.strptime(t["endDate"], "%Y-%m-%d") for t in phase1_tasks]
            phase1_start = min(phase1_start_dates).strftime("%-m/%-d")
            phase1_end = max(phase1_end_dates).strftime("%-m/%-d")

            content += f"### Phase 1: 基盤整備と設計 (Week 1-4: {phase1_start}-{phase1_end})\n\n"

            # カテゴリ別にタスクを分類
            phase1_by_category = {}
            for task in phase1_tasks:
                category = task.get("category", "その他")
                if category not in phase1_by_category:
                    phase1_by_category[category] = []
                phase1_by_category[category].append(task)

            # カテゴリごとに出力
            category_titles = {
                "design": "設計・調査",
                "development": "開発",
                "testing": "テスト",
                "documentation": "ドキュメント"
            }

            section_counter = 1
            for category, cat_tasks in phase1_by_category.items():
                cat_title = category_titles.get(category, category.capitalize())
                content += f"#### 1.{section_counter} {cat_title}\n"

                for task in sorted(cat_tasks, key=lambda x: x["id"]):
                    task_id = task["id"]
                    title = task.get("title", "")
                    effort = task.get("effort", 0)
                    effort_hours = task.get("effortHours", 0)
                    weight = task.get("weight", 0)
                    assignee = task.get("assignee", "未定")
                    description = task.get("description", "")
                    dependencies = task.get("dependencies", [])

                    dep_text = ", ".join(dependencies) if dependencies else "なし"

                    content += f"- **{task_id}** {title}\n"
                    content += f"  - 担当: {assignee}\n"
                    content += f"  - 工数: {effort}日（{effort_hours}時間）\n"
                    content += f"  - Weight: {weight}\n"
                    content += f"  - 依存: {dep_text}\n"
                    content += f"  - 説明: {description}\n\n"

                section_counter += 1

            content += f"**Phase 1 合計**: {phase1_effort}日（{phase1_hours}時間）、Weight {phase1_weight}\n\n"

        # Phase 2 WBS
        if phase2_tasks:
            phase2_start_dates = [datetime.strptime(t["startDate"], "%Y-%m-%d") for t in phase2_tasks]
            phase2_end_dates = [datetime.strptime(t["endDate"], "%Y-%m-%d") for t in phase2_tasks]
            phase2_start = min(phase2_start_dates).strftime("%-m/%-d")
            phase2_end = max(phase2_end_dates).strftime("%-m/%-d")

            content += f"### Phase 2: 実装と技術検証 (Week 5-8: {phase2_start}-{phase2_end})\n\n"

            phase2_by_category = {}
            for task in phase2_tasks:
                category = task.get("category", "その他")
                if category not in phase2_by_category:
                    phase2_by_category[category] = []
                phase2_by_category[category].append(task)

            section_counter = 1
            for category, cat_tasks in phase2_by_category.items():
                cat_title = category_titles.get(category, category.capitalize())
                content += f"#### 2.{section_counter} {cat_title}\n"

                for task in sorted(cat_tasks, key=lambda x: x["id"]):
                    task_id = task["id"]
                    title = task.get("title", "")
                    effort = task.get("effort", 0)
                    effort_hours = task.get("effortHours", 0)
                    weight = task.get("weight", 0)
                    assignee = task.get("assignee", "未定")
                    description = task.get("description", "")
                    dependencies = task.get("dependencies", [])

                    dep_text = ", ".join(dependencies) if dependencies else "なし"

                    content += f"- **{task_id}** {title}\n"
                    content += f"  - 担当: {assignee}\n"
                    content += f"  - 工数: {effort}日（{effort_hours}時間）\n"
                    content += f"  - Weight: {weight}\n"
                    content += f"  - 依存: {dep_text}\n"
                    content += f"  - 説明: {description}\n\n"

                section_counter += 1

            content += f"**Phase 2 合計**: {phase2_effort}日（{phase2_hours}時間）、Weight {phase2_weight}\n\n"

        # Phase 3 WBS
        if phase3_tasks:
            phase3_start_dates = [datetime.strptime(t["startDate"], "%Y-%m-%d") for t in phase3_tasks]
            phase3_end_dates = [datetime.strptime(t["endDate"], "%Y-%m-%d") for t in phase3_tasks]
            phase3_start = min(phase3_start_dates).strftime("%-m/%-d")
            phase3_end = max(phase3_end_dates).strftime("%-m/%-d")

            content += f"### Phase 3: フル移行と展開 (Week 9-12: {phase3_start}-{phase3_end})\n\n"

            phase3_by_category = {}
            for task in phase3_tasks:
                category = task.get("category", "その他")
                if category not in phase3_by_category:
                    phase3_by_category[category] = []
                phase3_by_category[category].append(task)

            section_counter = 1
            for category, cat_tasks in phase3_by_category.items():
                cat_title = category_titles.get(category, category.capitalize())
                content += f"#### 3.{section_counter} {cat_title}\n"

                for task in sorted(cat_tasks, key=lambda x: x["id"]):
                    task_id = task["id"]
                    title = task.get("title", "")
                    effort = task.get("effort", 0)
                    effort_hours = task.get("effortHours", 0)
                    weight = task.get("weight", 0)
                    assignee = task.get("assignee", "未定")
                    description = task.get("description", "")
                    dependencies = task.get("dependencies", [])

                    dep_text = ", ".join(dependencies) if dependencies else "なし"

                    content += f"- **{task_id}** {title}\n"
                    content += f"  - 担当: {assignee}\n"
                    content += f"  - 工数: {effort}日（{effort_hours}時間）\n"
                    content += f"  - Weight: {weight}\n"
                    content += f"  - 依存: {dep_text}\n"
                    content += f"  - 説明: {description}\n\n"

                section_counter += 1

            content += f"**Phase 3 合計**: {phase3_effort}日（{phase3_hours}時間）、Weight {phase3_weight}\n\n"

        # タスク一覧テーブル
        content += "## タスク一覧（GitHub Projects用）\n\n"
        content += "| ID | タスク名 | Phase | 工数 | Weight | 依存関係 | カテゴリ |\n"
        content += "|----|---------|-------|------|--------|----------|----------|\n"

        for task in sorted(tasks, key=lambda x: x["id"]):
            task_id = task["id"]
            title = task.get("title", "")
            phase = task.get("phase", "")
            effort = task.get("effort", 0)
            weight = task.get("weight", 0)
            dependencies = task.get("dependencies", [])
            category = task.get("category", "")

            dep_text = ", ".join(dependencies) if dependencies else "-"

            content += f"| {task_id} | {title} | {phase} | {effort}日 | {weight} | {dep_text} | {category} |\n"

        content += f"\n**Weight設定ガイド:**\n"
        content += f"- 総Weight = {total_weight} (プロジェクト全体の進捗を%で管理)\n"
        content += f"- 0.5日タスク = Weight 2, 1日タスク = Weight 3-4, 1.5日タスク = Weight 5, 2.5日タスク = Weight 9\n\n"

        # 依存関係マップ（簡易版）
        content += "## 依存関係マップ\n\n```\n"
        content += f"Phase 1: 基盤整備と設計 (Weight: {phase1_weight})\n"
        for task in phase1_tasks[:5]:  # 最初の5つのみ表示
            task_id = task["id"]
            title = task.get("title", "")
            weight = task.get("weight", 0)
            content += f"├── {task_id}: {title} (W:{weight})\n"

        content += f"\nPhase 2: 実装と技術検証 (Weight: {phase2_weight})\n"
        for task in phase2_tasks[:5]:
            task_id = task["id"]
            title = task.get("title", "")
            weight = task.get("weight", 0)
            content += f"├── {task_id}: {title} (W:{weight})\n"

        content += f"\nPhase 3: フル移行と展開 (Weight: {phase3_weight})\n"
        for task in phase3_tasks[:5]:
            task_id = task["id"]
            title = task.get("title", "")
            weight = task.get("weight", 0)
            content += f"├── {task_id}: {title} (W:{weight})\n"

        content += "```\n\n"

        # 工数サマリー
        content += "## 工数サマリー\n\n"
        content += "### Phase別工数\n\n"
        content += "| Phase | 期間 | タスク数 | 総工数 | Total Weight |\n"
        content += "|-------|------|----------|--------|--------------||\n"
        content += f"| Phase 1 | Week 1-4 ({phase1_start}-{phase1_end}) | {len(phase1_tasks)}個 | {phase1_effort}日 ({phase1_hours}時間) | {phase1_weight}% |\n"
        content += f"| Phase 2 | Week 5-8 ({phase2_start}-{phase2_end}) | {len(phase2_tasks)}個 | {phase2_effort}日 ({phase2_hours}時間) | {phase2_weight}% |\n"
        content += f"| Phase 3 | Week 9-12 ({phase3_start}-{phase3_end}) | {len(phase3_tasks)}個 | {phase3_effort}日 ({phase3_hours}時間) | {phase3_weight}% |\n"
        content += f"| **合計** | **{total_weeks}週間** | **{len(tasks)}個** | **{total_effort}日 ({total_hours}時間)** | **{total_weight}%** |\n\n"

        content += "### メンバー別工数\n\n"
        content += "| メンバー | 担当タスク数 | 総工数 | 備考 |\n"
        content += "|---------|-------------|--------|------|\n"
        content += f"| BI Engineer | {len(tasks)}個 | {total_effort}日 ({total_hours}時間) | 50%稼働（1日3.5時間） |\n\n"

        content += "### 稼働日数計算\n\n"
        content += f"- **プロジェクト期間**: {project_start}〜{project_end}（{total_days}日間）\n"
        content += "- **休業日**: 土日、1/12(成人の日)、2/11(建国記念の日)、2/23(天皇誕生日)、3/20(春分の日)\n"
        content += "- **稼働日数**: 約56日\n"
        content += "- **50%稼働**: 28人日 = 196時間\n"
        content += f"- **計画工数**: {total_effort}人日 = {total_hours}時間\n"

        buffer_rate = ((28 - total_effort) / 28 * 100) if total_effort > 0 else 0
        content += f"- **余裕率**: {buffer_rate:.1f}%\n\n"

        # 残りの固定セクション
        content += """## リスク管理

| ID | リスク | 影響度 | 発生確率 | 対策 | 責任者 |
|----|--------|--------|----------|------|--------|
| RISK-001 | LookerML習熟度不足による開発遅延 | 高 | 中 | ・Phase 2でトライアル期間を設定<br>・外部トレーニングの活用<br>・シンプルな実装から開始 | PM |
| RISK-002 | データ品質問題によるダッシュボード信頼性低下 | 高 | 中 | ・Phase 1での徹底的なデータ検証<br>・データ品質チェックの自動化<br>・問題データのクレンジングルール策定 | BI Engineer |
| RISK-003 | ユーザー要件変更によるスコープクリープ | 中 | 高 | ・優先度による段階的実装<br>・変更管理プロセスの明確化<br>・Phase 3での調整バッファ確保 | PM |
| RISK-004 | BigQueryコスト超過 | 中 | 低 | ・クエリ最適化<br>・コストモニタリングの自動化<br>・予算アラート設定 | BI Engineer |
| RISK-005 | 50%稼働による遅延リスク | 高 | 中 | ・優先度の明確化<br>・クリティカルパスの管理<br>・早期のリスク検知とエスカレーション | PM |

## マイルストーン

"""

        # マイルストーンを動的生成
        weekly_schedule = self.schedule_data.get("weeklySchedule", [])
        if len(weekly_schedule) >= 4:
            week4_end = weekly_schedule[3]["dateRange"].split("〜")[-1].strip()
            content += f"- **Week 4 ({week4_end})**: Phase 1完了 - 基盤整備・設計完了、LookerML設計方針確定\n"
        if len(weekly_schedule) >= 8:
            week8_end = weekly_schedule[7]["dateRange"].split("〜")[-1].strip()
            content += f"- **Week 8 ({week8_end})**: Phase 2完了 - Looker Studio高優先度ダッシュボード3種完成、LookerML基本構造実装完了\n"
        if len(weekly_schedule) >= 12:
            week12_end = weekly_schedule[11]["dateRange"].split("〜")[-1].strip()
            content += f"- **Week 12 ({week12_end})**: Phase 3完了 - 全ダッシュボード完成、本番リリース\n"

        content += """
## 成果物

### Phase 1
- [ ] 既存BigQuery DWHテーブルのドキュメント（テーブル一覧、スキーマ定義）
- [ ] スプレッドシート→BigQueryマッピング表
- [ ] データ品質チェックスクリプト
- [ ] ダッシュボードワイヤーフレーム（高優先度3種）
- [ ] KPI定義書
- [ ] LookerML設計書

### Phase 2
- [ ] Looker Studioダッシュボード（優先度：高）×3
  - 経営ダッシュボード
  - 稼働状況ダッシュボード
  - 財務ダッシュボード
- [ ] Looker Models（advisor_operations, financial_analysis）
- [ ] Looker Views（base, facts, aggregates）
- [ ] Looker Explores（advisor_activity, contract_management等）
- [ ] GitHubリポジトリ（LookerMLコードベース）
- [ ] LookerML開発ガイドライン
- [ ] トレーニング資料

### Phase 3
- [ ] Lookerダッシュボード（優先度：中）×3
  - 顧問パフォーマンスダッシュボード
  - 解約分析ダッシュボード
  - 営業（SS）分析ダッシュボード
- [ ] Lookerダッシュボード（優先度：低）×1
  - 詳細分析ダッシュボード
- [ ] システムアーキテクチャ設計書
- [ ] ダッシュボード利用マニュアル
- [ ] 運用手順書
- [ ] トラブルシューティングガイド

## コミュニケーション計画

### 定例会議
- **週次進捗会議**: 毎週月曜日 10:00-10:30
- **フェーズレビュー**: 各Phase終了時（Week 4, Week 8, Week 12）

### レポート
- **週次レポート**: 毎週金曜日に進捗報告
- **月次レポート**: 月末に全体まとめ

### コミュニケーションチャネル
- **Slack**: #project-dashboard-migration
- **GitHub Projects**: 進捗トラッキング
- **Email**: プロジェクト関係者メーリングリスト

## 品質基準

### ダッシュボード品質
- [ ] データ整合性100%（スプレッドシートとの突合）
- [ ] ダッシュボード目視検証完了
- [ ] LookML構文チェック（LookML Validator）
- [ ] ユーザーレビュー実施

### ドキュメント
- [ ] システムアーキテクチャ設計書作成
- [ ] ダッシュボード利用マニュアル作成
- [ ] LookerML開発ガイドライン作成
- [ ] 運用手順書作成

### セキュリティ
- [ ] BigQuery IAMアクセス制御設定
- [ ] 列レベルセキュリティ設定（顧問名、企業名）
- [ ] 監査ログ有効化

## 承認

| 役割 | 氏名 | 承認日 | 署名 |
|------|------|--------|------|
| プロジェクトマネージャー | [未定] | - | _______ |
| バックオフィス責任者 | [未定] | - | _______ |
| IT部門責任者 | [未定] | - | _______ |

---

**作成日**: 2026-01-15
**最終更新**: """ + datetime.now().strftime("%Y-%m-%d") + f"""
**バージョン**: 1.0（自動生成）
**SPEC.md参照**: Version 2.0 (2026-01-15)
"""

        # ファイルに書き込み
        plan_md_file = self.base_dir / "PLAN.md"
        with open(plan_md_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  ✓ PLAN.md再生成完了")

    def regenerate_schedule_md(self):
        """SCHEDULE.mdを再生成"""
        print("\n📝 SCHEDULE.mdを再生成中...")

        # 基本情報
        project_name = self.tasks_data.get("project", {}).get("name", "プロジェクト")
        total_tasks = len(self.schedule_data.get("tasks", []))
        total_weeks = len(self.schedule_data.get("weeklySchedule", []))

        # 開始日・終了日
        tasks = self.schedule_data.get("tasks", [])
        if tasks:
            start_dates = [datetime.strptime(t["startDate"], "%Y-%m-%d") for t in tasks]
            end_dates = [datetime.strptime(t["endDate"], "%Y-%m-%d") for t in tasks]
            project_start = min(start_dates).strftime("%Y-%m-%d")
            project_end = max(end_dates).strftime("%Y-%m-%d")
        else:
            project_start = "未定"
            project_end = "未定"

        # SCHEDULE.md生成
        content = f"""# {project_name} - スケジュール

## 📅 プロジェクト期間

- **開始日**: {project_start}
- **終了日**: {project_end}
- **総タスク数**: {total_tasks}個
- **スケジュール期間**: {total_weeks}週間

## 📊 週次スケジュール

"""

        # 週次スケジュールを追加
        for week_info in self.schedule_data.get("weeklySchedule", []):
            week = week_info["week"]
            date_range = week_info["dateRange"]
            cumulative_progress = week_info["cumulativeProgress"]
            tasks_in_week = week_info["tasks"]

            content += f"### {week} ({date_range})\n\n"
            content += f"- **累積進捗率**: {cumulative_progress}%\n"
            content += f"- **タスク数**: {len(tasks_in_week)}個\n\n"

            if tasks_in_week:
                content += "**タスク一覧**:\n\n"
                for task_id in tasks_in_week:
                    task = self.find_task_in_schedule(task_id)
                    if task:
                        title = task.get("title", "")
                        priority = task.get("priority", "medium")
                        category = task.get("category", "")
                        effort = task.get("effort", 0)

                        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")

                        content += f"- {priority_emoji} **{task_id}**: {title}\n"
                        content += f"  - カテゴリ: {category}, 工数: {effort}日\n"
                        content += f"  - 期間: {task['startDate']} 〜 {task['endDate']}\n"

            content += "\n"

        # タスク詳細
        content += "## 📋 全タスク詳細\n\n"

        for task in self.schedule_data.get("tasks", []):
            task_id = task["id"]
            title = task.get("title", "")
            description = task.get("description", "")
            phase = task.get("phase", "")
            priority = task.get("priority", "medium")
            category = task.get("category", "")
            effort = task.get("effort", 0)
            weight = task.get("weight", 0)
            start_date = task.get("startDate", "")
            end_date = task.get("endDate", "")
            dependencies = task.get("dependencies", [])

            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")

            content += f"### {priority_emoji} {task_id}: {title}\n\n"
            content += f"**概要**: {description}\n\n"
            content += f"- **Phase**: {phase}\n"
            content += f"- **カテゴリ**: {category}\n"
            content += f"- **優先度**: {priority}\n"
            content += f"- **工数**: {effort}日\n"
            content += f"- **重み**: {weight}%\n"
            content += f"- **期間**: {start_date} 〜 {end_date}\n"

            if dependencies:
                content += f"- **依存タスク**: {', '.join(dependencies)}\n"

            content += "\n"

        # ファイルに書き込み
        with open(self.schedule_md_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  ✓ SCHEDULE.md再生成完了")

    def update_github_issue(self, task_id: str):
        """GitHub Issueを更新"""
        print(f"\n🔄 GitHub Issue更新中: {task_id}...")

        # Issue番号を取得
        if task_id not in self.issue_mapping:
            print(f"  ⚠️  {task_id}のIssue番号が見つかりません。スキップします。")
            return

        issue_number = self.issue_mapping[task_id]
        schedule_task = self.find_task_in_schedule(task_id)

        if not schedule_task:
            print(f"  ⚠️  {task_id}がschedule.jsonに見つかりません。スキップします。")
            return

        # マイルストーンを更新（週番号から）
        week_number = schedule_task.get("weekNumber", "")
        if week_number:
            # "Week 2-3" → "Week 2" のように最初の週を抽出
            import re
            match = re.search(r"Week (\d+)", week_number)
            if match:
                milestone_name = f"Week {match.group(1)}"
                try:
                    self.run_gh_command([
                        "issue", "edit", issue_number,
                        "--repo", REPO_FULL_NAME,
                        "--milestone", milestone_name
                    ])
                    print(f"  ✓ Milestone更新: {milestone_name}")
                except Exception as e:
                    print(f"  ⚠️  Milestone更新失敗: {e}")

        print(f"  ✓ Issue #{issue_number} 更新完了")

    def update_github_projects_dates(self, task_id: str):
        """GitHub Projects V2の日付フィールドを更新"""
        print(f"\n📊 Projects V2 日付更新中: {task_id}...")

        # Issue番号を取得
        if task_id not in self.issue_mapping:
            print(f"  ⚠️  {task_id}のIssue番号が見つかりません。スキップします。")
            return

        issue_number = self.issue_mapping[task_id]
        schedule_task = self.find_task_in_schedule(task_id)

        if not schedule_task:
            print(f"  ⚠️  {task_id}がschedule.jsonに見つかりません。スキップします。")
            return

        start_date = schedule_task.get("startDate")
        end_date = schedule_task.get("endDate")

        # プロジェクト情報を取得
        query = f"""
        {{
          user(login: "{REPO_OWNER}") {{
            projectV2(number: {PROJECT_NUMBER}) {{
              id
              fields(first: 20) {{
                nodes {{
                  ... on ProjectV2Field {{
                    id
                    name
                  }}
                }}
              }}
              items(first: 100) {{
                nodes {{
                  id
                  content {{
                    ... on Issue {{
                      number
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """

        try:
            result = self.run_gh_api(query)
            project_info = result["data"]["user"]["projectV2"]
            project_id = project_info["id"]

            # フィールドIDを取得
            fields = {field["name"]: field["id"] for field in project_info["fields"]["nodes"]}
            start_date_field_id = fields.get("Start Date")
            end_date_field_id = fields.get("End Date")

            if not start_date_field_id or not end_date_field_id:
                print("  ⚠️  'Start Date' または 'End Date' フィールドが見つかりません")
                return

            # Issue番号からItem IDを取得
            issue_to_item = {}
            for item in project_info["items"]["nodes"]:
                if item["content"]:
                    item_issue_number = str(item["content"]["number"])
                    issue_to_item[item_issue_number] = item["id"]

            if issue_number not in issue_to_item:
                print(f"  ⚠️  Issue #{issue_number} がProjectsに追加されていません")
                return

            item_id = issue_to_item[issue_number]

            # Start Dateを更新
            self._update_project_field(project_id, item_id, start_date_field_id, start_date)
            print(f"  ✓ Start Date更新: {start_date}")

            # End Dateを更新
            self._update_project_field(project_id, item_id, end_date_field_id, end_date)
            print(f"  ✓ End Date更新: {end_date}")

        except Exception as e:
            print(f"  ⚠️  Projects更新失敗: {e}")

    def _update_project_field(self, project_id: str, item_id: str, field_id: str, value: str):
        """Project ItemのフィールドValueを更新"""
        mutation = f"""
        mutation {{
          updateProjectV2ItemFieldValue(
            input: {{
              projectId: "{project_id}"
              itemId: "{item_id}"
              fieldId: "{field_id}"
              value: {{
                date: "{value}"
              }}
            }}
          ) {{
            projectV2Item {{
              id
            }}
          }}
        }}
        """
        self.run_gh_api(mutation)

    def delete_github_issue(self, task_id: str):
        """GitHub Issueをクローズ（削除の代わり）"""
        print(f"\n🗑️  GitHub Issue クローズ中: {task_id}...")

        # Issue番号を取得
        if task_id not in self.issue_mapping:
            print(f"  ⚠️  {task_id}のIssue番号が見つかりません。スキップします。")
            return

        issue_number = self.issue_mapping[task_id]

        try:
            self.run_gh_command([
                "issue", "close", issue_number,
                "--repo", REPO_FULL_NAME,
                "--comment", f"タスク{task_id}が削除されたため、このIssueをクローズします。"
            ])
            print(f"  ✓ Issue #{issue_number} クローズ完了")

            # マッピングから削除
            del self.issue_mapping[task_id]

        except Exception as e:
            print(f"  ⚠️  Issue クローズ失敗: {e}")

    def sync_to_github(self, task_ids: Optional[List[str]] = None):
        """GitHubに変更を同期"""
        print("\n" + "=" * 70)
        print("🔄 GitHubに変更を同期中...")
        print("=" * 70)

        if task_ids is None:
            # 全タスクを同期
            task_ids = [task["id"] for task in self.schedule_data.get("tasks", [])]

        for task_id in task_ids:
            if task_id in self.issue_mapping:
                self.update_github_issue(task_id)
                self.update_github_projects_dates(task_id)

        print("\n✅ GitHub同期完了")

    def save_all_changes(self):
        """全ての変更をファイルに保存"""
        print("\n💾 変更をファイルに保存中...")

        # tasks.jsonを保存
        self._save_json(self.tasks_file, self.tasks_data)
        print("  ✓ tasks.json保存完了")

        # schedule.jsonを保存
        self._save_json(self.schedule_file, self.schedule_data)
        print("  ✓ schedule.json保存完了")

        # github-issue-mapping.jsonを保存
        self._save_json(self.mapping_file, self.issue_mapping)
        print("  ✓ github-issue-mapping.json保存完了")

        print("\n✅ 全ファイル保存完了")

    def show_summary(self):
        """変更サマリーを表示"""
        print("\n" + "=" * 70)
        print("📋 変更サマリー")
        print("=" * 70)

        if self.changes:
            for change in self.changes:
                print(f"  ✓ {change}")
        else:
            print("  変更はありません")

        if self.errors:
            print("\n⚠️  エラー:")
            for error in self.errors:
                print(f"  ✗ {error}")


def interactive_mode(manager: ScheduleUpdateManager):
    """インタラクティブモード"""
    print("\n" + "=" * 70)
    print("📋 スケジュール更新 - インタラクティブモード")
    print("=" * 70)

    print("\n実行する操作を選択してください:")
    print("  1. タスクの期限を延長")
    print("  2. タスクの開始日を変更")
    print("  3. タスクを削除")
    print("  4. タスクの優先度を変更")
    print("  5. 終了")

    choice = input("\n選択 (1-5): ").strip()

    if choice == "1":
        task_id = input("タスクID (例: TASK-007): ").strip()
        days = int(input("延長する日数: ").strip())

        backup_dir = manager._backup_files()
        try:
            manager.extend_deadline(task_id, days)
            manager.recalculate_weekly_schedule()
            manager.regenerate_plan_md()
            manager.regenerate_schedule_md()
            manager.save_all_changes()
            manager.sync_to_github([task_id])
            manager.show_summary()
        except Exception as e:
            print(f"\nERROR: {e}")
            manager._restore_from_backup(backup_dir)
            sys.exit(1)

    elif choice == "2":
        task_id = input("タスクID (例: TASK-015): ").strip()
        new_date = input("新しい開始日 (YYYY-MM-DD): ").strip()

        backup_dir = manager._backup_files()
        try:
            manager.change_start_date(task_id, new_date)
            manager.recalculate_weekly_schedule()
            manager.regenerate_plan_md()
            manager.regenerate_schedule_md()
            manager.save_all_changes()
            manager.sync_to_github([task_id])
            manager.show_summary()
        except Exception as e:
            print(f"\nERROR: {e}")
            manager._restore_from_backup(backup_dir)
            sys.exit(1)

    elif choice == "3":
        task_id = input("削除するタスクID (例: TASK-010): ").strip()
        confirm = input(f"本当に{task_id}を削除しますか？ (yes/no): ").strip().lower()

        if confirm == "yes":
            backup_dir = manager._backup_files()
            try:
                manager.delete_task(task_id)
                manager.delete_github_issue(task_id)
                manager.recalculate_weekly_schedule()
                manager.regenerate_plan_md()
                manager.regenerate_schedule_md()
                manager.save_all_changes()
                manager.show_summary()
            except Exception as e:
                print(f"\nERROR: {e}")
                manager._restore_from_backup(backup_dir)
                sys.exit(1)
        else:
            print("キャンセルしました。")

    elif choice == "4":
        task_id = input("タスクID (例: TASK-005): ").strip()
        new_priority = input("新しい優先度 (high/medium/low): ").strip()

        backup_dir = manager._backup_files()
        try:
            manager.change_priority(task_id, new_priority)
            manager.save_all_changes()
            # 優先度変更はGitHub Issueのラベルを更新する必要がある
            # （簡易版では省略）
            manager.show_summary()
        except Exception as e:
            print(f"\nERROR: {e}")
            manager._restore_from_backup(backup_dir)
            sys.exit(1)

    elif choice == "5":
        print("終了します。")
        sys.exit(0)

    else:
        print("無効な選択です。")
        sys.exit(1)


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description="スケジュール更新オーケストレーションスクリプト",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # タスクの期限を7日延長
  python3 scripts/update-schedule.py --task TASK-007 --extend-deadline 7

  # タスクの開始日を変更
  python3 scripts/update-schedule.py --task TASK-015 --start-date 2026-02-10

  # タスクを削除
  python3 scripts/update-schedule.py --task TASK-010 --action delete

  # タスクの優先度を変更
  python3 scripts/update-schedule.py --task TASK-005 --priority high

  # インタラクティブモード
  python3 scripts/update-schedule.py --interactive
        """
    )

    parser.add_argument("--task", type=str, help="対象タスクID (例: TASK-007)")
    parser.add_argument("--extend-deadline", type=int, help="期限を延長する日数")
    parser.add_argument("--start-date", type=str, help="新しい開始日 (YYYY-MM-DD)")
    parser.add_argument("--action", type=str, choices=["delete"], help="実行するアクション")
    parser.add_argument("--priority", type=str, choices=["high", "medium", "low"], help="新しい優先度")
    parser.add_argument("--interactive", action="store_true", help="インタラクティブモード")
    parser.add_argument("--no-github-sync", action="store_true", help="GitHub同期をスキップ")

    args = parser.parse_args()

    # プロジェクトディレクトリ
    base_dir = Path(__file__).parent.parent

    # マネージャー初期化
    manager = ScheduleUpdateManager(base_dir)

    # インタラクティブモード
    if args.interactive:
        interactive_mode(manager)
        return

    # タスクIDが指定されていない場合はエラー
    if not args.task and not args.interactive:
        parser.print_help()
        sys.exit(1)

    # バックアップ作成
    backup_dir = manager._backup_files()

    try:
        # 操作実行
        if args.extend_deadline:
            manager.extend_deadline(args.task, args.extend_deadline)
        elif args.start_date:
            manager.change_start_date(args.task, args.start_date)
        elif args.action == "delete":
            confirm = input(f"本当に{args.task}を削除しますか？ (yes/no): ").strip().lower()
            if confirm != "yes":
                print("キャンセルしました。")
                sys.exit(0)
            manager.delete_task(args.task)
            if not args.no_github_sync:
                manager.delete_github_issue(args.task)
        elif args.priority:
            manager.change_priority(args.task, args.priority)
        else:
            print("ERROR: 実行する操作を指定してください（--extend-deadline, --start-date, --action, --priority）")
            sys.exit(1)

        # 週次スケジュール再計算
        manager.recalculate_weekly_schedule()

        # PLAN.md再生成
        manager.regenerate_plan_md()

        # SCHEDULE.md再生成
        manager.regenerate_schedule_md()

        # ファイル保存
        manager.save_all_changes()

        # GitHub同期
        if not args.no_github_sync and args.action != "delete":
            manager.sync_to_github([args.task])

        # サマリー表示
        manager.show_summary()

        print("\n" + "=" * 70)
        print("✅ スケジュール更新完了")
        print("=" * 70)

    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        manager._restore_from_backup(backup_dir)
        sys.exit(1)


if __name__ == "__main__":
    main()
