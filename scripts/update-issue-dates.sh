#!/bin/bash
# GitHub Issues に開始日・終了日を設定するスクリプト
# 使用方法: ./scripts/update-issue-dates.sh

REPO="sh-usami-rg/dashboard-migration-project"

echo "📅 Issuesに日付を設定中..."

# schedule.jsonから日付を取得して、各Issueを更新
# 注意: GitHub Projects V2のカスタムフィールドAPIは複雑なため、
# 手動でTable viewから設定することを推奨します。

echo "ℹ️  GitHub Projects V2のカスタムフィールド（Start Date / End Date）は、"
echo "   Projects画面のTable viewから手動で設定してください。"
echo ""
echo "📊 以下のURLからTable viewを開いて設定："
echo "   https://github.com/users/sh-usami-rg/projects/YOUR_PROJECT_NUMBER"
echo ""
echo "📋 schedule.jsonの日付を参照してください："
echo "   cat schedule.json | jq '.tasks[] | {id, startDate, endDate}'"

# schedule.jsonから日付情報を表示
cat schedule.json | jq -r '.tasks[] | "\(.id): \(.startDate) 〜 \(.endDate)"'
