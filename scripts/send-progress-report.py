#!/usr/bin/env python3
"""
週次進捗レポート生成・送信スクリプト

このスクリプトは tasks.json と schedule.json を読み込み、
プロジェクトの進捗率を計算して、メールでレポートを送信します。

環境変数:
    SENDGRID_API_KEY: SendGrid APIキー
    REPORT_TO_EMAIL: 送信先メールアドレス（カンマ区切りで複数指定可）
    REPORT_FROM_EMAIL: 送信元メールアドレス

使用方法:
    python scripts/send-progress-report.py
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, To
except ImportError:
    print("ERROR: sendgrid package not installed. Run: pip install sendgrid")
    sys.exit(1)


class ProgressReportGenerator:
    """進捗レポート生成クラス"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.tasks_file = base_dir / "tasks.json"
        self.schedule_file = base_dir / "schedule.json"

        # JSONファイルを読み込む
        self.tasks_data = self._load_json(self.tasks_file)
        self.schedule_data = self._load_json(self.schedule_file)

        # プロジェクト情報
        self.project_name = self.tasks_data["project"]["name"]
        self.start_date = datetime.strptime(
            self.tasks_data["project"]["startDate"], "%Y-%m-%d"
        )
        self.end_date = datetime.strptime(
            self.tasks_data["project"]["estimatedEndDate"], "%Y-%m-%d"
        )

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

    def get_current_week(self) -> Tuple[int, Dict]:
        """
        現在の週番号と週情報を取得

        Returns:
            Tuple[int, Dict]: (週番号, 週情報辞書)
        """
        today = datetime.now()

        # プロジェクト開始前
        if today < self.start_date:
            return 0, self.schedule_data["weeklySchedule"][0]

        # プロジェクト終了後
        if today > self.end_date:
            last_week = len(self.schedule_data["weeklySchedule"])
            return last_week, self.schedule_data["weeklySchedule"][-1]

        # 現在の週を計算
        days_since_start = (today - self.start_date).days
        week_number = (days_since_start // 7) + 1

        # 週番号が範囲内か確認
        total_weeks = len(self.schedule_data["weeklySchedule"])
        if week_number > total_weeks:
            week_number = total_weeks

        week_info = self.schedule_data["weeklySchedule"][week_number - 1]
        return week_number, week_info

    def calculate_actual_progress(self) -> int:
        """
        実績進捗率を計算（完了タスクのWeight合計）

        Returns:
            int: 実績進捗率（0-100）
        """
        completed_weight = sum(
            task["weight"]
            for task in self.tasks_data["tasks"]
            if task["status"] == "done"
        )
        return completed_weight

    def get_status(self, actual: int, planned: int) -> Tuple[str, str]:
        """
        進捗ステータスを判定

        Args:
            actual: 実績進捗率
            planned: 予定進捗率

        Returns:
            Tuple[str, str]: (ステータス文字列, 色コード)
        """
        diff = actual - planned

        if actual >= planned:
            return "🟢 予定通り", "#28a745"
        elif diff >= -5:
            return "🟡 やや遅延", "#ffc107"
        else:
            return "🔴 要注意", "#dc3545"

    def get_tasks_by_status(self) -> Dict[str, List[Dict]]:
        """
        ステータス別にタスクを分類

        Returns:
            Dict[str, List[Dict]]: ステータス別タスクリスト
        """
        tasks_by_status = {
            "done": [],
            "in_progress": [],
            "pending": []
        }

        for task in self.tasks_data["tasks"]:
            status = task["status"]
            if status in tasks_by_status:
                tasks_by_status[status].append(task)

        return tasks_by_status

    def get_weekly_tasks(self, week_number: int) -> Dict[str, List[Dict]]:
        """
        指定週のタスク情報を取得

        Args:
            week_number: 週番号（1-12）

        Returns:
            Dict: 今週・来週のタスク情報
        """
        # 今週のタスクID
        current_week_info = self.schedule_data["weeklySchedule"][week_number - 1]
        current_week_task_ids = current_week_info["tasks"]

        # 来週のタスクID
        next_week_task_ids = []
        if week_number < len(self.schedule_data["weeklySchedule"]):
            next_week_info = self.schedule_data["weeklySchedule"][week_number]
            next_week_task_ids = next_week_info["tasks"]

        # タスクIDから詳細情報を取得
        all_tasks = {task["id"]: task for task in self.tasks_data["tasks"]}

        current_week_tasks = [
            all_tasks[task_id] for task_id in current_week_task_ids
            if task_id in all_tasks
        ]

        next_week_tasks = [
            all_tasks[task_id] for task_id in next_week_task_ids
            if task_id in all_tasks
        ]

        return {
            "current": current_week_tasks,
            "next": next_week_tasks
        }

    def generate_html_report(
        self,
        week_number: int,
        week_info: Dict,
        actual_progress: int,
        planned_progress: int
    ) -> str:
        """
        HTML形式の進捗レポートを生成

        Args:
            week_number: 週番号
            week_info: 週情報
            actual_progress: 実績進捗率
            planned_progress: 予定進捗率

        Returns:
            str: HTML形式のレポート
        """
        status, status_color = self.get_status(actual_progress, planned_progress)
        diff = actual_progress - planned_progress
        diff_sign = "+" if diff >= 0 else ""

        tasks_by_status = self.get_tasks_by_status()
        weekly_tasks = self.get_weekly_tasks(week_number)

        # 今週完了したタスク（今週予定で完了済み）
        completed_this_week = [
            task for task in weekly_tasks["current"]
            if task["status"] == "done"
        ]

        # 進行中のタスク
        in_progress_tasks = tasks_by_status["in_progress"]

        # 来週予定のタスク
        next_week_tasks = weekly_tasks["next"]

        # HTMLテンプレート
        html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h2 {{
            color: #0366d6;
            border-bottom: 2px solid #0366d6;
            padding-bottom: 10px;
        }}
        h3 {{
            color: #24292e;
            margin-top: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: #fff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        table th, table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e1e4e8;
        }}
        table th {{
            background-color: #f6f8fa;
            font-weight: 600;
            width: 30%;
        }}
        .status {{
            font-size: 1.1em;
            font-weight: bold;
            color: {status_color};
        }}
        .diff {{
            font-weight: bold;
            color: {"#28a745" if diff >= 0 else "#dc3545"};
        }}
        ul {{
            list-style-type: none;
            padding: 0;
        }}
        li {{
            padding: 8px 0;
            border-bottom: 1px solid #e1e4e8;
        }}
        li:last-child {{
            border-bottom: none;
        }}
        .task-id {{
            display: inline-block;
            background: #0366d6;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: bold;
            margin-right: 8px;
        }}
        .task-weight {{
            display: inline-block;
            background: #6f42c1;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.85em;
            margin-left: 8px;
        }}
        .no-tasks {{
            color: #6a737d;
            font-style: italic;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e1e4e8;
            color: #6a737d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h2>📊 週次進捗レポート - Week {week_number}</h2>

    <table>
        <tr>
            <th>プロジェクト</th>
            <td>{self.project_name}</td>
        </tr>
        <tr>
            <th>期間</th>
            <td>{week_info['dateRange']}</td>
        </tr>
        <tr>
            <th>予定進捗率</th>
            <td>{planned_progress}%</td>
        </tr>
        <tr>
            <th>実績進捗率</th>
            <td>{actual_progress}%</td>
        </tr>
        <tr>
            <th>差分</th>
            <td class="diff">{diff_sign}{diff}%</td>
        </tr>
        <tr>
            <th>ステータス</th>
            <td class="status">{status}</td>
        </tr>
    </table>

    <h3>✅ 今週完了したタスク ({len(completed_this_week)}件)</h3>
    <ul>
"""

        if completed_this_week:
            for task in completed_this_week:
                html_content += f"""
        <li>
            <span class="task-id">{task['id']}</span>
            {task['title']}
            <span class="task-weight">Weight: {task['weight']}</span>
        </li>
"""
        else:
            html_content += """
        <li class="no-tasks">完了したタスクはありません</li>
"""

        html_content += f"""
    </ul>

    <h3>🔄 進行中のタスク ({len(in_progress_tasks)}件)</h3>
    <ul>
"""

        if in_progress_tasks:
            for task in in_progress_tasks:
                html_content += f"""
        <li>
            <span class="task-id">{task['id']}</span>
            {task['title']}
            <span class="task-weight">Weight: {task['weight']}</span>
        </li>
"""
        else:
            html_content += """
        <li class="no-tasks">進行中のタスクはありません</li>
"""

        html_content += f"""
    </ul>

    <h3>📅 来週予定のタスク ({len(next_week_tasks)}件)</h3>
    <ul>
"""

        if next_week_tasks:
            for task in next_week_tasks:
                html_content += f"""
        <li>
            <span class="task-id">{task['id']}</span>
            {task['title']}
            <span class="task-weight">Weight: {task['weight']}</span>
        </li>
"""
        else:
            html_content += """
        <li class="no-tasks">来週予定のタスクはありません（プロジェクト終了）</li>
"""

        html_content += f"""
    </ul>

    <div class="footer">
        <p>このレポートは自動生成されました。</p>
        <p>詳細は <a href="https://github.com/your-repo/project-requirements-system">プロジェクトリポジトリ</a> をご確認ください。</p>
        <p>生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""

        return html_content


def send_email(from_email: str, to_emails: List[str], subject: str, html_content: str):
    """
    SendGrid APIを使用してメールを送信

    Args:
        from_email: 送信元メールアドレス
        to_emails: 送信先メールアドレスのリスト
        subject: メールの件名
        html_content: HTML形式のメール本文
    """
    api_key = os.environ.get("SENDGRID_API_KEY")
    if not api_key:
        print("ERROR: SENDGRID_API_KEY environment variable not set")
        sys.exit(1)

    try:
        # To オブジェクトのリストを作成
        to_list = [To(email.strip()) for email in to_emails]

        # メールオブジェクトを作成
        message = Mail(
            from_email=from_email,
            to_emails=to_list,
            subject=subject,
            html_content=html_content
        )

        # SendGrid APIクライアント
        sg = SendGridAPIClient(api_key)

        # メール送信
        response = sg.send(message)

        print(f"✅ Email sent successfully!")
        print(f"   Status code: {response.status_code}")
        print(f"   To: {', '.join(to_emails)}")

    except Exception as e:
        print(f"ERROR: Failed to send email: {e}")
        sys.exit(1)


def main():
    """メイン処理"""
    print("📊 週次進捗レポート生成開始")
    print("=" * 60)

    # 環境変数チェック
    required_env_vars = ["SENDGRID_API_KEY", "REPORT_TO_EMAIL", "REPORT_FROM_EMAIL"]
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"ERROR: Missing environment variables: {', '.join(missing_vars)}")
        print("\nRequired environment variables:")
        print("  SENDGRID_API_KEY: SendGrid API key")
        print("  REPORT_TO_EMAIL: Recipient email address(es), comma-separated")
        print("  REPORT_FROM_EMAIL: Sender email address")
        sys.exit(1)

    # プロジェクトディレクトリ
    base_dir = Path(__file__).parent.parent

    # レポート生成器を初期化
    generator = ProgressReportGenerator(base_dir)

    # 現在の週を取得
    week_number, week_info = generator.get_current_week()
    print(f"\n📅 現在の週: Week {week_number}")
    print(f"   期間: {week_info['dateRange']}")

    # 進捗率を計算
    actual_progress = generator.calculate_actual_progress()
    planned_progress = week_info["cumulativeProgress"]

    print(f"\n📈 進捗率:")
    print(f"   予定: {planned_progress}%")
    print(f"   実績: {actual_progress}%")

    status, _ = generator.get_status(actual_progress, planned_progress)
    print(f"   ステータス: {status}")

    # HTMLレポートを生成
    print(f"\n📝 HTMLレポート生成中...")
    html_content = generator.generate_html_report(
        week_number, week_info, actual_progress, planned_progress
    )

    # メール送信
    from_email = os.environ.get("REPORT_FROM_EMAIL")
    to_emails_str = os.environ.get("REPORT_TO_EMAIL")
    to_emails = [email.strip() for email in to_emails_str.split(",")]

    subject = f"[{generator.project_name}] 週次進捗レポート - Week {week_number}"

    print(f"\n📧 メール送信中...")
    send_email(from_email, to_emails, subject, html_content)

    print("\n" + "=" * 60)
    print("✅ 週次進捗レポート送信完了")


if __name__ == "__main__":
    main()
