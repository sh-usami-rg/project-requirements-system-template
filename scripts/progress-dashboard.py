#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDCA Progress Dashboard Generator

進捗ダッシュボードを生成するスクリプト
日次・週次・月次のレポート、遅延タスク警告、完了予測を提供
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse


class ProgressDashboard:
    """進捗ダッシュボード生成クラス"""

    def __init__(self, progress_file: str = "progress.json"):
        """
        初期化

        Args:
            progress_file: 進捗データファイルのパス
        """
        self.progress_file = Path(progress_file)
        self.data: Optional[Dict[str, Any]] = None
        self.today = datetime.now().date()

    def load_data(self) -> bool:
        """
        進捗データを読み込む

        Returns:
            読み込み成功したかどうか
        """
        if not self.progress_file.exists():
            print(f"エラー: {self.progress_file} が見つかりません", file=sys.stderr)
            return False

        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            return True
        except json.JSONDecodeError as e:
            print(f"エラー: JSONパースエラー: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"エラー: データ読み込み失敗: {e}", file=sys.stderr)
            return False

    def calculate_metrics(self) -> Dict[str, Any]:
        """
        各種メトリクスを計算

        Returns:
            計算されたメトリクス
        """
        if not self.data:
            return {}

        tasks = self.data.get("tasks", [])
        project = self.data.get("project", {})

        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.get("status") == "completed")
        in_progress_tasks = sum(1 for t in tasks if t.get("status") == "in_progress")
        not_started_tasks = sum(1 for t in tasks if t.get("status") == "not_started")
        blocked_tasks = sum(1 for t in tasks if t.get("status") == "blocked")

        # 進捗率計算
        total_progress = sum(t.get("progress", 0) for t in tasks)
        avg_progress = total_progress / total_tasks if total_tasks > 0 else 0

        # 工数計算
        total_estimated_hours = sum(t.get("estimatedHours", 0) for t in tasks)
        total_actual_hours = sum(t.get("actualHours", 0) for t in tasks)
        effort_efficiency = (total_actual_hours / total_estimated_hours * 100) if total_estimated_hours > 0 else 0

        # スケジュール計算
        start_date = datetime.strptime(project.get("startDate", ""), "%Y-%m-%d").date() if project.get("startDate") else self.today
        end_date = datetime.strptime(project.get("endDate", ""), "%Y-%m-%d").date() if project.get("endDate") else self.today
        total_days = (end_date - start_date).days
        elapsed_days = (self.today - start_date).days
        remaining_days = (end_date - self.today).days
        elapsed_ratio = (elapsed_days / total_days * 100) if total_days > 0 else 0

        # 遅延タスク検出
        delayed_tasks = []
        at_risk_tasks = []

        for task in tasks:
            if task.get("status") == "completed":
                continue

            planned_end = task.get("plannedEndDate")
            if not planned_end:
                continue

            planned_end_date = datetime.strptime(planned_end, "%Y-%m-%d").date()
            days_until_due = (planned_end_date - self.today).days
            task_progress = task.get("progress", 0)

            if planned_end_date < self.today:
                delayed_tasks.append({
                    "id": task.get("id"),
                    "name": task.get("name"),
                    "plannedEndDate": planned_end,
                    "daysDelayed": -days_until_due,
                    "progress": task_progress
                })
            elif days_until_due <= 3 and task_progress < 80:
                at_risk_tasks.append({
                    "id": task.get("id"),
                    "name": task.get("name"),
                    "plannedEndDate": planned_end,
                    "daysRemaining": days_until_due,
                    "progress": task_progress
                })

        # 完了予測日計算
        if elapsed_days > 0 and avg_progress > 0:
            velocity = avg_progress / elapsed_days
            days_to_complete = (100 - avg_progress) / velocity if velocity > 0 else 999
            predicted_end_date = self.today + timedelta(days=int(days_to_complete))
        else:
            predicted_end_date = end_date

        # 予定通り完了率
        completed_on_time = 0
        for task in tasks:
            if task.get("status") == "completed":
                actual_end = task.get("actualEndDate")
                planned_end = task.get("plannedEndDate")
                if actual_end and planned_end:
                    if datetime.strptime(actual_end, "%Y-%m-%d").date() <= datetime.strptime(planned_end, "%Y-%m-%d").date():
                        completed_on_time += 1

        on_time_rate = (completed_on_time / completed_tasks * 100) if completed_tasks > 0 else 0

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "not_started_tasks": not_started_tasks,
            "blocked_tasks": blocked_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "avg_progress": avg_progress,
            "total_estimated_hours": total_estimated_hours,
            "total_actual_hours": total_actual_hours,
            "effort_efficiency": effort_efficiency,
            "elapsed_days": elapsed_days,
            "remaining_days": remaining_days,
            "elapsed_ratio": elapsed_ratio,
            "predicted_end_date": predicted_end_date.strftime("%Y-%m-%d"),
            "on_time_rate": on_time_rate,
            "delayed_tasks": delayed_tasks,
            "at_risk_tasks": at_risk_tasks,
            "schedule_health": "健全" if avg_progress >= elapsed_ratio else "遅延" if avg_progress < elapsed_ratio - 10 else "要注意"
        }

    def generate_daily_report(self) -> str:
        """
        日次レポートを生成

        Returns:
            Markdown形式のレポート
        """
        metrics = self.calculate_metrics()
        project = self.data.get("project", {})

        report = f"""# 進捗ダッシュボード（日次）
**日付**: {self.today.strftime("%Y年%m月%d日")}
**プロジェクト**: {project.get("name", "未設定")}

## サマリー

| 項目 | 値 |
|------|-----|
| 全体進捗率 | {metrics.get("avg_progress", 0):.1f}% |
| 完了タスク | {metrics.get("completed_tasks", 0)}/{metrics.get("total_tasks", 0)} ({metrics.get("completion_rate", 0):.1f}%) |
| 進行中タスク | {metrics.get("in_progress_tasks", 0)} |
| 未着手タスク | {metrics.get("not_started_tasks", 0)} |
| ブロック中タスク | {metrics.get("blocked_tasks", 0)} |
| スケジュール健全性 | {metrics.get("schedule_health", "不明")} |

## 進捗状況

```
進捗バー: [{"=" * int(metrics.get("avg_progress", 0) / 5)}{"." * (20 - int(metrics.get("avg_progress", 0) / 5))}] {metrics.get("avg_progress", 0):.1f}%
```

## 工数分析

| 項目 | 値 |
|------|-----|
| 見積工数 | {metrics.get("total_estimated_hours", 0):.1f}h |
| 実績工数 | {metrics.get("total_actual_hours", 0):.1f}h |
| 工数効率 | {metrics.get("effort_efficiency", 0):.1f}% |

## スケジュール

| 項目 | 値 |
|------|-----|
| 経過日数 | {metrics.get("elapsed_days", 0)}日 ({metrics.get("elapsed_ratio", 0):.1f}%) |
| 残り日数 | {metrics.get("remaining_days", 0)}日 |
| 完了予測日 | {metrics.get("predicted_end_date", "不明")} |
| 予定通り完了率 | {metrics.get("on_time_rate", 0):.1f}% |

"""

        # 警告セクション
        delayed = metrics.get("delayed_tasks", [])
        at_risk = metrics.get("at_risk_tasks", [])

        if delayed or at_risk:
            report += "## 警告\n\n"

        if delayed:
            report += f"### 遅延タスク ({len(delayed)}件)\n\n"
            for task in delayed:
                report += f"- **{task['id']}**: {task['name']}\n"
                report += f"  - 計画終了日: {task['plannedEndDate']}\n"
                report += f"  - 遅延日数: {task['daysDelayed']}日\n"
                report += f"  - 進捗率: {task['progress']}%\n\n"

        if at_risk:
            report += f"### 遅延リスク ({len(at_risk)}件)\n\n"
            for task in at_risk:
                report += f"- **{task['id']}**: {task['name']}\n"
                report += f"  - 計画終了日: {task['plannedEndDate']}\n"
                report += f"  - 残り日数: {task['daysRemaining']}日\n"
                report += f"  - 進捗率: {task['progress']}%\n\n"

        # 今日のタスク
        report += "## 今日のフォーカス\n\n"
        report += self._get_today_focus_tasks()

        return report

    def generate_weekly_report(self) -> str:
        """
        週次レポートを生成

        Returns:
            Markdown形式のレポート
        """
        metrics = self.calculate_metrics()
        project = self.data.get("project", {})

        week_start = self.today - timedelta(days=self.today.weekday())
        week_end = week_start + timedelta(days=6)

        # 今週完了したタスク
        weekly_completed = self._get_tasks_completed_in_period(week_start, week_end)

        report = f"""# 進捗ダッシュボード（週次）
**期間**: {week_start.strftime("%Y年%m月%d日")} - {week_end.strftime("%Y年%m月%d日")}
**プロジェクト**: {project.get("name", "未設定")}

## 週次サマリー

| 項目 | 値 |
|------|-----|
| 今週完了タスク | {len(weekly_completed)} |
| 全体進捗率 | {metrics.get("avg_progress", 0):.1f}% |
| スケジュール健全性 | {metrics.get("schedule_health", "不明")} |

## 今週の達成事項

"""

        if weekly_completed:
            for task in weekly_completed:
                report += f"- [{task['id']}] {task['name']}\n"
        else:
            report += "- なし\n"

        report += "\n## タスクステータス推移\n\n"
        report += self._get_status_distribution()

        report += "\n## 来週の予定\n\n"
        report += self._get_next_week_tasks()

        # PDCAサイクル
        recent_cycles = self._get_recent_pdca_cycles(7)
        if recent_cycles:
            report += "\n## 今週のPDCAサイクル\n\n"
            for cycle in recent_cycles:
                cycle_date = datetime.fromisoformat(cycle.get("date", "")).strftime("%Y-%m-%d")
                report += f"### {cycle.get('cycleId', '')} ({cycle_date})\n\n"

                check = cycle.get("check", {})
                report += f"- 進捗率: {check.get('progressRate', 0):.1f}%\n"
                report += f"- リスク評価: {check.get('riskAssessment', '不明')}\n"

                act = cycle.get("act", {})
                improvements = act.get("improvements", [])
                if improvements:
                    report += f"- 改善アクション: {len(improvements)}件\n"
                report += "\n"

        return report

    def generate_monthly_report(self) -> str:
        """
        月次レポートを生成

        Returns:
            Markdown形式のレポート
        """
        metrics = self.calculate_metrics()
        project = self.data.get("project", {})

        month_start = self.today.replace(day=1)
        if self.today.month == 12:
            month_end = month_start.replace(year=self.today.year + 1, month=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=self.today.month + 1) - timedelta(days=1)

        # 今月完了したタスク
        monthly_completed = self._get_tasks_completed_in_period(month_start, month_end)

        report = f"""# 進捗ダッシュボード（月次）
**期間**: {month_start.strftime("%Y年%m月")}
**プロジェクト**: {project.get("name", "未設定")}

## 月次サマリー

| 項目 | 値 |
|------|-----|
| 今月完了タスク | {len(monthly_completed)} |
| 全体進捗率 | {metrics.get("avg_progress", 0):.1f}% |
| 完了タスク合計 | {metrics.get("completed_tasks", 0)}/{metrics.get("total_tasks", 0)} |
| 工数効率 | {metrics.get("effort_efficiency", 0):.1f}% |

## 月間達成事項

"""

        if monthly_completed:
            for task in monthly_completed:
                report += f"- [{task['id']}] {task['name']} (完了日: {task.get('actualEndDate', '不明')})\n"
        else:
            report += "- なし\n"

        report += "\n## 品質メトリクス\n\n"
        report += self._get_quality_metrics()

        report += "\n## PDCAサイクル分析\n\n"
        monthly_cycles = self._get_recent_pdca_cycles(30)

        if monthly_cycles:
            report += f"- 実施回数: {len(monthly_cycles)}回\n"

            total_improvements = sum(len(c.get("act", {}).get("improvements", [])) for c in monthly_cycles)
            report += f"- 提案された改善アクション: {total_improvements}件\n"

            completed_improvements = sum(
                sum(1 for imp in c.get("act", {}).get("improvements", []) if imp.get("status") == "completed")
                for c in monthly_cycles
            )
            report += f"- 完了した改善アクション: {completed_improvements}件\n"

            report += "\n### 主な教訓\n\n"
            all_lessons = []
            for cycle in monthly_cycles:
                lessons = cycle.get("act", {}).get("lessonsLearned", [])
                all_lessons.extend(lessons)

            for i, lesson in enumerate(all_lessons[:5], 1):
                report += f"{i}. {lesson}\n"
        else:
            report += "- PDCAサイクルが実施されていません\n"

        report += "\n## トレンド分析\n\n"
        report += self._get_trend_analysis()

        return report

    def _get_today_focus_tasks(self) -> str:
        """今日フォーカスすべきタスクを取得"""
        tasks = self.data.get("tasks", [])
        focus_tasks = []

        for task in tasks:
            if task.get("status") in ["in_progress", "not_started"]:
                planned_end = task.get("plannedEndDate")
                if planned_end:
                    planned_end_date = datetime.strptime(planned_end, "%Y-%m-%d").date()
                    days_until_due = (planned_end_date - self.today).days

                    if days_until_due <= 1:
                        focus_tasks.append({
                            "task": task,
                            "priority": 1,
                            "reason": "期限当日または超過"
                        })
                    elif task.get("priority") == "critical":
                        focus_tasks.append({
                            "task": task,
                            "priority": 2,
                            "reason": "最優先タスク"
                        })
                    elif task.get("status") == "in_progress" and task.get("progress", 0) < 50:
                        focus_tasks.append({
                            "task": task,
                            "priority": 3,
                            "reason": "進捗が遅れている"
                        })

        focus_tasks.sort(key=lambda x: x["priority"])

        if not focus_tasks:
            return "- 特になし\n"

        result = ""
        for item in focus_tasks[:5]:
            task = item["task"]
            result += f"- **{task['id']}**: {task['name']}\n"
            result += f"  - 理由: {item['reason']}\n"
            result += f"  - 進捗: {task.get('progress', 0)}%\n"

        return result

    def _get_next_week_tasks(self) -> str:
        """来週開始予定のタスクを取得"""
        tasks = self.data.get("tasks", [])
        next_week_start = self.today + timedelta(days=(7 - self.today.weekday()))
        next_week_end = next_week_start + timedelta(days=6)

        next_week_tasks = []
        for task in tasks:
            planned_start = task.get("plannedStartDate")
            if planned_start:
                planned_start_date = datetime.strptime(planned_start, "%Y-%m-%d").date()
                if next_week_start <= planned_start_date <= next_week_end:
                    next_week_tasks.append(task)

        if not next_week_tasks:
            return "- なし\n"

        result = ""
        for task in next_week_tasks:
            result += f"- [{task['id']}] {task['name']} (開始予定: {task['plannedStartDate']})\n"

        return result

    def _get_tasks_completed_in_period(self, start_date, end_date) -> List[Dict]:
        """指定期間に完了したタスクを取得"""
        tasks = self.data.get("tasks", [])
        completed = []

        for task in tasks:
            if task.get("status") == "completed":
                actual_end = task.get("actualEndDate")
                if actual_end:
                    actual_end_date = datetime.strptime(actual_end, "%Y-%m-%d").date()
                    if start_date <= actual_end_date <= end_date:
                        completed.append(task)

        return completed

    def _get_recent_pdca_cycles(self, days: int) -> List[Dict]:
        """最近のPDCAサイクルを取得"""
        cycles = self.data.get("pdcaCycles", [])
        cutoff_date = self.today - timedelta(days=days)

        recent = []
        for cycle in cycles:
            cycle_date = datetime.fromisoformat(cycle.get("date", "")).date()
            if cycle_date >= cutoff_date:
                recent.append(cycle)

        return sorted(recent, key=lambda x: x.get("date", ""), reverse=True)

    def _get_status_distribution(self) -> str:
        """ステータス分布を取得"""
        tasks = self.data.get("tasks", [])
        total = len(tasks)

        if total == 0:
            return "タスクがありません\n"

        statuses = {
            "completed": "完了",
            "in_progress": "進行中",
            "not_started": "未着手",
            "blocked": "ブロック",
            "cancelled": "キャンセル"
        }

        result = "```\n"
        for status, label in statuses.items():
            count = sum(1 for t in tasks if t.get("status") == status)
            percentage = count / total * 100
            bar_length = int(percentage / 2)
            result += f"{label:10} | {'█' * bar_length}{' ' * (50 - bar_length)} | {count:3}/{total:3} ({percentage:5.1f}%)\n"
        result += "```\n"

        return result

    def _get_quality_metrics(self) -> str:
        """品質メトリクスを取得"""
        cycles = self.data.get("pdcaCycles", [])

        if not cycles:
            return "- データなし\n"

        total_defects = 0
        total_rework_hours = 0
        cycle_count = 0

        for cycle in cycles:
            check = cycle.get("check", {})
            quality = check.get("qualityMetrics", {})

            total_defects += quality.get("defectCount", 0)
            total_rework_hours += quality.get("reworkHours", 0)
            cycle_count += 1

        result = f"- 総不具合数: {total_defects}\n"
        result += f"- 総手戻り工数: {total_rework_hours:.1f}時間\n"

        if cycle_count > 0:
            result += f"- 平均不具合数（サイクルあたり）: {total_defects / cycle_count:.1f}\n"
            result += f"- 平均手戻り工数（サイクルあたり）: {total_rework_hours / cycle_count:.1f}時間\n"

        return result

    def _get_trend_analysis(self) -> str:
        """トレンド分析を取得"""
        cycles = self.data.get("pdcaCycles", [])

        if len(cycles) < 2:
            return "- 分析に十分なデータがありません（2サイクル以上必要）\n"

        # 最新3サイクルの進捗率推移
        recent_cycles = sorted(cycles, key=lambda x: x.get("date", ""), reverse=True)[:3]

        result = "### 進捗率推移\n\n"
        for cycle in reversed(recent_cycles):
            cycle_id = cycle.get("cycleId", "")
            progress = cycle.get("check", {}).get("progressRate", 0)
            result += f"- {cycle_id}: {progress:.1f}%\n"

        # トレンド判定
        if len(recent_cycles) >= 2:
            latest_progress = recent_cycles[0].get("check", {}).get("progressRate", 0)
            previous_progress = recent_cycles[1].get("check", {}).get("progressRate", 0)

            result += f"\n### トレンド評価\n\n"
            if latest_progress > previous_progress:
                result += "- 進捗は改善傾向にあります\n"
            elif latest_progress < previous_progress:
                result += "- 進捗が悪化しています。対策が必要です\n"
            else:
                result += "- 進捗は横ばいです\n"

        return result

    def export_dashboard(self, report_type: str, output_file: Optional[str] = None) -> bool:
        """
        ダッシュボードをファイルにエクスポート

        Args:
            report_type: レポートタイプ (daily/weekly/monthly)
            output_file: 出力ファイルパス（Noneの場合は標準出力）

        Returns:
            エクスポート成功したかどうか
        """
        if report_type == "daily":
            report = self.generate_daily_report()
        elif report_type == "weekly":
            report = self.generate_weekly_report()
        elif report_type == "monthly":
            report = self.generate_monthly_report()
        else:
            print(f"エラー: 不正なレポートタイプ: {report_type}", file=sys.stderr)
            return False

        if output_file:
            try:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report)

                print(f"ダッシュボードを {output_file} に出力しました")
                return True
            except Exception as e:
                print(f"エラー: ファイル出力失敗: {e}", file=sys.stderr)
                return False
        else:
            print(report)
            return True


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="PDCA進捗ダッシュボード生成ツール")
    parser.add_argument(
        "report_type",
        choices=["daily", "weekly", "monthly"],
        help="レポートタイプ"
    )
    parser.add_argument(
        "-f", "--file",
        default="progress.json",
        help="進捗データファイル（デフォルト: progress.json）"
    )
    parser.add_argument(
        "-o", "--output",
        help="出力ファイルパス（指定しない場合は標準出力）"
    )

    args = parser.parse_args()

    dashboard = ProgressDashboard(args.file)

    if not dashboard.load_data():
        sys.exit(1)

    if not dashboard.export_dashboard(args.report_type, args.output):
        sys.exit(1)


if __name__ == "__main__":
    main()
