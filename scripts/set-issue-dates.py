#!/usr/bin/env python3
"""
GitHub Projects V2のIssuesに開始日・終了日を一括設定するスクリプト

使用方法:
    python3 scripts/set-issue-dates.py --project-number PROJECT_NUMBER

前提条件:
    - GitHub CLIがインストール・認証済み
    - GitHub Projects V2が作成済み
    - Projects V2に「Start Date」「End Date」フィールドが作成済み
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional


def run_gh_api(query: str) -> Dict:
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
        print(f"ERROR: GraphQL API error: {e.stderr}")
        raise


def get_project_info(owner: str, project_number: int) -> Dict:
    """プロジェクト情報を取得"""
    query = f"""
    {{
      user(login: "{owner}") {{
        projectV2(number: {project_number}) {{
          id
          title
          fields(first: 20) {{
            nodes {{
              ... on ProjectV2Field {{
                id
                name
              }}
              ... on ProjectV2SingleSelectField {{
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
                  title
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    """

    result = run_gh_api(query)

    try:
        return result["data"]["user"]["projectV2"]
    except (KeyError, TypeError):
        print(f"ERROR: Project not found or invalid response")
        print(f"Response: {json.dumps(result, indent=2)}")
        sys.exit(1)


def update_item_field(project_id: str, item_id: str, field_id: str, value: str):
    """Project ItemのフィールドValue を更新"""
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

    try:
        run_gh_api(mutation)
    except Exception as e:
        print(f"  ⚠️  Failed to update field: {e}")


def main():
    # 引数チェック
    if len(sys.argv) < 2 or not sys.argv[1].startswith("--project-number="):
        print("使用方法: python3 scripts/set-issue-dates.py --project-number=PROJECT_NUMBER")
        print("\nProject Numberの確認方法:")
        print("  1. GitHub Projects V2を開く")
        print("  2. URLの末尾の数字がProject Number")
        print("     例: https://github.com/users/sh-usami-rg/projects/1 → Project Number = 1")
        sys.exit(1)

    project_number = int(sys.argv[1].split("=")[1])
    owner = "sh-usami-rg"

    print(f"📊 GitHub Projects V2 日付設定スクリプト")
    print(f"=" * 70)
    print(f"Project Number: {project_number}")
    print(f"Owner: {owner}\n")

    # データ読み込み
    base_dir = Path(__file__).parent.parent
    with open(base_dir / "schedule.json", "r", encoding="utf-8") as f:
        schedule_data = json.load(f)

    # Issue番号マッピング読み込み
    mapping_file = base_dir / "github-issue-mapping.json"
    if not mapping_file.exists():
        print("ERROR: github-issue-mapping.json が見つかりません")
        sys.exit(1)

    with open(mapping_file, "r", encoding="utf-8") as f:
        issue_mapping = json.load(f)  # TASK-ID -> Issue番号

    # プロジェクト情報取得
    print("📋 プロジェクト情報を取得中...")
    project_info = get_project_info(owner, project_number)
    project_id = project_info["id"]
    print(f"✓ Project ID: {project_id}")
    print(f"✓ Project Title: {project_info['title']}\n")

    # フィールドIDを取得
    fields = {field["name"]: field["id"] for field in project_info["fields"]["nodes"]}

    start_date_field_id = fields.get("Start Date")
    end_date_field_id = fields.get("End Date")

    if not start_date_field_id or not end_date_field_id:
        print("ERROR: 'Start Date' または 'End Date' フィールドが見つかりません")
        print("\nProjects V2で以下のフィールドを作成してください:")
        print("  1. Projects V2を開く")
        print("  2. '+ New field' をクリック")
        print("  3. Field type: 'Date' を選択")
        print("  4. Field name: 'Start Date' を入力して作成")
        print("  5. 同様に 'End Date' も作成")
        print(f"\n現在のフィールド: {list(fields.keys())}")
        sys.exit(1)

    print(f"✓ Start Date Field ID: {start_date_field_id}")
    print(f"✓ End Date Field ID: {end_date_field_id}\n")

    # Issue番号 -> Project Item IDのマッピング作成
    issue_to_item = {}
    for item in project_info["items"]["nodes"]:
        if item["content"]:
            issue_number = str(item["content"]["number"])
            issue_to_item[issue_number] = item["id"]

    print(f"📅 日付を設定中（{len(schedule_data['tasks'])}個）...\n")

    updated_count = 0
    error_count = 0

    # 各タスクの日付を設定
    for task in schedule_data["tasks"]:
        task_id = task["id"]
        start_date = task["startDate"]
        end_date = task["endDate"]

        # Issue番号を取得
        if task_id not in issue_mapping:
            print(f"  ⚠️  {task_id}: Issue番号が見つかりません")
            error_count += 1
            continue

        issue_number = issue_mapping[task_id]

        # Project Item IDを取得
        if issue_number not in issue_to_item:
            print(f"  ⚠️  {task_id} (#{issue_number}): ProjectにIssueが追加されていません")
            error_count += 1
            continue

        item_id = issue_to_item[issue_number]

        # Start Dateを設定
        try:
            update_item_field(project_id, item_id, start_date_field_id, start_date)
            # End Dateを設定
            update_item_field(project_id, item_id, end_date_field_id, end_date)
            print(f"  ✓ {task_id} (#{issue_number}): {start_date} 〜 {end_date}")
            updated_count += 1
        except Exception as e:
            print(f"  ✗ {task_id} (#{issue_number}): エラー - {e}")
            error_count += 1

    print(f"\n{'=' * 70}")
    print(f"✅ 完了: {updated_count}/{len(schedule_data['tasks'])}個のIssueに日付を設定")
    if error_count > 0:
        print(f"⚠️  エラー: {error_count}個")
    print(f"\n📊 Roadmapビューで確認してください:")
    print(f"   https://github.com/users/{owner}/projects/{project_number}")


if __name__ == "__main__":
    main()
