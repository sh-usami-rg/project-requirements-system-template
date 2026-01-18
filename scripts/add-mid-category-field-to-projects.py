#!/usr/bin/env python3
"""
GitHub Projects V2に「Mid Category」フィールドを追加するスクリプト

使い方:
    python3 scripts/add-mid-category-field-to-projects.py

前提条件:
    - GitHub CLI (gh) がインストールされ、認証されていること
    - tasks.jsonにmidCategoryフィールドが追加されていること
    - GitHub Projects V2が作成されていること

機能:
    1. Projects V2に Single Select フィールド「Mid Category」を作成
    2. 中カテゴリオプションを設定
    3. 各Issueにフィールド値を設定
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set


# 中カテゴリのフィールドカラー
FIELD_COLORS = [
    "GREEN", "BLUE", "PURPLE", "YELLOW", "RED", "PINK", "ORANGE",
    "GRAY", "TEAL", "CYAN", "LIME", "VIOLET", "SKY", "ROSE",
    "FUCHSIA", "EMERALD", "AMBER", "INDIGO"
]


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


def run_graphql_query(query: str) -> dict:
    """GraphQL APIクエリを実行"""
    result = run_gh_command(["api", "graphql", "-f", f"query={query}"])
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"❌ エラー: GraphQLレスポンスのパースに失敗しました: {e}")
        print(f"レスポンス: {result.stdout}")
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


def get_repository_info() -> Dict[str, str]:
    """リポジトリ情報を取得"""
    result = run_gh_command(["repo", "view", "--json", "owner,name"])
    data = json.loads(result.stdout)
    return {
        "owner": data["owner"]["login"],
        "name": data["name"]
    }


def get_all_mid_categories(tasks_data: dict) -> List[str]:
    """tasks.jsonから全ての中カテゴリを取得（ソート済み）"""
    mid_categories = set()
    for task in tasks_data.get("tasks", []):
        if "midCategory" in task and task["midCategory"]:
            mid_categories.add(task["midCategory"])
    return sorted(mid_categories)


def find_project_v2(owner: str, repo_name: str) -> Dict[str, str]:
    """Projects V2を検索"""
    print("🔍 GitHub Projects V2を検索中...")

    query = f"""
    {{
      repository(owner: "{owner}", name: "{repo_name}") {{
        projectsV2(first: 10) {{
          nodes {{
            id
            title
            number
          }}
        }}
      }}
    }}
    """

    response = run_graphql_query(query)

    projects = response.get("data", {}).get("repository", {}).get("projectsV2", {}).get("nodes", [])

    if not projects:
        print("❌ エラー: GitHub Projects V2が見つかりません")
        print("先にプロジェクトを作成してください:")
        print("  python3 scripts/sync-github.py")
        sys.exit(1)

    # 最初のプロジェクトを使用
    project = projects[0]
    print(f"  ✓ プロジェクト '{project['title']}' を見つけました（ID: {project['id'][:10]}...）")

    return {
        "id": project["id"],
        "title": project["title"],
        "number": project["number"]
    }


def check_existing_field(project_id: str) -> bool:
    """既存の「Mid Category」フィールドをチェック"""
    query = f"""
    {{
      node(id: "{project_id}") {{
        ... on ProjectV2 {{
          fields(first: 20) {{
            nodes {{
              ... on ProjectV2SingleSelectField {{
                id
                name
              }}
            }}
          }}
        }}
      }}
    }}
    """

    response = run_graphql_query(query)
    fields = response.get("data", {}).get("node", {}).get("fields", {}).get("nodes", [])

    for field in fields:
        if field.get("name") == "Mid Category":
            print("  ⏭️  'Mid Category' フィールドは既に存在します（スキップ）")
            return True

    return False


def create_mid_category_field(project_id: str, mid_categories: List[str]) -> Dict[str, any]:
    """Mid CategoryフィールドをProjects V2に作成"""
    print()
    print("📋 'Mid Category' フィールドを作成中...")

    # フィールドが既に存在するかチェック
    if check_existing_field(project_id):
        # 既存フィールドの情報を取得
        return get_existing_field_info(project_id)

    # オプションを作成
    options = []
    for i, category in enumerate(mid_categories):
        color = FIELD_COLORS[i % len(FIELD_COLORS)]
        options.append(f'{{name: "{category}", description: "{category}カテゴリのタスク", color: {color}}}')

    options_str = ", ".join(options)

    mutation = f"""
    mutation {{
      createProjectV2Field(
        input: {{
          projectId: "{project_id}"
          dataType: SINGLE_SELECT
          name: "Mid Category"
          singleSelectOptions: [{options_str}]
        }}
      ) {{
        projectV2Field {{
          ... on ProjectV2SingleSelectField {{
            id
            name
            options {{
              id
              name
            }}
          }}
        }}
      }}
    }}
    """

    response = run_graphql_query(mutation)

    field_data = response.get("data", {}).get("createProjectV2Field", {}).get("projectV2Field", {})

    if not field_data:
        print("❌ エラー: フィールドの作成に失敗しました")
        print(f"レスポンス: {response}")
        sys.exit(1)

    print(f"  ✓ フィールドを作成しました（ID: {field_data['id'][:10]}...）")
    print()
    print("  オプション一覧:")
    for option in field_data.get("options", []):
        print(f"    - {option['name']}")

    return field_data


def get_existing_field_info(project_id: str) -> Dict[str, any]:
    """既存の「Mid Category」フィールド情報を取得"""
    query = f"""
    {{
      node(id: "{project_id}") {{
        ... on ProjectV2 {{
          fields(first: 20) {{
            nodes {{
              ... on ProjectV2SingleSelectField {{
                id
                name
                options {{
                  id
                  name
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    """

    response = run_graphql_query(query)
    fields = response.get("data", {}).get("node", {}).get("fields", {}).get("nodes", [])

    for field in fields:
        if field.get("name") == "Mid Category":
            return field

    return None


def get_project_items(project_id: str) -> List[Dict[str, str]]:
    """プロジェクトの全アイテム（Issue）を取得"""
    query = f"""
    {{
      node(id: "{project_id}") {{
        ... on ProjectV2 {{
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

    response = run_graphql_query(query)
    items = response.get("data", {}).get("node", {}).get("items", {}).get("nodes", [])

    result = []
    for item in items:
        content = item.get("content", {})
        if content:
            result.append({
                "item_id": item["id"],
                "issue_number": content.get("number"),
                "title": content.get("title")
            })

    return result


def update_item_field_value(project_id: str, item_id: str, field_id: str, option_id: str) -> None:
    """プロジェクトアイテムのフィールド値を更新"""
    mutation = f"""
    mutation {{
      updateProjectV2ItemFieldValue(
        input: {{
          projectId: "{project_id}"
          itemId: "{item_id}"
          fieldId: "{field_id}"
          value: {{
            singleSelectOptionId: "{option_id}"
          }}
        }}
      ) {{
        projectV2Item {{
          id
        }}
      }}
    }}
    """

    run_graphql_query(mutation)


def set_field_values_for_issues(
    project_id: str,
    field_data: Dict[str, any],
    tasks_data: dict,
    mapping_data: dict
) -> int:
    """各Issueにフィールド値を設定"""
    print()
    print("🔗 各Issueにフィールド値を設定中...")

    # プロジェクトアイテムを取得
    project_items = get_project_items(project_id)

    # Issue番号 -> アイテムIDのマッピングを作成
    issue_to_item = {item["issue_number"]: item["item_id"] for item in project_items}

    # 中カテゴリ名 -> オプションIDのマッピングを作成
    category_to_option = {
        option["name"]: option["id"]
        for option in field_data.get("options", [])
    }

    updated_count = 0

    for task in tasks_data.get("tasks", []):
        task_id = task.get("id")
        mid_category = task.get("midCategory")

        # midCategoryが設定されていない場合はスキップ
        if not mid_category:
            continue

        # Issue番号を取得
        issue_number = mapping_data.get(task_id)
        if not issue_number:
            continue

        # アイテムIDを取得
        item_id = issue_to_item.get(issue_number)
        if not item_id:
            print(f"  ⚠️  Issue #{issue_number}: プロジェクトアイテムが見つかりません")
            continue

        # オプションIDを取得
        option_id = category_to_option.get(mid_category)
        if not option_id:
            print(f"  ⚠️  {mid_category}: オプションが見つかりません")
            continue

        # フィールド値を更新
        try:
            update_item_field_value(
                project_id,
                item_id,
                field_data["id"],
                option_id
            )
            print(f"  ✓ Issue #{issue_number}: {mid_category}")
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

    # リポジトリ情報を取得
    print("📦 リポジトリ情報を取得中...")
    repo_info = get_repository_info()
    print(f"  リポジトリ: {repo_info['owner']}/{repo_info['name']}")
    print()

    # 全ての中カテゴリを取得
    mid_categories = get_all_mid_categories(tasks_data)

    if not mid_categories:
        print("⚠️  警告: tasks.jsonに中カテゴリが設定されていません")
        print("  先に scripts/add-mid-category.py を実行してください")
        sys.exit(1)

    print(f"📊 中カテゴリ: {len(mid_categories)}個")
    for category in mid_categories:
        print(f"  - {category}")
    print()

    # Projects V2を検索
    project = find_project_v2(repo_info["owner"], repo_info["name"])

    # Mid Categoryフィールドを作成
    field_data = create_mid_category_field(project["id"], mid_categories)

    # 各Issueにフィールド値を設定
    updated_count = set_field_values_for_issues(
        project["id"],
        field_data,
        tasks_data,
        mapping_data
    )

    # サマリーを表示
    print()
    print(f"✅ {updated_count}個のIssueにフィールド値を設定しました")
    print()
    print("💡 次のステップ:")
    print("  GitHub Projects V2を開いて、以下を確認してください:")
    print("  1. ロードマップビューで「Group by: Mid Category」を選択")
    print("  2. 中カテゴリごとにタスクがグループ化されていることを確認")
    print()
    print(f"  プロジェクトURL: https://github.com/{repo_info['owner']}/{repo_info['name']}/projects/{project['number']}")


if __name__ == "__main__":
    main()
