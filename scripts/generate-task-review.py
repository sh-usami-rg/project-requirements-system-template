#!/usr/bin/env python3
"""
タスクレビュードキュメント生成スクリプト
ASCIIツリーと詳細表でプロジェクトの全タスクを可視化
"""

import json
from pathlib import Path
from datetime import datetime

def create_ascii_tree(tasks, project_name):
    """タスク一覧をASCIIツリー形式で生成（開始日・終了日・重み付き）"""
    # Group by phase and midCategory
    phases = {}
    for task in tasks:
        phase = task.get('phase', 'Unknown')
        mid = task.get('midCategory', 'その他')

        if phase not in phases:
            phases[phase] = {}
        if mid not in phases[phase]:
            phases[phase][mid] = []

        phases[phase][mid].append(task)

    # Build tree
    lines = []
    lines.append(project_name)

    phase_list = sorted(phases.keys())
    for i, phase in enumerate(phase_list):
        is_last_phase = (i == len(phase_list) - 1)
        phase_prefix = '└──' if is_last_phase else '├──'

        lines.append(f'{phase_prefix} {phase}')

        mids = sorted(phases[phase].keys())
        for j, mid in enumerate(mids):
            is_last_mid = (j == len(mids) - 1)

            if is_last_phase:
                mid_prefix = '    └──' if is_last_mid else '    ├──'
            else:
                mid_prefix = '│   └──' if is_last_mid else '│   ├──'

            mid_tasks = phases[phase][mid]
            task_count = len(mid_tasks)
            lines.append(f'{mid_prefix} {mid} ({task_count})')

            for k, task in enumerate(mid_tasks):
                is_last_task = (k == len(mid_tasks) - 1)

                # Calculate task prefix based on tree structure
                if is_last_phase:
                    if is_last_mid:
                        task_prefix = '        └──' if is_last_task else '        ├──'
                    else:
                        task_prefix = '    │   └──' if is_last_task else '    │   ├──'
                else:
                    if is_last_mid:
                        task_prefix = '│       └──' if is_last_task else '│       ├──'
                    else:
                        task_prefix = '│   │   └──' if is_last_task else '│   │   ├──'

                status_icon = '完了' if task['status'] == 'completed' else '進行中' if task['status'] == 'in_progress' else '未着手'

                # Add dates and weight
                start = task.get('start_date', 'N/A')
                end = task.get('end_date', 'N/A')
                weight = task.get('weight', 0)

                # Format: [status] title (MM/DD〜MM/DD, W=n)
                start_short = start[5:] if start != 'N/A' else 'N/A'  # MM-DD
                end_short = end[5:] if end != 'N/A' else 'N/A'

                lines.append(f'{task_prefix} [{status_icon}] {task["title"]} ({start_short}〜{end_short}, W={weight})')

    return '\n'.join(lines)


def generate_task_review():
    """タスクレビュードキュメントを生成"""
    root_dir = Path(__file__).parent.parent
    tasks_file = root_dir / 'tasks.json'

    # Load tasks.json
    with open(tasks_file, 'r') as f:
        data = json.load(f)

    tasks = data['tasks']

    # Calculate stats
    total_tasks = len(tasks)
    completed = sum(1 for t in tasks if t['status'] == 'completed')
    total_weight = sum(t['weight'] for t in tasks)
    completed_weight = sum(t['weight'] for t in tasks if t['status'] == 'completed')

    # Phase stats
    phases_stats = {}
    for task in tasks:
        phase = task.get('phase', 'Unknown')
        if phase not in phases_stats:
            phases_stats[phase] = {'total': 0, 'completed': 0, 'weight': 0, 'completed_weight': 0}

        phases_stats[phase]['total'] += 1
        phases_stats[phase]['weight'] += task['weight']
        if task['status'] == 'completed':
            phases_stats[phase]['completed'] += 1
            phases_stats[phase]['completed_weight'] += task['weight']

    # Mid-category stats
    mid_stats = {}
    for task in tasks:
        mid = task.get('midCategory', 'その他')
        if mid not in mid_stats:
            mid_stats[mid] = {'total': 0, 'completed': 0, 'weight': 0, 'completed_weight': 0, 'phase': task.get('phase', '')}

        mid_stats[mid]['total'] += 1
        mid_stats[mid]['weight'] += task['weight']
        if task['status'] == 'completed':
            mid_stats[mid]['completed'] += 1
            mid_stats[mid]['completed_weight'] += task['weight']

    # Generate TASK_REVIEW.md
    output = []
    output.append('# プロジェクト全タスク一覧')
    output.append('')
    output.append(f'**プロジェクト名**: {data["project"]["name"]}')
    output.append(f'**期間**: {data["project"]["startDate"]} 〜 {data["project"]["estimatedEndDate"]}')
    output.append(f'**総重み**: {total_weight}')
    output.append('')
    output.append('## サマリー')
    output.append('')
    output.append(f'- 総タスク数: {total_tasks}件')
    output.append(f'- 完了タスク数: {completed}件 ({completed/total_tasks*100:.1f}%)')
    output.append(f'- 総重み: {total_weight}')
    output.append(f'- 完了重み: {completed_weight} ({completed_weight/total_weight*100:.1f}%)')
    output.append('')
    output.append('## プロジェクト構造（ASCIIツリー）')
    output.append('')
    output.append('```')
    output.append(create_ascii_tree(tasks, data['project']['name']))
    output.append('```')
    output.append('')
    output.append('---')
    output.append('')
    output.append('## 詳細タスク一覧（表形式）')
    output.append('')

    # Group tasks by phase
    for phase in sorted(phases_stats.keys()):
        stats = phases_stats[phase]
        output.append(f'### {phase}')
        output.append('')
        output.append(f'**進捗**: {stats["completed"]}/{stats["total"]}タスク ({stats["completed"]/stats["total"]*100:.1f}%), 重み{stats["completed_weight"]}/{stats["weight"]} ({stats["completed_weight"]/stats["weight"]*100:.1f}%)')
        output.append('')

        # Group by midCategory within phase
        phase_tasks = [t for t in tasks if t.get('phase') == phase]
        mids = {}
        for t in phase_tasks:
            mid = t.get('midCategory', 'その他')
            if mid not in mids:
                mids[mid] = []
            mids[mid].append(t)

        for mid in sorted(mids.keys()):
            mid_tasks = mids[mid]
            mid_stat = mid_stats[mid]

            output.append(f'#### 中カテゴリ: {mid}')
            output.append('')
            output.append(f'**進捗**: {mid_stat["completed"]}/{mid_stat["total"]}タスク, 重み{mid_stat["completed_weight"]}/{mid_stat["weight"]}')
            output.append('')
            output.append('| ID | タスク名 | 開始日 | 終了日 | 重み | ステータス |')
            output.append('|-------|---------|--------|--------|------|-----------|')

            for task in mid_tasks:
                status_text = '✅ 完了' if task['status'] == 'completed' else '🔄 進行中' if task['status'] == 'in_progress' else '⬜ 未着手'
                output.append(f'| {task["id"]} | {task["title"]} | {task.get("start_date", "")} | {task.get("end_date", "")} | {task["weight"]} | {status_text} |')

            output.append('')

        output.append('---')
        output.append('')

    # Write to file
    output_file = root_dir / 'docs' / 'TASK_REVIEW.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f'✓ Generated {output_file}')


if __name__ == '__main__':
    generate_task_review()
