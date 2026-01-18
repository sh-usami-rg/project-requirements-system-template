#!/usr/bin/env python3
"""
tasks.jsonに中カテゴリ（midCategory）フィールドを追加するスクリプト

使い方:
    python3 scripts/add-mid-category.py

機能:
    - tasks.jsonの各タスクにmidCategoryフィールドを追加
    - タスク内容を分析して中カテゴリを提案（MID_CATEGORY_MAPPINGで定義）
    - 中カテゴリ別の件数を表示
"""

import json
import sys
from pathlib import Path
from collections import Counter


# 中カテゴリマッピング（プロジェクトに応じてカスタマイズしてください）
# キー: タスクID、値: 中カテゴリ名
MID_CATEGORY_MAPPING = {
    # Phase 1タスク
    "TASK-001": "調査・分析",
    "TASK-002": "調査・分析",
    "TASK-003": "調査・分析",
    "TASK-004": "環境構築",
    "TASK-005": "要件定義",
    "TASK-006": "要件定義",
    "TASK-007": "要件定義",
    "TASK-008": "設計",

    # Phase 2タスク
    "TASK-009": "実装",
    "TASK-010": "実装",
    "TASK-011": "実装",
    "TASK-012": "テスト",
    "TASK-013": "環境構築",
    "TASK-014": "環境構築",
    "TASK-015": "実装",
    "TASK-016": "ドキュメント作成",
    "TASK-017": "トレーニング",

    # Phase 3タスク
    "TASK-018": "実装",
    "TASK-019": "実装",
    "TASK-020": "実装",
    "TASK-021": "実装",
    "TASK-022": "テスト",
    "TASK-023": "ドキュメント作成",
    "TASK-024": "トレーニング",
    "TASK-025": "デプロイ・リリース",
}


def load_tasks_json(tasks_file: Path) -> dict:
    """tasks.jsonを読み込む"""
    try:
        with open(tasks_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ エラー: {tasks_file} が見つかりません")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ エラー: {tasks_file} のJSON形式が不正です: {e}")
        sys.exit(1)


def save_tasks_json(tasks_file: Path, data: dict) -> None:
    """tasks.jsonを保存する"""
    try:
        with open(tasks_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ エラー: {tasks_file} の保存に失敗しました: {e}")
        sys.exit(1)


def add_mid_category(data: dict) -> tuple[int, Counter]:
    """
    各タスクにmidCategoryフィールドを追加

    Returns:
        (追加された件数, 中カテゴリ別のカウンター)
    """
    added_count = 0
    mid_category_counter = Counter()

    for task in data.get("tasks", []):
        task_id = task.get("id")

        # 既にmidCategoryが設定されている場合はスキップ
        if "midCategory" in task and task["midCategory"]:
            mid_category_counter[task["midCategory"]] += 1
            continue

        # MID_CATEGORY_MAPPINGから中カテゴリを取得
        if task_id in MID_CATEGORY_MAPPING:
            mid_category = MID_CATEGORY_MAPPING[task_id]
            task["midCategory"] = mid_category
            mid_category_counter[mid_category] += 1
            added_count += 1
            print(f"✓ {task_id}: {mid_category}")
        else:
            # マッピングに存在しない場合は警告を表示
            print(f"⚠️  {task_id}: マッピングに定義されていません（スキップ）")

    return added_count, mid_category_counter


def display_summary(added_count: int, total_count: int, mid_category_counter: Counter) -> None:
    """サマリーを表示"""
    print()
    if added_count > 0:
        print(f"✅ 中カテゴリを{added_count}タスクに追加しました")
    else:
        print("ℹ️  追加された中カテゴリはありません（既に設定済み）")

    print()
    print("📊 中カテゴリ別件数:")
    for mid_category, count in sorted(mid_category_counter.items()):
        print(f"  - {mid_category}: {count}タスク")

    print()
    print(f"📝 合計: {total_count}タスク")


def main():
    """メイン処理"""
    # tasks.jsonのパスを取得
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    tasks_file = project_root / "tasks.json"

    print(f"📄 tasks.jsonを読み込み中: {tasks_file}")
    print()

    # tasks.jsonを読み込み
    data = load_tasks_json(tasks_file)

    # 中カテゴリを追加
    added_count, mid_category_counter = add_mid_category(data)

    # tasks.jsonを保存
    save_tasks_json(tasks_file, data)

    # サマリーを表示
    total_count = len(data.get("tasks", []))
    display_summary(added_count, total_count, mid_category_counter)

    print()
    print("💡 ヒント:")
    print("  - MID_CATEGORY_MAPPINGを編集して、各タスクの中カテゴリをカスタマイズできます")
    print("  - GitHubに同期するには、以下のコマンドを実行してください:")
    print("    python3 scripts/update-mid-category-to-github.py")
    print("    python3 scripts/add-mid-category-field-to-projects.py")


if __name__ == "__main__":
    main()
