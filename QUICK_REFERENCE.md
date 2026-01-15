# クイックリファレンス - プロジェクト要件システム

## 🚀 ワークフロー（7ステップ）

```
STEP 1: /spec-refine          → SPEC.md
   ↓
STEP 2: /plan-project         → tasks.json, PLAN.md
   ↓
STEP 3: /schedule-tasks       → schedule.json, SCHEDULE.md
   ↓
STEP 4: /github-sync          → GitHub Repo, Issues, Projects V2
   ↓
STEP 5: 手動設定 + スクリプト   → Roadmap View
   ↓
STEP 6: SendGrid設定          → 週次レポート自動送信
   ↓
STEP 7: update-schedule.py    → スケジュール変更管理
```

**所要時間**: 約1.5時間（初回）

---

## 📝 Slash Commands

| コマンド | 用途 | 時間 |
|---------|------|------|
| `/spec-refine` | 仕様書作成 | 30-60分 |
| `/plan-project` | タスク分解 | 10-15分 |
| `/schedule-tasks` | スケジューリング | 5-10分 |
| `/github-sync` | GitHub連携 | 5-10分 |

---

## 🔧 主要スクリプト

### GitHub連携
```bash
# 初回同期
python3 scripts/sync-github.py

# Roadmap日付設定
python3 scripts/set-issue-dates.py --project-number=3
```

### スケジュール変更
```bash
# インタラクティブモード（推奨）
python3 scripts/update-schedule.py --interactive

# 期限延長
python3 scripts/update-schedule.py --task TASK-007 --extend-deadline 7

# 開始日変更
python3 scripts/update-schedule.py --task TASK-015 --start-date 2026-02-10

# タスク削除
python3 scripts/update-schedule.py --task TASK-010 --action delete

# 優先度変更
python3 scripts/update-schedule.py --task TASK-005 --priority high
```

### 週次レポート
```bash
# 手動送信テスト
python3 scripts/send-progress-report.py
```

---

## 📊 自動更新されるファイル

スケジュール変更時、以下が**自動更新**されます：

✅ `tasks.json` - タスク定義
✅ `schedule.json` - スケジュールデータ
✅ **`PLAN.md`** - WBS、工数サマリー
✅ **`SCHEDULE.md`** - 週次スケジュール
✅ `github-issue-mapping.json` - マッピング
✅ GitHub Issues - マイルストーン
✅ GitHub Projects V2 - Start/End Date
✅ **依存タスク** - 自動連鎖延長

---

## 🔗 重要リンク

### ドキュメント
- **[完全ワークフローガイド](docs/PROJECT_WORKFLOW_GUIDE.md)** - 必読
- [GitHub連携セットアップ](docs/GITHUB_SYNC_SETUP.md)
- [スケジュール更新ガイド](docs/SCHEDULE_UPDATE_GUIDE.md)
- [週次レポート設定](docs/PROGRESS_REPORT_SETUP.md)

### 計画ファイル
- [SPEC.md](SPEC.md) - 仕様書
- [PLAN.md](PLAN.md) - WBS、工数
- [SCHEDULE.md](SCHEDULE.md) - 週次スケジュール

---

## 💬 自然言語でのスケジュール変更

Claude Codeに以下のように依頼するだけで、全ファイル+GitHubが自動更新されます：

- 「TASK-007の期限を1週間延ばしたい」
- 「TASK-015を2月10日から開始するように変更したい」
- 「TASK-010は不要になったので削除したい」
- 「TASK-005の優先度を高くしたい」

---

## ⚡ よく使うコマンド

### プロジェクト開始時
```bash
/spec-refine
/plan-project
/schedule-tasks
/github-sync
python3 scripts/set-issue-dates.py --project-number=3
```

### プロジェクト実行中
```bash
# ステータス更新
code tasks.json  # status を "in_progress" または "done" に変更
git add tasks.json && git commit -m "Update status" && git push

# スケジュール変更
python3 scripts/update-schedule.py --interactive
```

### 週次レビュー
- 月曜日 9:00: 週次レポートがメールで届く
- GitHub Milestones で進捗確認
- GitHub Projects V2 Roadmap で全体確認

---

## 🆘 トラブルシューティング

### GitHub CLI認証エラー
```bash
gh auth login
```

### Projects V2日付設定エラー
1. Projects V2に「Start Date」「End Date」フィールドを作成
2. Project Numberを確認（URLの末尾）
3. スクリプト再実行

### 週次レポートが届かない
1. GitHub Secrets確認（SENDGRID_API_KEY, REPORT_TO_EMAIL）
2. 迷惑メールフォルダ確認
3. SendGrid API Key確認

---

**詳細**: [docs/PROJECT_WORKFLOW_GUIDE.md](docs/PROJECT_WORKFLOW_GUIDE.md)
