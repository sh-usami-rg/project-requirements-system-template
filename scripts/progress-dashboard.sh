#!/bin/bash
# -*- coding: utf-8 -*-
#
# PDCA Progress Dashboard Generator (Shell Script版)
#
# 進捗ダッシュボードを生成するシェルスクリプト
# Pythonが利用できない環境でも動作可能
#

set -euo pipefail

# 設定
PROGRESS_FILE="${PROGRESS_FILE:-progress.json}"
REPORT_TYPE="${1:-daily}"
OUTPUT_FILE="${2:-}"

# 色設定
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# エラーメッセージ出力
error() {
    echo -e "${RED}エラー: $1${NC}" >&2
    exit 1
}

# 警告メッセージ出力
warning() {
    echo -e "${YELLOW}警告: $1${NC}" >&2
}

# 成功メッセージ出力
success() {
    echo -e "${GREEN}$1${NC}"
}

# 情報メッセージ出力
info() {
    echo -e "${BLUE}$1${NC}"
}

# jqの存在確認
check_dependencies() {
    if ! command -v jq &> /dev/null; then
        error "jq がインストールされていません。以下のコマンドでインストールしてください:
  Ubuntu/Debian: sudo apt-get install jq
  macOS: brew install jq
  RHEL/CentOS: sudo yum install jq"
    fi
}

# 進捗ファイルの存在確認
check_progress_file() {
    if [[ ! -f "$PROGRESS_FILE" ]]; then
        error "進捗ファイル '$PROGRESS_FILE' が見つかりません"
    fi
}

# 日付計算（移植性のため複数の方法を試行）
get_date() {
    local offset_days="${1:-0}"

    if date -v-1d &> /dev/null; then
        # macOS
        date -v"${offset_days}d" "+%Y-%m-%d"
    else
        # Linux
        date -d "$offset_days days" "+%Y-%m-%d"
    fi
}

# JSONから値を抽出
jq_get() {
    local query="$1"
    jq -r "$query" "$PROGRESS_FILE" 2>/dev/null || echo "0"
}

# タスク数を取得
get_task_count() {
    local status="$1"
    jq_get "[.tasks[] | select(.status == \"$status\")] | length"
}

# 全体進捗率を計算
calculate_overall_progress() {
    local total_progress
    total_progress=$(jq_get '[.tasks[].progress] | add // 0')

    local total_tasks
    total_tasks=$(jq_get '.tasks | length')

    if [[ "$total_tasks" -gt 0 ]]; then
        echo "scale=1; $total_progress / $total_tasks" | bc
    else
        echo "0.0"
    fi
}

# 工数効率を計算
calculate_effort_efficiency() {
    local estimated
    estimated=$(jq_get '[.tasks[].estimatedHours // 0] | add // 0')

    local actual
    actual=$(jq_get '[.tasks[].actualHours // 0] | add // 0')

    if (( $(echo "$estimated > 0" | bc -l) )); then
        echo "scale=1; ($actual / $estimated) * 100" | bc
    else
        echo "0.0"
    fi
}

# 遅延タスクを検出
get_delayed_tasks() {
    local today
    today=$(get_date 0)

    jq -r --arg today "$today" '
        .tasks[] |
        select(.status != "completed") |
        select(.plannedEndDate < $today) |
        "\(.id)|\(.name)|\(.plannedEndDate)|\(.progress)"
    ' "$PROGRESS_FILE"
}

# 遅延リスクタスクを検出
get_at_risk_tasks() {
    local today
    today=$(get_date 0)

    local three_days_later
    three_days_later=$(get_date 3)

    jq -r --arg today "$today" --arg three_days "$three_days_later" '
        .tasks[] |
        select(.status != "completed") |
        select(.plannedEndDate >= $today and .plannedEndDate <= $three_days) |
        select(.progress < 80) |
        "\(.id)|\(.name)|\(.plannedEndDate)|\(.progress)"
    ' "$PROGRESS_FILE"
}

# 期間内に完了したタスクを取得
get_completed_tasks_in_period() {
    local start_date="$1"
    local end_date="$2"

    jq -r --arg start "$start_date" --arg end "$end_date" '
        .tasks[] |
        select(.status == "completed") |
        select(.actualEndDate >= $start and .actualEndDate <= $end) |
        "\(.id)|\(.name)|\(.actualEndDate)"
    ' "$PROGRESS_FILE"
}

# プログレスバーを生成
generate_progress_bar() {
    local progress="$1"
    local width=50

    local filled
    filled=$(echo "scale=0; $progress * $width / 100" | bc)

    local empty
    empty=$((width - filled))

    printf "["
    printf "%${filled}s" | tr ' ' '='
    printf "%${empty}s" | tr ' ' '.'
    printf "] %.1f%%\n" "$progress"
}

# 日次レポート生成
generate_daily_report() {
    local today
    today=$(get_date 0)

    local project_name
    project_name=$(jq_get '.project.name // "未設定"')

    local total_tasks
    total_tasks=$(jq_get '.tasks | length')

    local completed_tasks
    completed_tasks=$(get_task_count "completed")

    local in_progress_tasks
    in_progress_tasks=$(get_task_count "in_progress")

    local not_started_tasks
    not_started_tasks=$(get_task_count "not_started")

    local blocked_tasks
    blocked_tasks=$(get_task_count "blocked")

    local overall_progress
    overall_progress=$(calculate_overall_progress)

    local completion_rate
    if [[ "$total_tasks" -gt 0 ]]; then
        completion_rate=$(echo "scale=1; ($completed_tasks * 100) / $total_tasks" | bc)
    else
        completion_rate="0.0"
    fi

    local effort_efficiency
    effort_efficiency=$(calculate_effort_efficiency)

    # レポート出力開始
    cat << EOF
# 進捗ダッシュボード（日次）
**日付**: $(date "+%Y年%m月%d日")
**プロジェクト**: $project_name

## サマリー

| 項目 | 値 |
|------|-----|
| 全体進捗率 | ${overall_progress}% |
| 完了タスク | ${completed_tasks}/${total_tasks} (${completion_rate}%) |
| 進行中タスク | ${in_progress_tasks} |
| 未着手タスク | ${not_started_tasks} |
| ブロック中タスク | ${blocked_tasks} |

## 進捗状況

\`\`\`
進捗バー: $(generate_progress_bar "$overall_progress")
\`\`\`

## 工数分析

| 項目 | 値 |
|------|-----|
| 工数効率 | ${effort_efficiency}% |

EOF

    # 警告セクション
    local delayed_tasks
    delayed_tasks=$(get_delayed_tasks)

    local at_risk_tasks
    at_risk_tasks=$(get_at_risk_tasks)

    if [[ -n "$delayed_tasks" ]] || [[ -n "$at_risk_tasks" ]]; then
        echo "## 警告"
        echo ""
    fi

    if [[ -n "$delayed_tasks" ]]; then
        local delayed_count
        delayed_count=$(echo "$delayed_tasks" | wc -l)

        echo "### 遅延タスク (${delayed_count}件)"
        echo ""

        while IFS='|' read -r id name planned_end progress; do
            echo "- **${id}**: ${name}"
            echo "  - 計画終了日: ${planned_end}"
            echo "  - 進捗率: ${progress}%"
            echo ""
        done <<< "$delayed_tasks"
    fi

    if [[ -n "$at_risk_tasks" ]]; then
        local at_risk_count
        at_risk_count=$(echo "$at_risk_tasks" | wc -l)

        echo "### 遅延リスク (${at_risk_count}件)"
        echo ""

        while IFS='|' read -r id name planned_end progress; do
            local days_remaining
            days_remaining=$(( ( $(date -d "$planned_end" +%s) - $(date +%s) ) / 86400 ))

            echo "- **${id}**: ${name}"
            echo "  - 計画終了日: ${planned_end}"
            echo "  - 残り日数: ${days_remaining}日"
            echo "  - 進捗率: ${progress}%"
            echo ""
        done <<< "$at_risk_tasks"
    fi

    # 今日のフォーカス
    echo "## 今日のフォーカス"
    echo ""

    local focus_tasks
    focus_tasks=$(jq -r --arg today "$today" '
        .tasks[] |
        select(.status == "in_progress" or .status == "not_started") |
        select(.plannedEndDate <= $today or .priority == "critical") |
        "\(.id)|\(.name)|\(.progress)|\(.priority)"
    ' "$PROGRESS_FILE")

    if [[ -n "$focus_tasks" ]]; then
        while IFS='|' read -r id name progress priority; do
            echo "- **${id}**: ${name}"
            echo "  - 進捗: ${progress}%"
            echo "  - 優先度: ${priority}"
            echo ""
        done <<< "$focus_tasks"
    else
        echo "- 特になし"
        echo ""
    fi
}

# 週次レポート生成
generate_weekly_report() {
    local today
    today=$(get_date 0)

    # 今週の月曜日を計算
    local day_of_week
    day_of_week=$(date +%u)
    local days_since_monday=$((day_of_week - 1))

    local week_start
    week_start=$(get_date -$days_since_monday)

    local week_end
    week_end=$(get_date $((6 - days_since_monday)))

    local project_name
    project_name=$(jq_get '.project.name // "未設定"')

    local weekly_completed
    weekly_completed=$(get_completed_tasks_in_period "$week_start" "$week_end")

    local weekly_completed_count
    if [[ -n "$weekly_completed" ]]; then
        weekly_completed_count=$(echo "$weekly_completed" | wc -l)
    else
        weekly_completed_count=0
    fi

    local overall_progress
    overall_progress=$(calculate_overall_progress)

    # レポート出力
    cat << EOF
# 進捗ダッシュボード（週次）
**期間**: $(date -d "$week_start" "+%Y年%m月%d日") - $(date -d "$week_end" "+%Y年%m月%d日")
**プロジェクト**: $project_name

## 週次サマリー

| 項目 | 値 |
|------|-----|
| 今週完了タスク | ${weekly_completed_count} |
| 全体進捗率 | ${overall_progress}% |

## 今週の達成事項

EOF

    if [[ -n "$weekly_completed" ]]; then
        while IFS='|' read -r id name actual_end; do
            echo "- [${id}] ${name} (完了日: ${actual_end})"
        done <<< "$weekly_completed"
    else
        echo "- なし"
    fi

    echo ""
    echo "## 来週の予定"
    echo ""

    local next_week_start
    next_week_start=$(get_date $((7 - days_since_monday)))

    local next_week_end
    next_week_end=$(get_date $((13 - days_since_monday)))

    local next_week_tasks
    next_week_tasks=$(jq -r --arg start "$next_week_start" --arg end "$next_week_end" '
        .tasks[] |
        select(.plannedStartDate >= $start and .plannedStartDate <= $end) |
        "\(.id)|\(.name)|\(.plannedStartDate)"
    ' "$PROGRESS_FILE")

    if [[ -n "$next_week_tasks" ]]; then
        while IFS='|' read -r id name start_date; do
            echo "- [${id}] ${name} (開始予定: ${start_date})"
        done <<< "$next_week_tasks"
    else
        echo "- なし"
    fi

    echo ""
}

# 月次レポート生成
generate_monthly_report() {
    local today
    today=$(get_date 0)

    local month_start
    month_start=$(date "+%Y-%m-01")

    local next_month
    next_month=$(date -d "$month_start +1 month" "+%Y-%m-01")

    local month_end
    month_end=$(date -d "$next_month -1 day" "+%Y-%m-%d")

    local project_name
    project_name=$(jq_get '.project.name // "未設定"')

    local monthly_completed
    monthly_completed=$(get_completed_tasks_in_period "$month_start" "$month_end")

    local monthly_completed_count
    if [[ -n "$monthly_completed" ]]; then
        monthly_completed_count=$(echo "$monthly_completed" | wc -l)
    else
        monthly_completed_count=0
    fi

    local total_tasks
    total_tasks=$(jq_get '.tasks | length')

    local completed_tasks
    completed_tasks=$(get_task_count "completed")

    local overall_progress
    overall_progress=$(calculate_overall_progress)

    local effort_efficiency
    effort_efficiency=$(calculate_effort_efficiency)

    # レポート出力
    cat << EOF
# 進捗ダッシュボード（月次）
**期間**: $(date "+%Y年%m月")
**プロジェクト**: $project_name

## 月次サマリー

| 項目 | 値 |
|------|-----|
| 今月完了タスク | ${monthly_completed_count} |
| 全体進捗率 | ${overall_progress}% |
| 完了タスク合計 | ${completed_tasks}/${total_tasks} |
| 工数効率 | ${effort_efficiency}% |

## 月間達成事項

EOF

    if [[ -n "$monthly_completed" ]]; then
        while IFS='|' read -r id name actual_end; do
            echo "- [${id}] ${name} (完了日: ${actual_end})"
        done <<< "$monthly_completed"
    else
        echo "- なし"
    fi

    echo ""
    echo "## PDCAサイクル分析"
    echo ""

    local cycle_count
    cycle_count=$(jq_get '.pdcaCycles | length')

    echo "- 総実施回数: ${cycle_count}回"

    if [[ "$cycle_count" -gt 0 ]]; then
        local total_improvements
        total_improvements=$(jq_get '[.pdcaCycles[].act.improvements | length] | add // 0')

        echo "- 提案された改善アクション: ${total_improvements}件"

        local completed_improvements
        completed_improvements=$(jq_get '[.pdcaCycles[].act.improvements[] | select(.status == "completed")] | length')

        echo "- 完了した改善アクション: ${completed_improvements}件"
    fi

    echo ""
}

# メイン処理
main() {
    check_dependencies
    check_progress_file

    local report_content

    case "$REPORT_TYPE" in
        daily)
            report_content=$(generate_daily_report)
            ;;
        weekly)
            report_content=$(generate_weekly_report)
            ;;
        monthly)
            report_content=$(generate_monthly_report)
            ;;
        *)
            error "不正なレポートタイプ: $REPORT_TYPE (daily/weekly/monthly を指定)"
            ;;
    esac

    if [[ -n "$OUTPUT_FILE" ]]; then
        # ディレクトリ作成
        mkdir -p "$(dirname "$OUTPUT_FILE")"

        # ファイルに出力
        echo "$report_content" > "$OUTPUT_FILE"
        success "ダッシュボードを $OUTPUT_FILE に出力しました"
    else
        # 標準出力
        echo "$report_content"
    fi
}

# 使用方法表示
usage() {
    cat << EOF
使用方法: $0 <report_type> [output_file]

引数:
  report_type   レポートタイプ (daily/weekly/monthly)
  output_file   出力ファイルパス（省略時は標準出力）

環境変数:
  PROGRESS_FILE  進捗データファイル（デフォルト: progress.json）

例:
  $0 daily                        # 日次レポートを標準出力
  $0 weekly reports/weekly.md     # 週次レポートをファイル出力
  PROGRESS_FILE=data.json $0 monthly  # カスタムデータファイルを使用

EOF
    exit 0
}

# ヘルプオプション
if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
    usage
fi

# メイン実行
main
