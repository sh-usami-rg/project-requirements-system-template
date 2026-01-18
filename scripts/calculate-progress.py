#!/usr/bin/env python3
"""
進捗可視化スクリプト - EVM方式で進捗を計算してREADME.mdに埋め込む

このスクリプトは以下を実行します：
1. tasks.jsonから進捗データを読み込み
2. EVM方式で進捗率を計算（PV, EV, AC, SPI, CPI）
3. README.mdに進捗バッジとサマリーを自動埋め込み
4. Phase別、中カテゴリ別の進捗も計算

使い方:
    python3 scripts/calculate-progress.py

EVMの指標:
- PV (Planned Value): 予定出来高（予定通りの進捗）
- EV (Earned Value): 実績出来高（実際の進捗）
- AC (Actual Cost): 実コスト（実際の工数）
- SPI (Schedule Performance Index): スケジュール効率指数 = EV / PV
- CPI (Cost Performance Index): コスト効率指数 = EV / AC
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

def load_tasks() -> Dict:
    """tasks.jsonを読み込む"""
    with open('tasks.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_pv(task: Dict, current_date: datetime, start_date: datetime, end_date: datetime) -> float:
    """
    Planned Value (予定出来高) を計算

    現在日が開始日〜終了日の範囲内なら、経過日数に応じて線形に増加
    """
    if current_date < start_date:
        return 0.0
    elif current_date >= end_date:
        return task.get('weight', 0)
    else:
        total_days = (end_date - start_date).days
        elapsed_days = (current_date - start_date).days
        if total_days == 0:
            return task.get('weight', 0)
        return task.get('weight', 0) * (elapsed_days / total_days)

def calculate_ev(task: Dict) -> float:
    """
    Earned Value (実績出来高) を計算

    ステータスに応じた完了率を適用
    """
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

def calculate_ac(task: Dict) -> float:
    """
    Actual Cost (実コスト) を計算

    実工数が記録されていればそれを使用、なければ見積工数を使用
    """
    actual_hours = task.get('actualHours', task.get('actual_hours', None))
    if actual_hours is not None:
        return actual_hours

    # 実工数が無い場合、ステータスに応じて見積工数を使用
    status = task.get('status', 'pending')
    estimated_hours = task.get('effortHours', task.get('estimatedHours', task.get('estimated_hours', 0)))

    if status in ['done', 'completed']:
        return estimated_hours
    elif status == 'in_progress':
        return estimated_hours * 0.5
    else:
        return 0.0

def calculate_overall_progress(data: Dict) -> Dict:
    """
    全体の進捗を計算

    Returns:
        {
            'total_weight': 総ウェイト,
            'pv': 予定出来高,
            'ev': 実績出来高,
            'ac': 実コスト,
            'spi': スケジュール効率指数,
            'cpi': コスト効率指数,
            'progress_rate': 進捗率 (%),
            'completion_rate': 完了率 (%)
        }
    """
    tasks = data.get('tasks', [])
    project = data.get('project', {})

    current_date = datetime.now()

    total_weight = sum(task.get('weight', 0) for task in tasks)
    total_pv = 0.0
    total_ev = 0.0
    total_ac = 0.0

    for task in tasks:
        # 日付をパース
        start_date_str = task.get('start_date') or task.get('startDate')
        end_date_str = task.get('end_date') or task.get('endDate')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

            total_pv += calculate_pv(task, current_date, start_date, end_date)

        total_ev += calculate_ev(task)
        total_ac += calculate_ac(task)

    # SPI, CPIの計算
    spi = total_ev / total_pv if total_pv > 0 else 0.0
    cpi = total_ev / total_ac if total_ac > 0 else 0.0

    # 進捗率と完了率
    progress_rate = (total_ev / total_weight * 100) if total_weight > 0 else 0.0
    completion_rate = (total_pv / total_weight * 100) if total_weight > 0 else 0.0

    return {
        'total_weight': total_weight,
        'pv': total_pv,
        'ev': total_ev,
        'ac': total_ac,
        'spi': spi,
        'cpi': cpi,
        'progress_rate': progress_rate,
        'completion_rate': completion_rate,
        'current_date': current_date.strftime('%Y-%m-%d')
    }

def calculate_phase_progress(data: Dict) -> Dict[str, Dict]:
    """Phase別の進捗を計算"""
    tasks = data.get('tasks', [])
    phases = {}
    current_date = datetime.now()

    for task in tasks:
        phase = task.get('phase', 'Unknown')
        if phase not in phases:
            phases[phase] = {
                'tasks': [],
                'total_weight': 0,
                'pv': 0.0,
                'ev': 0.0,
                'ac': 0.0
            }

        phases[phase]['tasks'].append(task)
        phases[phase]['total_weight'] += task.get('weight', 0)

        # 日付をパース
        start_date_str = task.get('start_date') or task.get('startDate')
        end_date_str = task.get('end_date') or task.get('endDate')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            phases[phase]['pv'] += calculate_pv(task, current_date, start_date, end_date)

        phases[phase]['ev'] += calculate_ev(task)
        phases[phase]['ac'] += calculate_ac(task)

    # SPI, CPI, 進捗率を計算
    for phase, stats in phases.items():
        stats['spi'] = stats['ev'] / stats['pv'] if stats['pv'] > 0 else 0.0
        stats['cpi'] = stats['ev'] / stats['ac'] if stats['ac'] > 0 else 0.0
        stats['progress_rate'] = (stats['ev'] / stats['total_weight'] * 100) if stats['total_weight'] > 0 else 0.0
        del stats['tasks']  # タスクリストは不要なので削除

    return phases

def calculate_mid_category_progress(data: Dict) -> Dict[str, Dict]:
    """中カテゴリ別の進捗を計算"""
    tasks = data.get('tasks', [])
    mid_categories = {}
    current_date = datetime.now()

    for task in tasks:
        mid_cat = task.get('midCategory', 'その他')
        if mid_cat not in mid_categories:
            mid_categories[mid_cat] = {
                'tasks': [],
                'total_weight': 0,
                'pv': 0.0,
                'ev': 0.0,
                'ac': 0.0
            }

        mid_categories[mid_cat]['tasks'].append(task)
        mid_categories[mid_cat]['total_weight'] += task.get('weight', 0)

        # 日付をパース
        start_date_str = task.get('start_date') or task.get('startDate')
        end_date_str = task.get('end_date') or task.get('endDate')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            mid_categories[mid_cat]['pv'] += calculate_pv(task, current_date, start_date, end_date)

        mid_categories[mid_cat]['ev'] += calculate_ev(task)
        mid_categories[mid_cat]['ac'] += calculate_ac(task)

    # SPI, CPI, 進捗率を計算
    for mid_cat, stats in mid_categories.items():
        stats['spi'] = stats['ev'] / stats['pv'] if stats['pv'] > 0 else 0.0
        stats['cpi'] = stats['ev'] / stats['ac'] if stats['ac'] > 0 else 0.0
        stats['progress_rate'] = (stats['ev'] / stats['total_weight'] * 100) if stats['total_weight'] > 0 else 0.0
        del stats['tasks']  # タスクリストは不要なので削除

    return mid_categories

def generate_progress_badge(progress_rate: float) -> str:
    """
    進捗率に応じたバッジを生成

    Args:
        progress_rate: 進捗率 (0-100)

    Returns:
        Markdown形式のバッジ
    """
    color = 'red'
    if progress_rate >= 80:
        color = 'brightgreen'
    elif progress_rate >= 60:
        color = 'green'
    elif progress_rate >= 40:
        color = 'yellow'
    elif progress_rate >= 20:
        color = 'orange'

    return f"![Progress](https://img.shields.io/badge/progress-{progress_rate:.1f}%25-{color})"

def generate_spi_badge(spi: float) -> str:
    """SPIバッジを生成"""
    color = 'red'
    if spi >= 1.0:
        color = 'brightgreen'
    elif spi >= 0.9:
        color = 'green'
    elif spi >= 0.8:
        color = 'yellow'
    elif spi >= 0.7:
        color = 'orange'

    return f"![SPI](https://img.shields.io/badge/SPI-{spi:.2f}-{color})"

def generate_cpi_badge(cpi: float) -> str:
    """CPIバッジを生成"""
    color = 'red'
    if cpi >= 1.0:
        color = 'brightgreen'
    elif cpi >= 0.9:
        color = 'green'
    elif cpi >= 0.8:
        color = 'yellow'
    elif cpi >= 0.7:
        color = 'orange'

    return f"![CPI](https://img.shields.io/badge/CPI-{cpi:.2f}-{color})"

def update_readme(overall: Dict, phases: Dict, mid_categories: Dict, project_name: str):
    """README.mdに進捗情報を埋め込む"""

    if not os.path.exists('README.md'):
        print("README.md が見つかりません。スキップします。")
        return

    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # 進捗セクションのマーカー
    start_marker = "<!-- PROGRESS_START -->"
    end_marker = "<!-- PROGRESS_END -->"

    # 進捗セクションの内容を生成
    progress_section = f"""{start_marker}

## 📊 プロジェクト進捗状況

**更新日時**: {overall['current_date']}

### 全体進捗

{generate_progress_badge(overall['progress_rate'])} {generate_spi_badge(overall['spi'])} {generate_cpi_badge(overall['cpi'])}

| 指標 | 値 | 説明 |
|------|-----|------|
| **進捗率** | {overall['progress_rate']:.1f}% | 完了したタスクのウェイト割合 |
| **PV (予定出来高)** | {overall['pv']:.1f} | スケジュール通りの進捗 |
| **EV (実績出来高)** | {overall['ev']:.1f} | 実際の進捗 |
| **SPI (スケジュール効率)** | {overall['spi']:.2f} | 1.0以上で予定より進んでいる |
| **CPI (コスト効率)** | {overall['cpi']:.2f} | 1.0以上で予算内で進んでいる |

### Phase別進捗

| Phase | 進捗率 | SPI | CPI | ステータス |
|-------|--------|-----|-----|-----------|
"""

    for phase, stats in sorted(phases.items()):
        status_emoji = "✅" if stats['progress_rate'] >= 100 else "🔄" if stats['progress_rate'] >= 50 else "📝"
        progress_section += f"| {phase} | {stats['progress_rate']:.1f}% | {stats['spi']:.2f} | {stats['cpi']:.2f} | {status_emoji} |\n"

    progress_section += "\n### 中カテゴリ別進捗\n\n| 中カテゴリ | 進捗率 | SPI | CPI | ステータス |\n|-----------|--------|-----|-----|-----------|\n"

    for mid_cat, stats in sorted(mid_categories.items()):
        status_emoji = "✅" if stats['progress_rate'] >= 100 else "🔄" if stats['progress_rate'] >= 50 else "📝"
        progress_section += f"| {mid_cat} | {stats['progress_rate']:.1f}% | {stats['spi']:.2f} | {stats['cpi']:.2f} | {status_emoji} |\n"

    progress_section += f"\n{end_marker}"

    # 既存の進捗セクションを置換、存在しない場合は追加
    if start_marker in content and end_marker in content:
        pattern = re.compile(f"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
        content = pattern.sub(progress_section, content)
    else:
        # タイトルの後に挿入
        lines = content.split('\n')
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith('# '):
                insert_index = i + 1
                break

        lines.insert(insert_index, '\n' + progress_section + '\n')
        content = '\n'.join(lines)

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ README.mdに進捗情報を更新しました")

def main():
    """メイン処理"""
    print("📊 進捗計算を開始します...")

    # tasks.jsonを読み込み
    data = load_tasks()
    project_name = data.get('project', {}).get('name', 'Unknown Project')

    # 進捗を計算
    overall = calculate_overall_progress(data)
    phases = calculate_phase_progress(data)
    mid_categories = calculate_mid_category_progress(data)

    # 結果を表示
    print(f"\n【{project_name}】")
    print(f"全体進捗率: {overall['progress_rate']:.1f}%")
    print(f"SPI: {overall['spi']:.2f} (スケジュール効率)")
    print(f"CPI: {overall['cpi']:.2f} (コスト効率)")

    print("\nPhase別進捗:")
    for phase, stats in sorted(phases.items()):
        print(f"  {phase}: {stats['progress_rate']:.1f}% (SPI: {stats['spi']:.2f}, CPI: {stats['cpi']:.2f})")

    print("\n中カテゴリ別進捗:")
    for mid_cat, stats in sorted(mid_categories.items()):
        print(f"  {mid_cat}: {stats['progress_rate']:.1f}% (SPI: {stats['spi']:.2f}, CPI: {stats['cpi']:.2f})")

    # README.mdを更新
    update_readme(overall, phases, mid_categories, project_name)

    print("\n✅ 進捗計算が完了しました")

if __name__ == '__main__':
    main()
