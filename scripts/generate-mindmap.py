#!/usr/bin/env python3
"""
マインドマップ生成スクリプト - tasks.jsonからMarkdownマインドマップを生成

このスクリプトは以下を実行します：
1. tasks.jsonからタスク情報を読み込み
2. Phase > Mid Category > Task の階層構造でマインドマップを生成
3. docs/MINDMAP.mdとして出力

使い方:
    python3 scripts/generate-mindmap.py

出力:
    docs/MINDMAP.md
"""

import json
import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, List

def load_tasks() -> Dict:
    """tasks.jsonを読み込む"""
    with open('tasks.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_status_emoji(status: str) -> str:
    """ステータスに応じた絵文字を返す"""
    emoji_map = {
        'done': '✅',
        'completed': '✅',
        'in_progress': '🔄',
        'pending': '📝',
        'not_started': '📝',
        'blocked': '🚫',
        'cancelled': '❌'
    }
    return emoji_map.get(status, '❓')

def get_priority_emoji(priority: str) -> str:
    """優先度に応じた絵文字を返す"""
    emoji_map = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢'
    }
    return emoji_map.get(priority, '⚪')

def calculate_completion_stats(tasks: List[Dict]) -> Dict:
    """タスクリストから完了統計を計算"""
    total = len(tasks)
    completed = sum(1 for t in tasks if t.get('status') in ['done', 'completed'])
    in_progress = sum(1 for t in tasks if t.get('status') == 'in_progress')
    pending = sum(1 for t in tasks if t.get('status') in ['pending', 'not_started'])

    completion_rate = (completed / total * 100) if total > 0 else 0

    return {
        'total': total,
        'completed': completed,
        'in_progress': in_progress,
        'pending': pending,
        'completion_rate': completion_rate
    }

def generate_mindmap_content(data: Dict) -> str:
    """マインドマップのMarkdownコンテンツを生成"""
    project = data.get('project', {})
    tasks = data.get('tasks', [])

    project_name = project.get('name', 'Unknown Project')
    start_date = project.get('startDate', 'N/A')
    end_date = project.get('estimatedEndDate', project.get('endDate', 'N/A'))

    # タスクを Phase > Mid Category > Task の階層に整理
    hierarchy = defaultdict(lambda: defaultdict(list))

    for task in tasks:
        phase = task.get('phase', 'Unknown Phase')
        mid_cat = task.get('midCategory', 'その他')
        hierarchy[phase][mid_cat].append(task)

    # マインドマップを生成
    mindmap = f"""# {project_name} - プロジェクトマインドマップ

**生成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**プロジェクト期間**: {start_date} 〜 {end_date}

---

## プロジェクト全体

```
{project_name}
"""

    # Phase別に展開
    for phase in sorted(hierarchy.keys()):
        mindmap += f"├── {phase}\n"

        mid_cats = hierarchy[phase]
        mid_cat_list = sorted(mid_cats.keys())

        for i, mid_cat in enumerate(mid_cat_list):
            is_last_mid_cat = (i == len(mid_cat_list) - 1)
            mid_cat_prefix = "└──" if is_last_mid_cat else "├──"

            task_list = mid_cats[mid_cat]
            stats = calculate_completion_stats(task_list)

            mindmap += f"│   {mid_cat_prefix} {mid_cat} ({stats['completed']}/{stats['total']}タスク完了, {stats['completion_rate']:.0f}%)\n"

            # タスクを展開
            for j, task in enumerate(task_list):
                is_last_task = (j == len(task_list) - 1)

                if is_last_mid_cat:
                    task_prefix = "    └──" if is_last_task else "    ├──"
                else:
                    task_prefix = "│       └──" if is_last_task else "│       ├──"

                status_emoji = get_status_emoji(task.get('status', 'pending'))
                priority_emoji = get_priority_emoji(task.get('priority', 'medium'))
                task_id = task.get('id', 'N/A')
                task_title = task.get('title', task.get('name', 'Unnamed'))

                # 日付と重みを追加
                start = task.get('start_date', 'N/A')
                end = task.get('end_date', 'N/A')
                weight = task.get('weight', 0)

                # Format: MM-DD形式
                start_short = start[5:] if start != 'N/A' and len(start) > 5 else 'N/A'
                end_short = end[5:] if end != 'N/A' and len(end) > 5 else 'N/A'

                mindmap += f"{task_prefix} {status_emoji} {priority_emoji} [{task_id}] {task_title} ({start_short}〜{end_short}, W={weight})\n"

    mindmap += "```\n\n"

    # 凡例を追加
    mindmap += """---

## 凡例

### ステータス

- ✅ 完了 (done, completed)
- 🔄 進行中 (in_progress)
- 📝 未着手 (pending, not_started)
- 🚫 ブロック中 (blocked)
- ❌ キャンセル (cancelled)

### 優先度

- 🔴 Critical (緊急)
- 🟠 High (高)
- 🟡 Medium (中)
- 🟢 Low (低)

---

## Phase別サマリー

| Phase | タスク数 | 完了 | 進行中 | 未着手 | 完了率 |
|-------|---------|------|--------|--------|--------|
"""

    # Phase別統計
    for phase in sorted(hierarchy.keys()):
        all_tasks = []
        for mid_cat, task_list in hierarchy[phase].items():
            all_tasks.extend(task_list)

        stats = calculate_completion_stats(all_tasks)
        mindmap += f"| {phase} | {stats['total']} | {stats['completed']} | {stats['in_progress']} | {stats['pending']} | {stats['completion_rate']:.1f}% |\n"

    mindmap += "\n---\n\n## 中カテゴリ別サマリー\n\n| 中カテゴリ | タスク数 | 完了 | 進行中 | 未着手 | 完了率 |\n|-----------|---------|------|--------|--------|--------|\n"

    # 中カテゴリ別統計
    mid_cat_stats = defaultdict(list)
    for phase, mid_cats in hierarchy.items():
        for mid_cat, task_list in mid_cats.items():
            mid_cat_stats[mid_cat].extend(task_list)

    for mid_cat in sorted(mid_cat_stats.keys()):
        task_list = mid_cat_stats[mid_cat]
        stats = calculate_completion_stats(task_list)
        mindmap += f"| {mid_cat} | {stats['total']} | {stats['completed']} | {stats['in_progress']} | {stats['pending']} | {stats['completion_rate']:.1f}% |\n"

    mindmap += "\n---\n\n## タスク詳細リスト\n\n"

    # タスク詳細
    for phase in sorted(hierarchy.keys()):
        mindmap += f"### {phase}\n\n"

        for mid_cat in sorted(hierarchy[phase].keys()):
            mindmap += f"#### {mid_cat}\n\n"

            for task in hierarchy[phase][mid_cat]:
                task_id = task.get('id', 'N/A')
                task_title = task.get('title', task.get('name', 'Unnamed'))
                status = task.get('status', 'pending')
                priority = task.get('priority', 'medium')
                assignee = task.get('assignee', '未割当')
                start_date = task.get('start_date', task.get('startDate', 'N/A'))
                end_date = task.get('end_date', task.get('endDate', 'N/A'))
                description = task.get('description', '')

                status_emoji = get_status_emoji(status)
                priority_emoji = get_priority_emoji(priority)

                mindmap += f"**{status_emoji} {priority_emoji} [{task_id}] {task_title}**\n\n"
                mindmap += f"- **ステータス**: {status}\n"
                mindmap += f"- **優先度**: {priority}\n"
                mindmap += f"- **担当者**: {assignee}\n"
                mindmap += f"- **期間**: {start_date} 〜 {end_date}\n"

                if description:
                    mindmap += f"- **説明**: {description}\n"

                # 依存関係
                dependencies = task.get('dependencies', [])
                if dependencies:
                    mindmap += f"- **依存**: {', '.join(dependencies)}\n"

                mindmap += "\n"

            mindmap += "\n"

    return mindmap

def main():
    """メイン処理"""
    print("🌳 マインドマップ生成を開始します...")

    # tasks.jsonを読み込み
    data = load_tasks()

    # マインドマップを生成
    mindmap_content = generate_mindmap_content(data)

    # docs/MINDMAP.mdに出力
    os.makedirs('docs', exist_ok=True)
    output_path = 'docs/MINDMAP.md'

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(mindmap_content)

    print(f"✅ マインドマップを生成しました: {output_path}")

if __name__ == '__main__':
    main()
