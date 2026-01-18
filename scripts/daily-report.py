#!/usr/bin/env python3
"""
日次進捗レポート生成スクリプト

このスクリプトは以下を実行します：
1. tasks.jsonから進捗データを読み込み
2. EVM方式で進捗率を計算
3. 日次レポートをMarkdown形式で生成
4. GitHub IssueまたはSlackに投稿（オプション）

使い方:
    # 標準出力に出力
    python3 scripts/daily-report.py

    # ファイルに出力
    python3 scripts/daily-report.py --output daily-report.md

    # GitHub Issueに投稿
    python3 scripts/daily-report.py --github --issue-number 1

環境変数:
    GITHUB_REPOSITORY: GitHubリポジトリ (例: owner/repo)
    GITHUB_TOKEN: GitHub Personal Access Token
"""

import json
import os
import sys
import argparse
import subprocess
from datetime import datetime, timedelta
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

def calculate_ev(task: Dict) -> float:
    """Earned Value (実績出来高) を計算"""
    status = task.get('status', 'pending')
    weight = task.get('weight', 0)

    status_completion = {
        'done': 1.0,
        'completed': 1.0,
        'in_progress': 0.5,
        'pending': 0.0,
        'not_started': 0.0,
        'blocked': 0.0,
        'cancelled': 0.0
    }

    return weight * status_completion.get(status, 0.0)

def calculate_progress(data: Dict) -> Dict:
    """進捗を計算"""
    tasks = data.get('tasks', [])
    total_weight = sum(task.get('weight', 0) for task in tasks)
    total_ev = sum(calculate_ev(task) for task in tasks)

    progress_rate = (total_ev / total_weight * 100) if total_weight > 0 else 0.0

    # ステータス別カウント
    status_count = {
        'completed': 0,
        'in_progress': 0,
        'pending': 0,
        'blocked': 0
    }

    for task in tasks:
        status = task.get('status', 'pending')
        if status in ['done', 'completed']:
            status_count['completed'] += 1
        elif status == 'in_progress':
            status_count['in_progress'] += 1
        elif status in ['pending', 'not_started']:
            status_count['pending'] += 1
        elif status == 'blocked':
            status_count['blocked'] += 1

    return {
        'total_tasks': len(tasks),
        'progress_rate': progress_rate,
        'status_count': status_count
    }

def get_tasks_by_status(tasks: List[Dict], status_list: List[str]) -> List[Dict]:
    """指定されたステータスのタスクを取得"""
    return [task for task in tasks if task.get('status') in status_list]

def get_today_tasks(tasks: List[Dict]) -> List[Dict]:
    """今日が開始日または終了日のタスクを取得"""
    today = datetime.now().date()
    today_tasks = []

    for task in tasks:
        start_date_str = task.get('start_date') or task.get('startDate')
        end_date_str = task.get('end_date') or task.get('endDate')

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            if start_date == today:
                today_tasks.append(task)
                continue

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            if end_date == today:
                today_tasks.append(task)

    return today_tasks

def generate_report(data: Dict) -> str:
    """日次レポートを生成"""
    project = data.get('project', {})
    tasks = data.get('tasks', [])

    project_name = project.get('name', 'Unknown Project')
    today = datetime.now()

    # 進捗計算
    stats = calculate_progress(data)

    # レポート生成
    report = f"""# 📊 日次進捗レポート - {project_name}

**日付**: {today.strftime('%Y年%m月%d日 (%A)')}

---

## 📈 全体進捗

- **進捗率**: {stats['progress_rate']:.1f}%
- **総タスク数**: {stats['total_tasks']}
  - ✅ 完了: {stats['status_count']['completed']}
  - 🔄 進行中: {stats['status_count']['in_progress']}
  - 📝 未着手: {stats['status_count']['pending']}
  - 🚫 ブロック: {stats['status_count']['blocked']}

進捗バー: """

    # 進捗バーを生成
    progress_bar_length = 20
    filled_length = int(stats['progress_rate'] / 100 * progress_bar_length)
    bar = '█' * filled_length + '░' * (progress_bar_length - filled_length)
    report += f"`{bar}` {stats['progress_rate']:.1f}%\n\n"

    report += "---\n\n"

    # 今日のタスク
    today_tasks = get_today_tasks(tasks)
    if today_tasks:
        report += "## 🎯 本日のタスク\n\n"
        for task in today_tasks:
            task_id = task.get('id', 'N/A')
            title = task.get('title', task.get('name', 'Unnamed'))
            status = task.get('status', 'pending')
            status_emoji = get_status_emoji(status)
            report += f"- {status_emoji} **[{task_id}]** {title}\n"
        report += "\n---\n\n"

    # 進行中のタスク
    in_progress_tasks = get_tasks_by_status(tasks, ['in_progress'])
    if in_progress_tasks:
        report += "## 🔄 進行中のタスク\n\n"
        for task in in_progress_tasks:
            task_id = task.get('id', 'N/A')
            title = task.get('title', task.get('name', 'Unnamed'))
            assignee = task.get('assignee', '未割当')
            phase = task.get('phase', 'N/A')
            mid_cat = task.get('midCategory', 'N/A')
            report += f"- **[{task_id}]** {title}\n"
            report += f"  - Phase: {phase} / 中カテゴリ: {mid_cat}\n"
            report += f"  - 担当: {assignee}\n"
        report += "\n---\n\n"

    # ブロックされているタスク
    blocked_tasks = get_tasks_by_status(tasks, ['blocked'])
    if blocked_tasks:
        report += "## 🚫 ブロック中のタスク\n\n"
        for task in blocked_tasks:
            task_id = task.get('id', 'N/A')
            title = task.get('title', task.get('name', 'Unnamed'))
            report += f"- **[{task_id}]** {title}\n"
        report += "\n---\n\n"

    # 完了したタスク（直近5件）
    completed_tasks = get_tasks_by_status(tasks, ['done', 'completed'])
    if completed_tasks:
        report += "## ✅ 最近完了したタスク（直近5件）\n\n"
        for task in completed_tasks[-5:]:
            task_id = task.get('id', 'N/A')
            title = task.get('title', task.get('name', 'Unnamed'))
            report += f"- **[{task_id}]** {title}\n"
        report += "\n---\n\n"

    # Phase別進捗
    phase_stats = {}
    for task in tasks:
        phase = task.get('phase', 'Unknown')
        if phase not in phase_stats:
            phase_stats[phase] = {'total': 0, 'completed': 0}

        phase_stats[phase]['total'] += 1
        if task.get('status') in ['done', 'completed']:
            phase_stats[phase]['completed'] += 1

    report += "## 📊 Phase別進捗\n\n"
    report += "| Phase | 完了 | 総数 | 進捗率 |\n"
    report += "|-------|------|------|--------|\n"

    for phase in sorted(phase_stats.keys()):
        stats = phase_stats[phase]
        completion_rate = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        report += f"| {phase} | {stats['completed']} | {stats['total']} | {completion_rate:.1f}% |\n"

    report += "\n---\n\n"

    # フッター
    report += f"*自動生成: {today.strftime('%Y-%m-%d %H:%M:%S')}*\n"

    return report

def post_to_github_issue(report: str, issue_number: int):
    """GitHub Issueにレポートを投稿"""
    repo = os.environ.get('GITHUB_REPOSITORY')
    if not repo:
        print("エラー: GITHUB_REPOSITORY 環境変数が設定されていません", file=sys.stderr)
        sys.exit(1)

    # gh CLI を使用してコメントを投稿
    cmd = [
        'gh', 'issue', 'comment', str(issue_number),
        '--repo', repo,
        '--body', report
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ GitHub Issue #{issue_number} にレポートを投稿しました")
        print(f"URL: https://github.com/{repo}/issues/{issue_number}")
    except subprocess.CalledProcessError as e:
        print(f"エラー: GitHub Issueへの投稿に失敗しました", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='日次進捗レポートを生成')
    parser.add_argument('--output', '-o', help='出力ファイル名')
    parser.add_argument('--github', action='store_true', help='GitHub Issueに投稿')
    parser.add_argument('--issue-number', type=int, help='GitHub Issue番号')

    args = parser.parse_args()

    # tasks.jsonを読み込み
    data = load_tasks()

    # レポートを生成
    report = generate_report(data)

    # 出力
    if args.github:
        if not args.issue_number:
            print("エラー: --github を使用する場合は --issue-number を指定してください", file=sys.stderr)
            sys.exit(1)
        post_to_github_issue(report, args.issue_number)
    elif args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ レポートを {args.output} に出力しました")
    else:
        print(report)

if __name__ == '__main__':
    main()
