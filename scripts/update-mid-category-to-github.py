#!/usr/bin/env python3
"""
GitHub Issueに中カテゴリを反映するスクリプト

使い方:
    python3 scripts/update-mid-category-to-github.py

前提条件:
    - GitHub CLI (gh) がインストールされ、認証されていること
    - tasks.jsonにmidCategoryフィールドが追加されていること
    - github-issue-mapping.jsonが存在すること

機能:
    1. 中カテゴリラベル（mid:XXX）を作成
    2. Issueタイトルを「中カテゴリ：タスク名」形式に変更
    3. 各Issueに中カテゴリラベルを付与
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Set


# 中カテゴリのラベルカラー（16色）
LABEL_COLORS = {
    "計画策定": "10B981",      # Green
    "要件定義": "3B82F6",      # Blue
    "設計": "8B5CF6",          # Purple
    "環境構築": "F59E0B",      # Yellow
    "実装": "EF4444",          # Red
    "フロントエンド実装": "EC4899",  # Pink
    "バックエンド実装": "F97316",   # Orange
    "テスト": "14B8A6",        # Teal
    "デプロイ・リリース": "6366F1",  # Indigo
    "調査・分析": "06B6D4",    # Cyan
    "データモデル設計": "84CC16",  # Lime
    "学習": "A855F7",          # Violet
    "PoC": "0EA5E9",           # Sky
    "BigQuery実装": "F43F5E",  # Rose
    "LookerML実装": "D946EF",  # Fuchsia
    "精度検証": "10B981",      # Emerald
    "ユーザーテスト": "F59E0B", # Amber
    "本番リリース": "EF4444",   # Red
    "ドキュメント作成": "6366F1", # Indigo
    "トレーニング": "8B5CF6",   # Purple
}


def run_gh_command(args: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """GitHub CLIコマンドを実行"""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        if check:
            print(f"❌ エラー: GitHub CLIコマンドの実行に失敗しました")
            print(f"コマンド: gh {' '.join(args)}")
            print(f"エラー: {e.stderr}")
            sys.exit(1)
        return e
    except FileNotFoundError:
        print("❌ エラー: GitHub CLI (gh) がインストールされていません")
        print("インストール方法: https://cli.github.com/")
        sys.exit(1)


def load_json_file(file_path: Path) -> dict:
    """JSONファイルを読み込む"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ エラー: {file_path} が見つかりません")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ エラー: {file_path} のJSON形式が不正です: {e}")
        sys.exit(1)


def get_repository_name() -> str:
    """現在のリポジトリ名を取得"""
    result = run_gh_command(["repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"])
    return result.stdout.strip()


def get_all_mid_categories(tasks_data: dict) -> Set[str]:
    """tasks.jsonから全ての中カテゴリを取得"""
    mid_categories = set()
    for task in tasks_data.get("tasks", []):
        if "midCategory" in task and task["midCategory"]:
            mid_categories.add(task["midCategory"])
    return mid_categories


def create_mid_category_labels(repo: str, mid_categories: Set[str]) -> None:
    """中カテゴリラベルを作成"""
    print("🏷️  中カテゴリラベルを作成中...")

    for category in sorted(mid_categories):
        label_name = f"mid:{category}"
        color = LABEL_COLORS.get(category, "D1D5DB")  # デフォルトはグレー

        # ラベルが既に存在するかチェック
        result = run_gh_command(
            ["label", "list", "--repo", repo, "--json", "name", "-q", f'.[] | select(.name == "{label_name}") | .name'],
            check=False
        )

        if result.stdout.strip() == label_name:
            print(f"  ⏭️  ラベル '{label_name}' は既に存在します（スキップ）")
            continue

        # ラベルを作成
        run_gh_command([
            "label", "create", label_name,
            "--repo", repo,
            "--color", color,
            "--description", f"{category}カテゴリのタスク"
        ])
        print(f"  ✓ ラベル '{label_name}' を作成しました（色: #{color}）")


def update_issue_titles_and_labels(repo: str, tasks_data: dict, mapping_data: dict) -> int:
    """Issueタイトルと中カテゴリラベルを更新"""
    print()
    print("📝 Issueタイトルと中カテゴリラベルを更新中...")

    updated_count = 0

    for task in tasks_data.get("tasks", []):
        task_id = task.get("id")
        task_title = task.get("title")
        mid_category = task.get("midCategory")

        # midCategoryが設定されていない場合はスキップ
        if not mid_category:
            print(f"  ⚠️  {task_id}: 中カテゴリが設定されていません（スキップ）")
            continue

        # Issue番号を取得
        issue_number = mapping_data.get(task_id)
        if not issue_number:
            print(f"  ⚠️  {task_id}: GitHub Issue番号が見つかりません（スキップ）")
            continue

        # 新しいタイトル: 「中カテゴリ：タスク名」
        new_title = f"{mid_category}：{task_title}"

        # 中カテゴリラベル
        label_name = f"mid:{mid_category}"

        # Issueを更新
        try:
            run_gh_command([
                "issue", "edit", str(issue_number),
                "--repo", repo,
                "--title", new_title,
                "--add-label", label_name
            ])
            print(f"  ✓ Issue #{issue_number}: {new_title}")
            updated_count += 1
        except Exception as e:
            print(f"  ❌ Issue #{issue_number} の更新に失敗: {e}")

    return updated_count


def main():
    """メイン処理"""
    # ファイルパスを取得
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    tasks_file = project_root / "tasks.json"
    mapping_file = project_root / "github-issue-mapping.json"

    # JSONファイルを読み込み
    tasks_data = load_json_file(tasks_file)
    mapping_data = load_json_file(mapping_file)

    # リポジトリ名を取得
    print("📦 リポジトリ情報を取得中...")
    repo = get_repository_name()
    print(f"  リポジトリ: {repo}")
    print()

    # 全ての中カテゴリを取得
    mid_categories = get_all_mid_categories(tasks_data)

    if not mid_categories:
        print("⚠️  警告: tasks.jsonに中カテゴリが設定されていません")
        print("  先に scripts/add-mid-category.py を実行してください")
        sys.exit(1)

    print(f"📊 中カテゴリ: {len(mid_categories)}個")
    for category in sorted(mid_categories):
        print(f"  - {category}")
    print()

    # 中カテゴリラベルを作成
    create_mid_category_labels(repo, mid_categories)

    # Issueタイトルとラベルを更新
    updated_count = update_issue_titles_and_labels(repo, tasks_data, mapping_data)

    # サマリーを表示
    print()
    print(f"✅ {updated_count}個のIssueを更新しました")
    print()
    print("💡 次のステップ:")
    print("  Projects V2に中カテゴリフィールドを追加するには、以下のコマンドを実行してください:")
    print("  python3 scripts/add-mid-category-field-to-projects.py")


if __name__ == "__main__":
    main()
