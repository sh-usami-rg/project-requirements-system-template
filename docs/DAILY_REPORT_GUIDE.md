# 日次レポート自動配信ガイド

プロジェクトの進捗を毎日自動的にGitHub Issueに投稿する機能のセットアップと使い方のガイドです。

---

## 📊 概要

この機能は、GitHub Actionsを使用して以下を自動実行します：

1. 毎日18:30 JST（9:30 UTC）にワークフロー実行
2. tasks.jsonから進捗データを読み込み
3. 日次レポートをMarkdown形式で生成
4. 指定したGitHub Issueにコメントとして投稿

---

## 🚀 セットアップ手順

### STEP 1: 進捗レポート用Issueを作成

まず、日次レポートを投稿するためのGitHub Issueを作成します。

```bash
# GitHub CLI で Issue を作成
gh issue create \
  --title "📊 日次進捗レポート" \
  --body "このIssueには、プロジェクトの日次進捗レポートが自動投稿されます。" \
  --label "progress-report"
```

または、GitHub Web UIで以下の内容で新しいIssueを作成：

- **タイトル**: 📊 日次進捗レポート
- **本文**: このIssueには、プロジェクトの日次進捗レポートが自動投稿されます。
- **ラベル**: progress-report（作成）

作成したIssueの番号をメモしてください（例: #1）

### STEP 2: GitHub Actionsワークフローを設定

`.github/workflows/daily-progress-report.yml` を編集し、Issue番号を設定します：

```yaml
# ⚠️ この行を編集
ISSUE_NUMBER: 1  # ← ここを作成したIssue番号に変更
```

例：Issue #66を作成した場合は `ISSUE_NUMBER: 66` に設定。

### STEP 3: ワークフローを有効化

変更をコミット＆プッシュします：

```bash
git add .github/workflows/daily-progress-report.yml
git commit -m "Setup daily progress report workflow"
git push origin main
```

これで、毎日18:30 JST（9:30 UTC）に自動実行されます。

### STEP 4: テスト実行

設定が正しいか確認するため、手動で実行してみます：

```bash
# GitHub Web UIから実行
# 1. リポジトリの "Actions" タブを開く
# 2. "Daily Progress Report" を選択
# 3. "Run workflow" をクリック

# または、GitHub CLIで実行
gh workflow run "Daily Progress Report"
```

実行後、指定したIssueにコメントが投稿されていることを確認してください。

---

## 📋 レポート内容

日次レポートには以下の情報が含まれます：

### 1. 全体進捗

- 進捗率（%）
- 総タスク数
- ステータス別タスク数（完了、進行中、未着手、ブロック）
- 進捗バー

### 2. 本日のタスク

開始日または終了日が今日のタスク

### 3. 進行中のタスク

現在進行中のすべてのタスク（Phase、中カテゴリ、担当者付き）

### 4. ブロック中のタスク

ブロックされているタスクの一覧

### 5. 最近完了したタスク

直近5件の完了タスク

### 6. Phase別進捗

各Phaseの完了数、総数、進捗率

---

## 🎨 レポート例

```markdown
# 📊 日次進捗レポート - Webアプリケーション開発

**日付**: 2026年01月18日 (Saturday)

---

## 📈 全体進捗

- **進捗率**: 45.5%
- **総タスク数**: 25
  - ✅ 完了: 10
  - 🔄 進行中: 5
  - 📝 未着手: 10
  - 🚫 ブロック: 0

進捗バー: `██████████░░░░░░░░░░` 45.5%

---

## 🎯 本日のタスク

- 🔄 **[TASK-011]** 認証画面実装
- 📝 **[TASK-012]** ダッシュボード画面実装

---

## 🔄 進行中のタスク

- **[TASK-011]** 認証画面実装
  - Phase: Phase 2 / 中カテゴリ: フロントエンド実装
  - 担当: Frontend Engineer

- **[TASK-013]** 認証API実装
  - Phase: Phase 2 / 中カテゴリ: バックエンド実装
  - 担当: Backend Engineer

...

---

## ✅ 最近完了したタスク（直近5件）

- **[TASK-006]** データベース設計
- **[TASK-007]** API設計
- **[TASK-008]** 開発環境セットアップ
- **[TASK-009]** CI/CDパイプライン構築
- **[TASK-010]** UIコンポーネントライブラリ構築

---

## 📊 Phase別進捗

| Phase | 完了 | 総数 | 進捗率 |
|-------|------|------|--------|
| Phase 1 | 7 | 7 | 100.0% |
| Phase 2 | 3 | 11 | 27.3% |
| Phase 3 | 0 | 7 | 0.0% |

---

*自動生成: 2026-01-18 18:30:00*
```

---

## 🔧 カスタマイズ

### 実行タイミングの変更

`.github/workflows/daily-progress-report.yml` の `cron` を編集：

```yaml
on:
  schedule:
    # 毎日 18:30 JST (09:30 UTC) に実行
    - cron: '30 9 * * *'  # ← ここを変更
```

**例**:
- 毎日9:00 JST: `cron: '0 0 * * *'`
- 毎週月曜日9:00 JST: `cron: '0 0 * * 1'`
- 平日のみ9:00 JST: `cron: '0 0 * * 1-5'`

### レポート内容の変更

`scripts/daily-report.py` を編集して、レポート内容をカスタマイズできます：

```python
def generate_report(data: Dict) -> str:
    """日次レポートを生成"""
    # この関数を編集してレポート内容を変更
    # ...
```

### 投稿先の変更

**Slackへ投稿する場合**:

1. Slack Incoming Webhookを設定
2. GitHub SecretsにWebhook URLを登録（`SLACK_WEBHOOK_URL`）
3. `daily-report.py` にSlack投稿機能を追加

---

## 🛠️ ローカルでの実行

GitHub Actionsを使わず、ローカルで実行する場合：

```bash
# 標準出力に表示
python3 scripts/daily-report.py

# ファイルに出力
python3 scripts/daily-report.py --output daily-report.md

# GitHub Issueに投稿（環境変数が必要）
export GITHUB_REPOSITORY="owner/repo"
export GITHUB_TOKEN="your_github_token"
python3 scripts/daily-report.py --github --issue-number 1
```

---

## 📅 運用のベストプラクティス

### 1. 毎日の確認

- 朝または夕方にIssueを確認
- ブロック中のタスクがあれば早期対応
- 進捗率が予定より低い場合はリソース配分を見直し

### 2. 週次レビューとの併用

- 日次レポート: 短期的な進捗確認
- 週次レビュー: 中長期的な進捗確認、リスク管理

### 3. チーム共有

- 日次レポートIssueをチーム全員がウォッチ
- コメント機能でタスクについて議論
- ブロック解消のための協力

### 4. 履歴として活用

- 過去のレポートで進捗の推移を確認
- プロジェクト終了後の振り返りに使用
- 次回プロジェクトの計画精度向上に活用

---

## 📊 進捗の解釈

### 健全なプロジェクト

- 進捗率が日々増加
- ブロック中のタスクが少ない（0-1件）
- Phase 1が100%完了してからPhase 2に着手

### 注意が必要なプロジェクト

- 進捗率が停滞または減少
- ブロック中のタスクが多い（3件以上）
- 複数のPhaseが同時に進行中

---

## ⚠️ トラブルシューティング

### Q1: ワークフローが実行されない

**原因と対策**:
- GitHub Actionsが有効か確認
- cronの時刻設定を確認（UTCであることに注意）
- リポジトリにpushしてワークフローをトリガー

### Q2: Issueにコメントが投稿されない

**原因と対策**:
- Issue番号が正しいか確認
- `GITHUB_TOKEN` の権限を確認
- `gh` CLIがインストールされているか確認（GitHub Actionsでは自動）

### Q3: tasks.jsonが見つからないエラー

**原因と対策**:
- リポジトリのルートディレクトリにtasks.jsonが存在するか確認
- ファイル名が正しいか確認（大文字小文字に注意）

### Q4: 手動実行はできるが、cronで実行されない

**原因と対策**:
- デフォルトブランチ（main/master）にワークフローファイルが存在するか確認
- cronは最後のコミットから60日以内のリポジトリでのみ動作

---

## 🔐 セキュリティ

### GitHub Token

- `GITHUB_TOKEN` は自動的に提供されるため、手動設定不要
- 権限は `contents: read`, `issues: write` のみ
- Personal Access Tokenを使う場合は、必要最小限の権限を付与

### プライベートリポジトリ

- プライベートリポジトリでも問題なく動作
- Issue は同じリポジトリ内にのみ投稿可能

---

## 📚 関連ドキュメント

- [進捗可視化ガイド](PROGRESS_VISUALIZATION_GUIDE.md)
- [中カテゴリ管理ガイド](MID_CATEGORY_GUIDE.md)
- [GitHub同期セットアップガイド](GITHUB_SYNC_SETUP.md)

---

## 🔄 更新履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-18 | 初版作成 |

---

**作成日**: 2026-01-18
**更新日**: 2026-01-18
