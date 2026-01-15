#!/usr/bin/env python3
"""
失敗したIssuesを作成するスクリプト

使用方法:
    python3 scripts/create-missing-issues.py
"""

import json
import re
import subprocess
import sys
from pathlib import Path


def run_gh_command(command):
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
        print(f"ERROR: {e.stderr}")
        raise


def main():
    # プロジェクトディレクトリ
    base_dir = Path(__file__).parent.parent

    # データ読み込み
    with open(base_dir / "schedule.json", "r", encoding="utf-8") as f:
        schedule_data = json.load(f)

    tasks = schedule_data["tasks"]
    critical_path = schedule_data.get("criticalPath", [])

    # リポジトリ情報
    repo_full_name = "sh-usami-rg/dashboard-migration-project"

    # 失敗したタスクIDリスト（手動で指定）
    failed_task_ids = ["TASK-006", "TASK-007", "TASK-008", "TASK-011", "TASK-018"]

    print(f"🔄 失敗したIssues作成中（{len(failed_task_ids)}個）...\n")

    # TASK-ID → タスク情報のマッピング
    task_map = {task["id"]: task for task in tasks}

    created_count = 0

    for task_id in failed_task_ids:
        if task_id not in task_map:
            print(f"  ⚠️  {task_id} が見つかりません。スキップします。")
            continue

        task = task_map[task_id]
        title = f"[{task_id}] {task['title']}"

        # ラベル生成
        labels = []

        # Phase ラベル
        phase = task.get("phase", "")
        if "Phase 1" in phase:
            labels.append("phase-1")
        elif "Phase 2" in phase:
            labels.append("phase-2")
        elif "Phase 3" in phase:
            labels.append("phase-3")

        # Priority ラベル
        priority = task.get("priority", "")
        if priority == "high":
            labels.append("priority-high")
        elif priority == "medium":
            labels.append("priority-medium")
        elif priority == "low":
            labels.append("priority-low")

        # Category ラベル
        category = task.get("category", "")
        if category in ["design", "development", "testing", "documentation"]:
            labels.append(category)

        # Critical Path
        if task_id in critical_path:
            labels.append("critical-path")

        # 依存関係を解決
        dependencies = task.get("dependencies", [])
        if dependencies:
            dep_text = ", ".join(dependencies)
        else:
            dep_text = "このタスクには依存タスクはありません。"

        # Issue本文
        body = f"""## 📋 タスク概要

{task['description']}

## 📊 タスク情報

- **Phase**: {task['phase']}
- **Priority**: {task['priority'].capitalize()}
- **Category**: {task['category'].capitalize()}
- **Assignee**: {task['assignee']}
- **Effort**: {task['effort']}日（{task['effortHours']}時間）
- **Weight**: {task['weight']}（進捗率への貢献: {task['weight']}%）

## 📅 スケジュール

- **開始日**: {task['startDate']}
- **終了日**: {task['endDate']}
- **Week**: {task['weekNumber']}

## 🔗 依存関係

{dep_text}

## ✅ 完了条件

- [ ] {task['title']}の完了
"""

        # マイルストーン名を取得（Week 2-3 → Week 2）
        week_number = task.get("weekNumber", "")
        if week_number and "Week" in week_number:
            match = re.search(r"Week (\d+)", week_number)
            if match:
                week_number = f"Week {match.group(1)}"
            else:
                week_number = ""

        # Issue作成コマンド
        command = [
            "issue", "create",
            "--repo", repo_full_name,
            "--title", title,
            "--body", body,
            "--label", ",".join(labels)
        ]

        # マイルストーンがある場合は追加
        if week_number:
            command.extend(["--milestone", week_number])

        # Issue作成
        try:
            issue_url = run_gh_command(command)
            issue_number = issue_url.split("/")[-1]
            print(f"  ✅ {task_id} → #{issue_number}")
            created_count += 1
        except Exception as e:
            print(f"  ❌ {task_id} - エラー: {e}")

    print(f"\n✅ 完了: {created_count}/{len(failed_task_ids)}個のIssueを作成しました")
    print(f"\n📦 Issues一覧: https://github.com/{repo_full_name}/issues")


if __name__ == "__main__":
    main()
