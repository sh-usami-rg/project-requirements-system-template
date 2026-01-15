# GitHub Issues & Projects連携 セットアップ手順

このドキュメントでは、tasks.jsonとschedule.jsonのデータをGitHub Issues・Milestones・Projects V2に同期する手順を説明します。

## 目次

1. [概要](#概要)
2. [前提条件](#前提条件)
3. [GitHub CLIのインストール](#github-cliのインストール)
4. [GitHub CLI認証](#github-cli認証)
5. [同期スクリプトの実行](#同期スクリプトの実行)
6. [作成されるもの](#作成されるもの)
7. [トラブルシューティング](#トラブルシューティング)
8. [よくある質問（FAQ）](#よくある質問faq)

## 概要

この同期機能により、以下がGitHub上に自動作成されます：

- **GitHubリポジトリ**: 新規作成（Private）
- **25個のIssues**: 各タスクに対応
- **12個のMilestones**: Week 1-12の週次マイルストーン
- **ラベル一式**: Phase, Priority, Category等
- **GitHub Projects V2**: プロジェクト管理ボード

## 前提条件

### 必須
- ✅ GitHubアカウント
- ✅ Python 3.7以上
- ✅ インターネット接続

### 推奨
- tasks.jsonとschedule.jsonが正しく作成されていること
- GitHubの無料プランで十分（Private Repositoryも利用可能）

## GitHub CLIのインストール

GitHub CLI (`gh`) は、コマンドラインからGitHubを操作するための公式ツールです。

### macOS

Homebrewを使用してインストール:

```bash
brew install gh
```

### Linux

#### Ubuntu/Debian

```bash
# パッケージリポジトリを追加
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null

# インストール
sudo apt update
sudo apt install gh
```

#### Fedora/RHEL/CentOS

```bash
sudo dnf install gh
```

### Windows

#### winget（Windows 11、Windows 10）

```powershell
winget install --id GitHub.cli
```

#### Scoop

```powershell
scoop install gh
```

#### Chocolatey

```powershell
choco install gh
```

### インストール確認

```bash
gh --version
```

以下のような出力が表示されればOK:

```
gh version 2.40.0 (2024-01-01)
https://github.com/cli/cli/releases/tag/v2.40.0
```

## GitHub CLI認証

GitHub CLIを使用するには、GitHubアカウントで認証する必要があります。

### 認証手順

```bash
gh auth login
```

対話的に以下の質問に答えます：

1. **What account do you want to log into?**
   - → `GitHub.com` を選択

2. **What is your preferred protocol for Git operations?**
   - → `HTTPS` を選択（推奨）

3. **Authenticate Git with your GitHub credentials?**
   - → `Yes` を選択

4. **How would you like to authenticate GitHub CLI?**
   - → `Login with a web browser` を選択（推奨）
   - または `Paste an authentication token` でPersonal Access Tokenを入力

5. ブラウザが開くので、GitHubにログインして認証コードを入力

### 認証確認

```bash
gh auth status
```

以下のような出力が表示されればOK:

```
github.com
  ✓ Logged in to github.com as your-username (oauth_token)
  ✓ Git operations for github.com configured to use https protocol.
  ✓ Token: *******************
```

## 同期スクリプトの実行

### 1. プロジェクトディレクトリに移動

```bash
cd /home/sh-usami/project-requirements-system
```

### 2. スクリプトを実行

```bash
python scripts/sync-github.py
```

または、実行権限がある場合:

```bash
./scripts/sync-github.py
```

### 3. リポジトリ名を入力

プロンプトが表示されたら、作成するGitHubリポジトリ名を入力します：

```
GitHubリポジトリ名を入力してください。
例: project-requirements-system
リポジトリ名: dashboard-migration-project
```

### 4. 実行完了を待つ

スクリプトが以下の処理を順番に実行します（約5-10分）：

```
🚀 GitHub同期開始
==================================================================
✅ GitHub CLI認証確認完了

📦 リポジトリ作成中: dashboard-migration-project (private)
✅ リポジトリ作成完了: your-username/dashboard-migration-project

🏷️  ラベル作成中（12個）...
  ✓ phase-1
  ✓ phase-2
  ...
✅ ラベル作成完了

🎯 マイルストーン作成中（12個）...
  ✓ Week 1
  ✓ Week 2
  ...
✅ マイルストーン作成完了

📝 Issue作成中（25個）...
  ✓ TASK-001 → #1
  ✓ TASK-002 → #2
  ...
✅ Issue作成完了

📊 GitHub Projects作成中: 顧問ミドル運用ダッシュボード移行 - プロジェクト管理
✅ Projects作成完了: https://github.com/users/your-username/projects/1
   Project ID: 1

🔗 IssuesをProjectsに追加中...
  ✓ #1 (TASK-001)
  ✓ #2 (TASK-002)
  ...
✅ Issue追加完了

⚙️  Projectsカスタムフィールド設定中...
  ✓ Weight (NUMBER)
  ✓ Effort (Days) (NUMBER)
  ✓ Week (TEXT)
✅ カスタムフィールド設定完了

📌 次のステップ:
  1. GitHubでProjectsを開く
  2. ビューを作成（Board, Table, Roadmap）
  3. Status, Start Date, End Date フィールドを手動で設定

==================================================================
✅ GitHub同期完了
==================================================================

📦 リポジトリ: https://github.com/your-username/dashboard-migration-project
📊 Projects: https://github.com/users/your-username/projects/1
📝 Issues: https://github.com/your-username/dashboard-migration-project/issues
```

### 5. GitHubで確認

ブラウザで以下のURLを開いて確認します：

- **リポジトリ**: 表示されたリポジトリURLを開く
- **Issues**: 25個のIssueが作成されているか確認
- **Milestones**: Week 1-12が作成されているか確認
- **Projects**: プロジェクトボードを開いて確認

## 作成されるもの

### 1. GitHubリポジトリ

- **名前**: 入力したリポジトリ名
- **可視性**: Private（デフォルト）
- **説明**: tasks.jsonのプロジェクト説明

### 2. Issues（25個）

各タスクがIssueとして作成されます：

- **タイトル**: `[TASK-001] タスク名`
- **本文**: タスク概要、情報、スケジュール、依存関係、完了条件
- **ラベル**: Phase, Priority, Category, Critical Path等
- **マイルストーン**: Week 1-12のいずれか
- **担当者**: 設定なし（手動で設定可能）

### 3. Milestones（12個）

Week 1-12の週次マイルストーン:

- **タイトル**: "Week 1", "Week 2", ..., "Week 12"
- **期限**: 各週の終了日
- **説明**: 日付範囲、予定進捗率、タスク一覧

### 4. ラベル（12個）

| ラベル名 | 色 | 説明 |
|---------|-----|------|
| phase-1 | 🟢 緑 | Phase 1: 基盤整備と設計 |
| phase-2 | 🔵 青 | Phase 2: 実装と技術検証 |
| phase-3 | 🟣 紫 | Phase 3: フル移行と展開 |
| priority-high | 🔴 赤 | 優先度: 高 |
| priority-medium | 🟡 黄 | 優先度: 中 |
| priority-low | 🔵 青 | 優先度: 低 |
| design | 🟣 紫 | カテゴリ: 設計 |
| development | 🟢 緑 | カテゴリ: 開発 |
| testing | 🟡 黄 | カテゴリ: テスト |
| documentation | 🔵 青 | カテゴリ: ドキュメント |
| critical-path | 🔴 赤 | クリティカルパス上のタスク |
| blocked | 🟠 オレンジ | ブロックされているタスク |

### 5. GitHub Projects V2

プロジェクト管理ボード:

- **名前**: "顧問ミドル運用ダッシュボード移行 - プロジェクト管理"
- **カスタムフィールド**: Weight, Effort (Days), Week
- **全Issueが追加済み**

#### 推奨ビュー設定（手動）

Projectsを開いて、以下のビューを作成することをお勧めします：

1. **Board View（ボード）**:
   - Status でグループ化（Todo / In Progress / Done）
   - カンバン形式

2. **Table View（テーブル）**:
   - 全フィールド表示
   - フィルタ・ソート可能

3. **Roadmap View（ロードマップ）**:
   - Start Date と End Date でガントチャート表示
   - タイムライン可視化

4. **Week View（週次ビュー）**:
   - Week フィールドでグループ化
   - 週次計画の確認

## トラブルシューティング

### gh コマンドが見つからない

**エラー**:
```
ERROR: GitHub CLI (gh) が見つかりません。
```

**解決策**:
- [GitHub CLIのインストール](#github-cliのインストール) セクションを参照してインストールしてください

### GitHub CLI認証エラー

**エラー**:
```
ERROR: GitHub CLIの認証が必要です。
```

**解決策**:
```bash
gh auth login
```

を実行して認証してください。

### リポジトリが既に存在する

**エラー**:
```
⚠️  リポジトリ dashboard-migration-project は既に存在する可能性があります。
```

**解決策**:
- 別のリポジトリ名を使用する
- または既存のリポジトリを削除してから再実行

### API レート制限エラー

**エラー**:
```
API rate limit exceeded
```

**解決策**:
- 認証済みの場合、1時間あたり5000リクエストまで可能
- 1時間待ってから再実行
- または一部のタスクのみを同期するようにスクリプトを修正

### Issue作成エラー

**エラー**:
```
ERROR: GitHub CLIコマンド実行エラー: issue create ...
```

**解決策**:
1. ラベルやマイルストーンが正しく作成されているか確認
2. リポジトリの権限を確認（書き込み権限が必要）
3. GitHub APIのステータスを確認: https://www.githubstatus.com/

### Projects作成エラー

**エラー**:
```
ERROR: Projects作成エラー
```

**解決策**:
1. GitHubアカウントでProjectsが有効になっているか確認
2. 認証トークンにproject権限があるか確認
3. 一度 `gh auth refresh -h github.com -s project` を実行

## よくある質問（FAQ）

### Q1: リポジトリをPublicにできますか？

はい。環境変数で指定できます：

```bash
export GITHUB_REPO_VISIBILITY=public
python scripts/sync-github.py
```

### Q2: 同期を複数回実行しても大丈夫ですか？

初回実行後、同じリポジトリ名で再実行すると、以下のようになります：
- リポジトリ: 既存のものをそのまま使用
- ラベル・マイルストーン: 既存のものをスキップ
- Issues: **重複して作成される**（注意）

Issueの重複を避けるため、再実行は推奨しません。

### Q3: OrganizationのリポジトリとしてProjects を作成できますか？

はい。リポジトリ名を `organization/repo-name` の形式で指定してください：

```bash
export GITHUB_REPO_NAME=your-org/dashboard-migration
python scripts/sync-github.py
```

### Q4: tasks.jsonのステータス更新をGitHub Issuesに反映できますか？

はい。別のスクリプト `scripts/update-github-issues.py`（将来実装予定）で、ステータスのみを同期できます。

### Q5: GitHub Issuesの変更をtasks.jsonに反映できますか（双方向同期）？

現在は未対応です。tasks.json → GitHub の一方向同期のみです。
GitHub Issuesで変更した場合は、手動でtasks.jsonも更新してください。

### Q6: 依存関係はGitHub上で視覚化されますか？

GitHub Issuesには依存関係の視覚化機能が標準では提供されていないため、Issue本文にテキストで記載されます。

### Q7: カスタムフィールドの値はスクリプトで自動入力されますか？

Weight, Effort, Week フィールドは作成されますが、値は自動入力されません。
GitHub Projects上で手動で入力するか、GitHub APIを使用して自動化する必要があります（将来対応予定）。

### Q8: Issue番号とTASK-IDの対応表はどこにありますか？

スクリプト実行後、`github-issue-mapping.json` ファイルに保存されます：

```json
{
  "TASK-001": "1",
  "TASK-002": "2",
  ...
}
```

### Q9: GitHub Actionsで自動同期できますか？

可能です。`.github/workflows/sync-github.yml` を作成し、tasks.jsonの変更時に自動実行するように設定できます（将来対応予定）。

### Q10: スクリプトの実行にかかる時間は？

- 25タスク、12マイルストーン、12ラベルの場合: **約5-10分**
- ネットワーク速度とGitHub APIのレスポンス時間に依存

## 次のステップ

同期完了後:

1. **GitHubでProjectsを開く**: ビュー設定とカスタマイズ
2. **Issue番号を確認**: `github-issue-mapping.json` を参照
3. **タスクの進捗を更新**: GitHub IssuesまたはProjectsで管理
4. **週次レポートと連携**: README.mdのGitHub連携セクションを参照

## 参考資料

- [GitHub CLI公式ドキュメント](https://cli.github.com/manual/)
- [GitHub Projects V2ドキュメント](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects)
- [GitHub Issues](https://docs.github.com/en/issues)
- [GitHub Milestones](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/about-milestones)

## サポート

問題が解決しない場合:

1. プロジェクトの [GitHub Issues](https://github.com/your-repo/project-requirements-system/issues) で質問
2. `docs/PROGRESS_REPORT_USAGE.md` も参照してください

---

**最終更新**: 2026-01-15
**バージョン**: 1.0
**作成者**: Claude AI (Sonnet 4.5)
