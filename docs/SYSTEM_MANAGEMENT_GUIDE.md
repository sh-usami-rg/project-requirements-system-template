# システム管理・運用ガイド

## 📋 概要

このドキュメントでは、作成したプロジェクト要件システムを**どのように管理・運用するか**を説明します。

---

## 🎯 このシステムの位置づけ

### このシステムは「テンプレート」兼「ツールキット」です

```
project-requirements-system/
├── 📦 テンプレート部分
│   ├── SPEC.md (例)          # 実際のプロジェクトで上書きされる
│   ├── PLAN.md (例)          # 実際のプロジェクトで上書きされる
│   ├── SCHEDULE.md (例)      # 実際のプロジェクトで上書きされる
│   ├── tasks.json (例)       # 実際のプロジェクトで上書きされる
│   └── schedule.json (例)    # 実際のプロジェクトで上書きされる
│
└── 🔧 ツールキット部分（再利用）
    ├── .claude/commands/     # Slash commands（変更不要）
    ├── scripts/              # 自動化スクリプト（変更不要）
    ├── docs/                 # ガイドドキュメント（参照のみ）
    └── .github/workflows/    # GitHub Actions（設定のみ変更）
```

---

## 🗂️ 管理方法（2つのアプローチ）

### アプローチ1: テンプレートリポジトリとして管理（推奨）

**メリット**: 新規プロジェクトごとに完全な独立環境を作成できる

#### セットアップ手順

1. **このシステムをGitHubテンプレートリポジトリ化**

```bash
cd /home/sh-usami/project-requirements-system

# Gitリポジトリ初期化（まだの場合）
git init

# .gitignoreを作成
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python
*.so

# Virtual Environment
venv/
env/

# Backups
.backups/

# Secrets（重要！）
.env
secrets.json

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
EOF

# 全ファイルをコミット
git add .
git commit -m "Initial commit: Project Requirements System Template"

# GitHubにプッシュ
gh repo create project-requirements-system-template --public --source=. --push

# テンプレート化（GitHub Web UIで設定）
# Settings → Template repository にチェック
```

2. **新規プロジェクト開始時の手順**

```bash
# GitHubでテンプレートから新規リポジトリを作成
# 「Use this template」ボタンをクリック → 新規リポジトリ名を入力

# ローカルにクローン
git clone https://github.com/your-username/new-project-name.git
cd new-project-name

# 新規プロジェクトの作成開始
/spec-refine
/plan-project
/schedule-tasks
/github-sync
```

**このアプローチが適している場合**:
- 複数の異なるプロジェクトで使いたい
- 各プロジェクトを完全に独立管理したい
- チームメンバーが異なる

---

### アプローチ2: 単一リポジトリ内で複数プロジェクト管理

**メリット**: 関連プロジェクトを1箇所で管理できる

#### ディレクトリ構造

```bash
project-requirements-system/
├── _system/                  # システム本体（共通）
│   ├── .claude/commands/
│   ├── scripts/
│   ├── docs/
│   └── .github/workflows/
│
├── projects/                 # 各プロジェクト
│   ├── dashboard-migration/  # プロジェクト1
│   │   ├── SPEC.md
│   │   ├── PLAN.md
│   │   ├── SCHEDULE.md
│   │   ├── tasks.json
│   │   └── schedule.json
│   │
│   ├── api-redesign/         # プロジェクト2
│   │   ├── SPEC.md
│   │   ├── PLAN.md
│   │   └── ...
│   │
│   └── mobile-app/           # プロジェクト3
│       └── ...
│
└── README.md                 # 全体の説明
```

#### セットアップ手順

```bash
# ディレクトリ構造を再編成
mkdir -p _system projects

# システムファイルを移動
mv .claude _system/
mv scripts _system/
mv docs _system/
mv .github _system/

# 現在のプロジェクトを移動
mkdir projects/dashboard-migration
mv SPEC.md PLAN.md SCHEDULE.md tasks.json schedule.json projects/dashboard-migration/

# スクリプトのパス調整
# scripts内のパスを相対パスから絶対パスに変更

# 新規プロジェクト開始時
cd projects/new-project
# システムのコマンドを実行（パスを調整）
```

**このアプローチが適している場合**:
- 関連する複数プロジェクトを並行管理したい
- チームが同じ
- システムの更新を一箇所で管理したい

---

## 🔄 運用フロー

### 初回セットアップ（プロジェクト開始前）

```bash
# 1. テンプレートから新規プロジェクト作成
# （GitHubで「Use this template」）

# 2. ローカルにクローン
git clone https://github.com/your-org/new-project.git
cd new-project

# 3. GitHub CLI認証
gh auth login

# 4. ワークフロー実行
/spec-refine          # 30分
/plan-project         # 10分
/schedule-tasks       # 5分
/github-sync          # 10分

# 5. Roadmap設定
# GitHub Projects V2でStart Date/End Dateフィールド作成
python3 scripts/set-issue-dates.py --project-number=3

# 6. 週次レポート設定
# SendGridアカウント作成
# GitHub Secrets設定

# 7. GitHubにプッシュ
git add .
git commit -m "Setup: Complete project initialization"
git push origin main
```

**所要時間**: 約1.5-2時間

---

### 日常的な運用（プロジェクト実行中）

#### 毎日のタスク管理

```bash
# タスク開始時
code tasks.json
# status を "in_progress" に変更

git add tasks.json
git commit -m "Start TASK-007"
git push

# タスク完了時
code tasks.json
# status を "done" に変更

git add tasks.json
git commit -m "Complete TASK-007"
git push
```

#### スケジュール変更時

```bash
# 方法1: 自然言語でClaude Codeに依頼（推奨）
「TASK-007の期限を1週間延ばしたい」

# 方法2: コマンド実行
python3 scripts/update-schedule.py --interactive

# 自動で更新されるファイルをコミット
git add tasks.json schedule.json PLAN.md SCHEDULE.md
git commit -m "Schedule: Extend TASK-007 deadline by 7 days"
git push
```

#### 週次レビュー（毎週月曜日）

```bash
# 1. 週次レポートを確認（メールで届く）
# 2. GitHub Milestones で進捗確認
#    https://github.com/your-org/project/milestones
# 3. GitHub Projects V2 Roadmap で全体確認
#    https://github.com/users/your-org/projects/3
# 4. 遅延タスクがあれば調整
python3 scripts/update-schedule.py --interactive
```

---

## 📦 バージョン管理のベストプラクティス

### コミットメッセージ規則

```bash
# タスクステータス更新
git commit -m "Task: Start TASK-007"
git commit -m "Task: Complete TASK-007"

# スケジュール変更
git commit -m "Schedule: Extend TASK-007 deadline by 7 days"
git commit -m "Schedule: Delete TASK-010"

# 仕様変更
git commit -m "Spec: Update BigQuery connection requirements"

# 計画変更
git commit -m "Plan: Add TASK-026 for data validation"
```

### ブランチ戦略

```bash
# 基本はmainブランチのみで運用
main

# 大きな変更の場合のみブランチを作成
git checkout -b feature/add-new-phase
# 変更作業
git commit -m "Plan: Add Phase 4 for maintenance"
git push origin feature/add-new-phase
# Pull Request作成 → レビュー → マージ
```

### タグ付け（マイルストーン完了時）

```bash
# Phase 1完了時
git tag -a phase1-complete -m "Phase 1: 基盤整備と設計 完了"
git push origin phase1-complete

# Phase 2完了時
git tag -a phase2-complete -m "Phase 2: 実装と技術検証 完了"
git push origin phase2-complete

# プロジェクト完了時
git tag -a v1.0.0 -m "Project Complete: Dashboard Migration v1.0"
git push origin v1.0.0
```

---

## 🔧 システムのメンテナンス

### システムファイルの更新

テンプレートリポジトリのシステムファイル（scripts, commands, docs）を更新した場合：

```bash
# 方法1: 手動で最新版を取得
cd ~/project-requirements-system-template
git pull

# 変更されたファイルを各プロジェクトにコピー
cp scripts/update-schedule.py ~/project1/scripts/
cp scripts/update-schedule.py ~/project2/scripts/

# 方法2: Git subtree/submodule を使用（上級者向け）
git subtree add --prefix=_system https://github.com/you/system.git main
git subtree pull --prefix=_system https://github.com/you/system.git main
```

### スクリプトのバージョン管理

```python
# scripts/update-schedule.py の先頭に追加
__version__ = "1.1.0"

# 使用時にバージョン確認
python3 scripts/update-schedule.py --version
```

---

## 📊 定期的なバックアップ

### 自動バックアップの確認

```bash
# システムは .backups/ に自動バックアップを作成
ls -la .backups/

# 古いバックアップの削除（30日以上前）
find .backups/ -type d -mtime +30 -exec rm -rf {} \;
```

### 手動バックアップ（重要なマイルストーン前）

```bash
# プロジェクト全体をバックアップ
cd ..
tar -czf project-backup-$(date +%Y%m%d).tar.gz project-name/

# または
rsync -av project-name/ backup/project-name-$(date +%Y%m%d)/
```

---

## 🔐 セキュリティ管理

### 機密情報の取り扱い

```bash
# .gitignoreに機密情報を追加（必須）
echo ".env" >> .gitignore
echo "secrets.json" >> .gitignore
echo "*.key" >> .gitignore
echo "*.pem" >> .gitignore

# GitHub Secretsを使用
# Settings → Secrets and variables → Actions
# - SENDGRID_API_KEY
# - REPORT_TO_EMAIL
# - 他の機密情報
```

### リポジトリのアクセス権限

```bash
# Private リポジトリを推奨
gh repo create project-name --private

# チームメンバーのみにアクセス権限を付与
# Settings → Collaborators → Add people
```

---

## 📈 システムの拡張

### 新しいSlash Commandの追加

```bash
# .claude/commands/new-command.md を作成
cat > .claude/commands/new-command.md << 'EOF'
---
allowed-tools: "Read, Write, Edit"
description: "新しいコマンドの説明"
---

# Role
あなたの役割

# Process
実行手順

# Start
開始
EOF

# 使用方法
/new-command
```

### 新しいスクリプトの追加

```bash
# scripts/new-script.py を作成
cat > scripts/new-script.py << 'EOF'
#!/usr/bin/env python3
"""
新しいスクリプトの説明
"""

def main():
    pass

if __name__ == "__main__":
    main()
EOF

chmod +x scripts/new-script.py
```

---

## 🆘 トラブル時のリカバリー

### バックアップからの復元

```bash
# 最新のバックアップを確認
ls -lt .backups/ | head -5

# 復元
cp .backups/20260115_143052/tasks.json ./
cp .backups/20260115_143052/schedule.json ./
cp .backups/20260115_143052/PLAN.md ./
cp .backups/20260115_143052/SCHEDULE.md ./

# GitHubに反映
git add tasks.json schedule.json PLAN.md SCHEDULE.md
git commit -m "Recovery: Restore from backup 20260115_143052"
git push
```

### Git履歴からの復元

```bash
# 特定のファイルを過去のバージョンに戻す
git log --oneline tasks.json
git checkout <commit-hash> -- tasks.json

# コミット全体を取り消す
git revert <commit-hash>
```

---

## 📚 ドキュメントの更新

### プロジェクト固有のドキュメント追加

```bash
# プロジェクト固有のドキュメントを追加
mkdir -p docs/project-specific
cat > docs/project-specific/DEPLOYMENT.md << 'EOF'
# デプロイメント手順

## 本番環境
...
EOF

# README.mdに追加
echo "- [デプロイメント手順](docs/project-specific/DEPLOYMENT.md)" >> README.md
```

### システムドキュメントの更新

```bash
# 新機能追加時は PROJECT_WORKFLOW_GUIDE.md を更新
code docs/PROJECT_WORKFLOW_GUIDE.md

# 変更履歴を記録
git add docs/PROJECT_WORKFLOW_GUIDE.md
git commit -m "Docs: Add new workflow step for deployment"
```

---

## 🎓 チーム運用のベストプラクティス

### オンボーディング（新メンバー参加時）

1. **リポジトリへのアクセス権付与**
2. **ドキュメント読解課題**:
   - README.md
   - docs/PROJECT_WORKFLOW_GUIDE.md
   - QUICK_REFERENCE.md
3. **環境セットアップ**:
   - GitHub CLI認証
   - SendGrid設定（オプション）
4. **練習タスク**: 1つのタスクをアサインして、ステータス更新の練習

### 定期的なレビュー（月次）

```bash
# 1. プロジェクト全体の進捗確認
cat SCHEDULE.md

# 2. クリティカルパスの確認
grep "critical-path" PLAN.md

# 3. リスクの再評価
code PLAN.md  # リスク管理セクションを更新

# 4. スケジュールの妥当性確認
# 遅延が続いている場合は全体を再スケジュール
python3 scripts/update-schedule.py --interactive
```

---

## 📊 運用チェックリスト

### 毎日
- [ ] タスクステータスを更新
- [ ] GitHubにプッシュ

### 毎週（月曜日）
- [ ] 週次レポートを確認
- [ ] GitHub Milestones で進捗確認
- [ ] Roadmap で全体確認
- [ ] 遅延タスクの調整

### 毎月
- [ ] 全体進捗のレビュー
- [ ] リスク管理の更新
- [ ] スケジュールの妥当性確認
- [ ] 古いバックアップの削除

### Phase完了時
- [ ] 成果物のレビュー
- [ ] Gitタグ付け
- [ ] レトロスペクティブ（振り返り）
- [ ] 次Phaseへの準備

### プロジェクト完了時
- [ ] 最終成果物の確認
- [ ] ドキュメントの完成
- [ ] 最終レポート作成
- [ ] リポジトリのアーカイブ
- [ ] ナレッジのドキュメント化

---

## 🚀 まとめ

### このシステムを効果的に運用するための5つのポイント

1. **テンプレート化**: 新規プロジェクトごとにテンプレートから開始
2. **自動化活用**: スクリプトとSlash Commandsを最大限活用
3. **定期的な同期**: GitHubと常に同期を保つ
4. **週次レビュー**: 毎週月曜日に必ず進捗確認
5. **ドキュメント更新**: 変更があれば必ずドキュメント更新

### よくある質問

**Q1: 複数プロジェクトを同時に管理できますか？**
A: はい。アプローチ2（単一リポジトリ内で複数プロジェクト管理）を使用するか、テンプレートから複数のリポジトリを作成してください。

**Q2: システムを更新したら全プロジェクトに反映する必要がありますか？**
A: いいえ。既存プロジェクトは現在のバージョンで継続可能です。重要な機能追加のみ手動で反映してください。

**Q3: チームメンバーが増えた場合は？**
A: GitHubリポジトリのCollaboratorsに追加し、オンボーディング手順に従ってください。

**Q4: プロジェクト完了後、リポジトリはどうすればいいですか？**
A: Gitタグを付けてアーカイブし、Settings → Archive this repository でアーカイブ化してください。

---

**最終更新**: 2026-01-15
**バージョン**: 1.0
