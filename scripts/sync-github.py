#!/usr/bin/env python3
"""
GitHub Issues & Projects同期スクリプト

tasks.json と schedule.json のデータを GitHub Issues・Milestones・Projects V2 に同期します。

前提条件:
    - GitHub CLI (gh) がインストールされていること
    - gh auth login で認証済みであること

使用方法:
    python scripts/sync-github.py

環境変数（オプション）:
    GITHUB_REPO_NAME: リポジトリ名（指定しない場合は対話的に入力）
    GITHUB_REPO_VISIBILITY: public または private（デフォルト: private）
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class GitHubSyncManager:
    """GitHub同期マネージャークラス"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.tasks_file = base_dir / "tasks.json"
        self.schedule_file = base_dir / "schedule.json"

        # JSONファイルを読み込む
        self.tasks_data = self._load_json(self.tasks_file)
        self.schedule_data = self._load_json(self.schedule_file)

        # プロジェクト情報
        self.project_info = self.tasks_data["project"]
        self.tasks = self.schedule_data["tasks"]  # schedule.jsonのタスク（日付情報付き）
        self.weekly_schedule = self.schedule_data["weeklySchedule"]
        self.critical_path = self.schedule_data.get("criticalPath", [])

        # GitHub情報
        self.repo_owner = None
        self.repo_name = None
        self.repo_full_name = None
        self.project_id = None
        self.issue_numbers = {}  # TASK-ID -> Issue番号のマッピング

        # ラベル定義
        self.labels = [
            # Phase ラベル
            {"name": "phase-1", "color": "0E8A16", "description": "Phase 1: 基盤整備と設計"},
            {"name": "phase-2", "color": "1D76DB", "description": "Phase 2: 実装と技術検証"},
            {"name": "phase-3", "color": "5319E7", "description": "Phase 3: フル移行と展開"},
            # Priority ラベル
            {"name": "priority-high", "color": "D73A4A", "description": "優先度: 高"},
            {"name": "priority-medium", "color": "FBCA04", "description": "優先度: 中"},
            {"name": "priority-low", "color": "0075CA", "description": "優先度: 低"},
            # Category ラベル
            {"name": "design", "color": "D4C5F9", "description": "カテゴリ: 設計"},
            {"name": "development", "color": "C2E0C6", "description": "カテゴリ: 開発"},
            {"name": "testing", "color": "FEF2C0", "description": "カテゴリ: テスト"},
            {"name": "documentation", "color": "BFD4F2", "description": "カテゴリ: ドキュメント"},
            # その他
            {"name": "critical-path", "color": "B60205", "description": "クリティカルパス上のタスク"},
            {"name": "blocked", "color": "E99695", "description": "ブロックされているタスク"},
        ]

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

    def run_gh_command(self, command: List[str], capture_output: bool = True) -> str:
        """GitHub CLIコマンドを実行"""
        try:
            result = subprocess.run(
                ["gh"] + command,
                capture_output=capture_output,
                text=True,
                check=True
            )
            if capture_output:
                return result.stdout.strip()
            return ""
        except FileNotFoundError:
            print("ERROR: GitHub CLI (gh) が見つかりません。")
            print("インストール手順: https://cli.github.com/")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"ERROR: GitHub CLIコマンド実行エラー: {' '.join(command)}")
            if e.stderr:
                print(f"詳細: {e.stderr}")
            raise

    def check_gh_auth(self):
        """GitHub CLI認証状態を確認"""
        try:
            result = self.run_gh_command(["auth", "status"])
            print("✅ GitHub CLI認証確認完了")
            return True
        except subprocess.CalledProcessError:
            print("ERROR: GitHub CLIの認証が必要です。")
            print("以下のコマンドを実行してください:")
            print("  gh auth login")
            sys.exit(1)

    def create_repository(self, repo_name: str, visibility: str = "private"):
        """GitHubリポジトリを作成"""
        print(f"\n📦 リポジトリ作成中: {repo_name} ({visibility})")

        description = self.project_info["description"]

        # リポジトリ作成
        command = [
            "repo", "create", repo_name,
            f"--{visibility}",
            "--description", description,
            "--confirm"
        ]

        try:
            self.run_gh_command(command, capture_output=False)
        except subprocess.CalledProcessError:
            print(f"⚠️  リポジトリ {repo_name} は既に存在する可能性があります。")
            # 既存リポジトリの情報を取得
            pass

        # リポジトリ情報を取得
        repo_info = self.run_gh_command(["repo", "view", repo_name, "--json", "owner,name"])
        repo_data = json.loads(repo_info)
        self.repo_owner = repo_data["owner"]["login"]
        self.repo_name = repo_data["name"]
        self.repo_full_name = f"{self.repo_owner}/{self.repo_name}"

        print(f"✅ リポジトリ作成完了: {self.repo_full_name}")

    def create_labels(self):
        """ラベルを作成"""
        print(f"\n🏷️  ラベル作成中（{len(self.labels)}個）...")

        for label in self.labels:
            try:
                self.run_gh_command([
                    "label", "create",
                    label["name"],
                    "--color", label["color"],
                    "--description", label["description"],
                    "--repo", self.repo_full_name
                ])
                print(f"  ✓ {label['name']}")
            except subprocess.CalledProcessError:
                # 既に存在する場合はスキップ
                print(f"  - {label['name']} (既存)")

        print("✅ ラベル作成完了")

    def create_milestones(self):
        """週次マイルストーン（Week 1-12）を作成"""
        print(f"\n🎯 マイルストーン作成中（{len(self.weekly_schedule)}個）...")

        for week_info in self.weekly_schedule:
            week = week_info["week"]
            date_range = week_info["dateRange"]
            cumulative_progress = week_info["cumulativeProgress"]
            tasks_in_week = week_info["tasks"]

            # 終了日を取得（dateRange から抽出: "2026-01-06 〜 2026-01-10"）
            end_date_str = date_range.split("〜")[-1].strip()
            due_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            due_date_iso = due_date.strftime("%Y-%m-%dT23:59:59Z")

            # マイルストーン説明
            description = f"""期間: {date_range}
予定進捗率: {cumulative_progress}%
タスク: {", ".join(tasks_in_week)}"""

            # マイルストーン作成（GitHub REST APIを使用）
            command = [
                "api", f"repos/{self.repo_full_name}/milestones",
                "-X", "POST",
                "-f", f"title={week}",
                "-f", f"due_on={due_date_iso}",
                "-f", f"description={description}"
            ]

            try:
                self.run_gh_command(command)
                print(f"  ✓ {week}")
            except subprocess.CalledProcessError:
                # 既に存在する場合はスキップ
                print(f"  - {week} (既存)")

        print("✅ マイルストーン作成完了")

    def create_issues(self):
        """全タスクをIssueとして作成"""
        print(f"\n📝 Issue作成中（{len(self.tasks)}個）...")

        # TASK-ID → タスク情報のマッピング
        task_map = {task["id"]: task for task in self.tasks}

        for task in self.tasks:
            task_id = task["id"]
            title = f"[{task_id}] {task['title']}"

            # Issue本文を生成
            body = self._generate_issue_body(task, task_map)

            # ラベルを生成
            labels = self._generate_issue_labels(task)

            # マイルストーン名を取得（例: "Week 1"）
            week_number = task.get("weekNumber", "")
            if week_number and "Week" in week_number:
                # "Week 2-3" のような場合は最初の週を使用
                match = re.search(r"Week (\d+)", week_number)
                if match:
                    week_number = f"Week {match.group(1)}"
                else:
                    week_number = ""

            # Issue作成
            command = [
                "issue", "create",
                "--repo", self.repo_full_name,
                "--title", title,
                "--body", body,
                "--label", ",".join(labels)
            ]

            # マイルストーンがある場合は追加
            if week_number:
                command.extend(["--milestone", week_number])

            try:
                issue_url = self.run_gh_command(command)
                # Issue番号を抽出
                issue_number = issue_url.split("/")[-1]
                self.issue_numbers[task_id] = issue_number
                print(f"  ✓ {task_id} → #{issue_number}")
            except subprocess.CalledProcessError as e:
                print(f"  ✗ {task_id} - エラー: {e}")

        print("✅ Issue作成完了")

        # Issue番号マッピングを保存
        self._save_issue_mapping()

    def _generate_issue_body(self, task: Dict, task_map: Dict) -> str:
        """Issue本文を生成"""
        # 依存関係を解決
        dependencies = task.get("dependencies", [])
        if dependencies:
            dep_links = []
            for dep_id in dependencies:
                if dep_id in self.issue_numbers:
                    issue_num = self.issue_numbers[dep_id]
                    dep_links.append(f"#{issue_num} ({dep_id})")
                else:
                    dep_links.append(dep_id)
            dep_text = ", ".join(dep_links)
        else:
            dep_text = "このタスクには依存タスクはありません。"

        # 完了条件のチェックリストを生成（簡易版）
        checklist = f"- [ ] {task['title']}の完了"

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

{checklist}
"""

        return body

    def _generate_issue_labels(self, task: Dict) -> List[str]:
        """Issueのラベルを生成"""
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
        if task["id"] in self.critical_path:
            labels.append("critical-path")

        return labels

    def _save_issue_mapping(self):
        """TASK-ID → Issue番号のマッピングを保存"""
        mapping_file = self.base_dir / "github-issue-mapping.json"
        with open(mapping_file, "w", encoding="utf-8") as f:
            json.dump(self.issue_numbers, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Issue番号マッピング保存: {mapping_file}")

    def create_project(self, project_name: str):
        """Projects V2を作成"""
        print(f"\n📊 GitHub Projects作成中: {project_name}")

        # Projects V2作成（GraphQL使用）
        command = [
            "project", "create",
            "--owner", self.repo_owner,
            "--title", project_name
        ]

        try:
            project_url = self.run_gh_command(command)
            # Project IDを抽出（URLから）
            # 例: https://github.com/users/{owner}/projects/123
            match = re.search(r"/projects/(\d+)", project_url)
            if match:
                self.project_id = match.group(1)
                print(f"✅ Projects作成完了: {project_url}")
                print(f"   Project ID: {self.project_id}")
            else:
                print(f"⚠️  Project IDを抽出できませんでした: {project_url}")
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Projects作成エラー: {e}")
            sys.exit(1)

    def add_issues_to_project(self):
        """全IssueをProjectsに追加"""
        if not self.project_id:
            print("⚠️  Project IDが設定されていません。スキップします。")
            return

        print(f"\n🔗 IssuesをProjectsに追加中...")

        for task_id, issue_number in self.issue_numbers.items():
            issue_url = f"https://github.com/{self.repo_full_name}/issues/{issue_number}"

            command = [
                "project", "item-add", self.project_id,
                "--owner", self.repo_owner,
                "--url", issue_url
            ]

            try:
                self.run_gh_command(command)
                print(f"  ✓ #{issue_number} ({task_id})")
            except subprocess.CalledProcessError as e:
                print(f"  ✗ #{issue_number} - エラー: {e}")

        print("✅ Issue追加完了")

    def setup_project_fields(self):
        """Projects V2にカスタムフィールドを追加"""
        if not self.project_id:
            print("⚠️  Project IDが設定されていません。スキップします。")
            return

        print(f"\n⚙️  Projectsカスタムフィールド設定中...")

        # カスタムフィールド定義
        fields = [
            {"name": "Weight", "data_type": "NUMBER"},
            {"name": "Effort (Days)", "data_type": "NUMBER"},
            {"name": "Week", "data_type": "TEXT"},
        ]

        for field in fields:
            command = [
                "project", "field-create", self.project_id,
                "--owner", self.repo_owner,
                "--name", field["name"],
                "--data-type", field["data_type"]
            ]

            try:
                self.run_gh_command(command)
                print(f"  ✓ {field['name']} ({field['data_type']})")
            except subprocess.CalledProcessError:
                # 既に存在する場合はスキップ
                print(f"  - {field['name']} (既存)")

        print("✅ カスタムフィールド設定完了")
        print("\n📌 次のステップ:")
        print("  1. GitHubでProjectsを開く")
        print("  2. ビューを作成（Board, Table, Roadmap）")
        print("  3. Status, Start Date, End Date フィールドを手動で設定")

    def sync_all(self, repo_name: str, visibility: str = "private"):
        """全体の同期処理を実行"""
        print("=" * 70)
        print("🚀 GitHub同期開始")
        print("=" * 70)

        # 認証確認
        self.check_gh_auth()

        # リポジトリ作成
        self.create_repository(repo_name, visibility)

        # ラベル作成
        self.create_labels()

        # マイルストーン作成
        self.create_milestones()

        # Issues作成
        self.create_issues()

        # Projects作成
        project_name = f"{self.project_info['name']} - プロジェクト管理"
        self.create_project(project_name)

        # IssuesをProjectsに追加
        self.add_issues_to_project()

        # カスタムフィールド設定
        self.setup_project_fields()

        print("\n" + "=" * 70)
        print("✅ GitHub同期完了")
        print("=" * 70)
        print(f"\n📦 リポジトリ: https://github.com/{self.repo_full_name}")
        print(f"📊 Projects: https://github.com/users/{self.repo_owner}/projects/{self.project_id}")
        print(f"📝 Issues: https://github.com/{self.repo_full_name}/issues")


def main():
    """メイン処理"""
    print("📊 GitHub Issues & Projects同期ツール")
    print("=" * 70)

    # プロジェクトディレクトリ
    base_dir = Path(__file__).parent.parent

    # 環境変数からリポジトリ名を取得
    repo_name = os.environ.get("GITHUB_REPO_NAME")
    if not repo_name:
        print("\nGitHubリポジトリ名を入力してください。")
        print("例: project-requirements-system")
        repo_name = input("リポジトリ名: ").strip()

        if not repo_name:
            print("ERROR: リポジトリ名が指定されていません。")
            sys.exit(1)

    # 可視性を取得
    visibility = os.environ.get("GITHUB_REPO_VISIBILITY", "private")

    # 同期マネージャーを初期化
    manager = GitHubSyncManager(base_dir)

    # 同期実行
    try:
        manager.sync_all(repo_name, visibility)
    except KeyboardInterrupt:
        print("\n\n⚠️  ユーザーによって中断されました。")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
