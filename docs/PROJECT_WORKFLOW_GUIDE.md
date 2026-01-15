# プロジェクト要件システム - 完全ワークフローガイド

## 📋 概要

このガイドでは、SPEC.mdの作成からGitHub Roadmap連携、スケジュール更新までの**完全なエンドツーエンドワークフロー**を説明します。

### このシステムで実現できること

✅ **仕様書の作成と洗練** - 対話形式でSPEC.mdを精緻化
✅ **自動タスク分解** - SPEC.mdから25個のタスク（tasks.json）を自動生成
✅ **自動スケジューリング** - タスクから12週間のスケジュール（schedule.json, SCHEDULE.md）を生成
✅ **GitHub完全連携** - Issues、Milestones、Projects V2、Roadmapビューを自動作成
✅ **スケジュール変更管理** - 自然言語でのスケジュール変更と全ファイル自動更新
✅ **週次進捗レポート** - 自動メール送信とステータス判定

---

## 🚀 完全ワークフロー図

```
┌─────────────────────────────────────────────────────────────────┐
│                     STEP 1: 仕様書作成                            │
│                   /spec-refine コマンド                           │
│                                                                   │
│  入力: プロジェクト概要、要件、背景情報                              │
│  出力: SPEC.md（精緻化された仕様書）                               │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  STEP 2: タスク分解と計画                          │
│                  /plan-project コマンド                           │
│                                                                   │
│  入力: SPEC.md                                                    │
│  出力: tasks.json（25タスク）                                      │
│       PLAN.md（WBS、工数見積もり、リスク管理）                      │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  STEP 3: スケジューリング                          │
│                 /schedule-tasks コマンド                          │
│                                                                   │
│  入力: tasks.json                                                 │
│  出力: schedule.json（日付付きタスク、週次スケジュール）             │
│       SCHEDULE.md（人間が読めるスケジュール）                       │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  STEP 4: GitHub連携                               │
│                  /github-sync コマンド                            │
│                                                                   │
│  入力: tasks.json, schedule.json                                  │
│  出力: ✓ GitHubリポジトリ                                          │
│       ✓ 25個のIssues                                              │
│       ✓ 12個のMilestones（Week 1-12）                             │
│       ✓ ラベル一式（Phase, Priority, Category）                    │
│       ✓ Projects V2プロジェクトボード                              │
│       ✓ github-issue-mapping.json                                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│               STEP 5: Roadmap設定（手動）                          │
│                                                                   │
│  1. GitHub Projects V2を開く                                      │
│  2. カスタムフィールド追加:                                         │
│     - Start Date（Date型）                                        │
│     - End Date（Date型）                                          │
│  3. Roadmapビューを作成                                            │
│  4. scripts/set-issue-dates.py を実行して日付を一括設定            │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 6: 週次進捗レポート設定                          │
│                                                                   │
│  1. SendGridアカウント作成                                         │
│  2. GitHub Secrets設定（API Key、メールアドレス）                   │
│  3. GitHub Actionsで自動実行開始                                   │
│     - 毎週月曜日 9:00（JST）に自動送信                             │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│          STEP 7: プロジェクト実行とスケジュール変更                 │
│                                                                   │
│  - タスク実行とステータス更新（tasks.json）                         │
│  - スケジュール変更が必要になったら:                                │
│    python3 scripts/update-schedule.py --interactive               │
│                                                                   │
│  自動更新: tasks.json, schedule.json, PLAN.md, SCHEDULE.md,       │
│           GitHub Issues, Projects V2                              │
└───────────────────────────────────────────────────────────────────┘
```

---

## 📖 各ステップの詳細

### STEP 1: 仕様書作成（/spec-refine）

**目的**: プロジェクトの仕様書（SPEC.md）を対話形式で精緻化する

**コマンド**:
```bash
/spec-refine
```

**実行内容**:
1. 既存のSPEC.mdを読み込む（存在する場合）
2. 対話形式で以下の情報を収集・改善:
   - プロジェクト概要と目的
   - 背景と課題
   - 機能要件と非機能要件
   - 技術スタック
   - 制約事項
   - 成功基準
3. SPEC.mdを生成・更新

**出力ファイル**:
- `SPEC.md` - 精緻化された仕様書

**所要時間**: 30-60分（初回）、10-20分（更新）

**Tips**:
- 複数回実行して段階的に仕様を洗練できます
- 曖昧な要件があれば、エージェントが質問してくれます
- 既存のSPEC.mdがあれば、それをベースに改善されます

---

### STEP 2: タスク分解と計画（/plan-project）

**目的**: SPEC.mdから実行可能なタスクとWBSを生成する

**コマンド**:
```bash
/plan-project
```

**前提条件**:
- ✅ SPEC.mdが存在すること

**実行内容**:
1. SPEC.mdを解析
2. プロジェクトをPhase別に分割（Phase 1-3）
3. 各Phaseをタスクに分解（合計25タスク）
4. タスクごとに以下を設定:
   - タスクID（TASK-001〜TASK-025）
   - タイトル、説明
   - Phase、カテゴリ（design/development/testing/documentation）
   - 優先度（high/medium/low）
   - 工数（日数と時間）
   - Weight（進捗率への貢献度、合計100）
   - 依存関係
5. クリティカルパス分析
6. リスク管理計画

**出力ファイル**:
- `tasks.json` - 25タスクの完全定義
- `PLAN.md` - WBS、工数見積もり、リスク管理

**所要時間**: 10-15分

**Tips**:
- タスク数、工数、Weightは自動で最適化されます
- 依存関係も自動で設定されます
- PLAN.mdは後でスケジュール変更時に自動更新されます

---

### STEP 3: スケジューリング（/schedule-tasks）

**目的**: タスクに日付を割り当て、週次スケジュールを作成する

**コマンド**:
```bash
/schedule-tasks
```

**前提条件**:
- ✅ tasks.jsonが存在すること

**実行内容**:
1. プロジェクト開始日を設定（対話形式）
2. タスクの依存関係を考慮して日付を割り当て
3. 週次スケジュールを生成（Week 1-12）
4. 各週の累積進捗率を計算
5. クリティカルパスを特定

**出力ファイル**:
- `schedule.json` - 日付付きタスク、週次スケジュール、クリティカルパス
- `SCHEDULE.md` - 人間が読めるスケジュール（週次計画）

**所要時間**: 5-10分

**対話内容の例**:
```
プロジェクト開始日を入力してください (YYYY-MM-DD): 2026-01-06
並行実行可能なタスク数（デフォルト: 2）: 2
バッファ日数（デフォルト: 0）: 0
```

**Tips**:
- 開始日以外はデフォルト値で問題ありません
- schedule.jsonは後でスケジュール変更時に自動更新されます

---

### STEP 4: GitHub連携（/github-sync）

**目的**: tasks.jsonとschedule.jsonをGitHub Issues・Projects V2に同期する

**コマンド**:
```bash
/github-sync
```

**前提条件**:
- ✅ tasks.jsonとschedule.jsonが存在すること
- ✅ GitHub CLI（gh）がインストールされていること
- ✅ `gh auth login` で認証済みであること

**実行内容**:
1. GitHubリポジトリを作成（新規 or 既存）
2. ラベルを作成:
   - `phase-1`, `phase-2`, `phase-3`
   - `priority-high`, `priority-medium`, `priority-low`
   - `design`, `development`, `testing`, `documentation`
   - `critical-path`
3. マイルストーンを作成（Week 1-12）
4. Issues作成（25個）
   - タイトル: `[TASK-001] タスク名`
   - 本文: タスク概要、情報、スケジュール、依存関係
   - ラベル: Phase, Priority, Category
   - マイルストーン: Week番号
5. Projects V2作成
6. 全IssueをProjects V2に追加
7. カスタムフィールド作成（Weight, Effort, Week）

**出力**:
- ✅ GitHubリポジトリ: `https://github.com/{owner}/{repo}`
- ✅ 25個のIssues
- ✅ 12個のMilestones
- ✅ Projects V2: `https://github.com/users/{owner}/projects/{number}`
- ✅ `github-issue-mapping.json` - TASK-ID → Issue番号のマッピング

**所要時間**: 5-10分

**Tips**:
- リポジトリ名を入力すると、自動で作成されます
- Private/Publicを選択できます
- 既存リポジトリを指定することも可能です

**詳細ドキュメント**: `docs/GITHUB_SYNC_SETUP.md`

---

### STEP 5: Roadmap設定（手動＋自動）

**目的**: GitHub Projects V2にRoadmapビューを作成し、ガントチャートで可視化する

#### 5-1. カスタムフィールド追加（手動）

1. GitHub Projects V2を開く
   - URL: `https://github.com/users/{owner}/projects/{number}`

2. 右上の「...」→「Settings」をクリック

3. 「+ New field」をクリックして以下を作成:
   - **Field name**: `Start Date`
   - **Field type**: `Date`

4. 同様に「End Date」も作成

#### 5-2. Roadmapビュー作成（手動）

1. Projects V2で「+ New view」をクリック

2. View typeで「Roadmap」を選択

3. 以下の設定:
   - **Start date field**: `Start Date`
   - **End date field**: `End Date`
   - **Zoom level**: Week or Month

4. ビュー名を「Roadmap」に設定

#### 5-3. 日付の一括設定（自動）

```bash
# Projects V2のProject Numberを確認（URLの末尾の数字）
# 例: https://github.com/users/sh-usami-rg/projects/3 → Project Number = 3

python3 scripts/set-issue-dates.py --project-number=3
```

**実行内容**:
- schedule.jsonから各タスクの開始日・終了日を取得
- GitHub Projects V2の各IssueにStart Date / End Dateを設定
- 25個すべてのIssueに日付を一括設定

**結果**:
- ✅ Roadmapビューでガントチャートが表示される
- ✅ タスクの依存関係が視覚的に確認できる
- ✅ プロジェクト全体の期間が一目でわかる

**所要時間**: 5-10分

**詳細ドキュメント**: `docs/GITHUB_SYNC_SETUP.md`

---

### STEP 6: 週次進捗レポート設定

**目的**: 毎週月曜日に進捗レポートをメールで自動送信する

#### 6-1. SendGridアカウント作成

1. https://sendgrid.com/ にアクセス
2. 無料プランでアカウント作成（月100通まで無料）
3. API Keyを作成（"Mail Send" 権限）

#### 6-2. GitHub Secrets設定

1. GitHubリポジトリの「Settings」→「Secrets and variables」→「Actions」

2. 以下の3つのSecretを追加:
   - `SENDGRID_API_KEY`: SendGridのAPI Key
   - `REPORT_TO_EMAIL`: レポート送信先メールアドレス
   - `REPORT_FROM_EMAIL`: 送信元メールアドレス（SendGridで認証済み）

#### 6-3. GitHub Actionsの有効化

1. リポジトリをGitHubにプッシュ（`.github/workflows/weekly-progress-report.yml`を含む）

2. GitHub Actionsが自動的に有効化される

3. 手動テスト実行:
   - リポジトリの「Actions」タブ
   - 「Weekly Progress Report」を選択
   - 「Run workflow」をクリック

#### 6-4. レポート内容

毎週月曜日 9:00（JST）に以下の情報がメールで届きます:

- ✅ 予定進捗率 vs 実績進捗率
- ✅ ステータス判定（🟢予定通り / 🟡やや遅延 / 🔴要注意）
- ✅ 今週完了したタスク
- ✅ 進行中のタスク
- ✅ 来週予定のタスク
- ✅ 週次スケジュール

**所要時間**: 20-30分（初回のみ）

**詳細ドキュメント**:
- `docs/PROGRESS_REPORT_SETUP.md`
- `docs/PROGRESS_REPORT_USAGE.md`

---

### STEP 7: プロジェクト実行とスケジュール変更

#### 7-1. タスクステータスの更新

**日常的な作業**:
1. タスクを開始したら `tasks.json` のステータスを `"in_progress"` に更新
2. タスクを完了したら `tasks.json` のステータスを `"done"` に更新
3. GitHubにプッシュ

```bash
# tasks.jsonを編集
code tasks.json

# GitHubにプッシュ
git add tasks.json
git commit -m "Update TASK-007 status to done"
git push origin main
```

**次回の週次レポート**で実績進捗率が自動更新されます。

#### 7-2. スケジュール変更（自然言語 or コマンド）

**状況**: タスクが遅延している、または開始日を変更したい

**方法1: 自然言語でClaude Codeに依頼**

Claude Codeに以下のように依頼するだけで、全ファイルとGitHubが自動更新されます:

- 「TASK-007の期限を1週間延ばしたい」
- 「TASK-015を2月10日から開始するように変更したい」
- 「TASK-010は不要になったので削除したい」
- 「TASK-005の優先度を高くしたい」

**方法2: インタラクティブモード**

```bash
python3 scripts/update-schedule.py --interactive
```

メニューから操作を選択:
```
実行する操作を選択してください:
  1. タスクの期限を延長
  2. タスクの開始日を変更
  3. タスクを削除
  4. タスクの優先度を変更
  5. 終了

選択 (1-5): 1
タスクID (例: TASK-007): TASK-007
延長する日数: 7
```

**方法3: コマンドラインモード**

```bash
# タスクの期限を7日延長
python3 scripts/update-schedule.py --task TASK-007 --extend-deadline 7

# タスクの開始日を変更
python3 scripts/update-schedule.py --task TASK-015 --start-date 2026-02-10

# タスクを削除
python3 scripts/update-schedule.py --task TASK-010 --action delete

# タスクの優先度を変更
python3 scripts/update-schedule.py --task TASK-005 --priority high
```

**自動更新されるもの（更新漏れゼロ！）**:

| ファイル/システム | 更新内容 |
|------------------|---------|
| `tasks.json` | タスク定義、優先度、依存関係 |
| `schedule.json` | 開始日、終了日、週番号、週次スケジュール |
| **`PLAN.md`** | WBS、タスク一覧、工数サマリー、マイルストーン |
| **`SCHEDULE.md`** | 週次スケジュール、タスク詳細 |
| `github-issue-mapping.json` | タスク削除時にマッピング削除 |
| GitHub Issues | マイルストーンの更新 |
| GitHub Projects V2 | Start Date / End Dateフィールドの更新 |
| **依存タスク** | 自動的に連鎖延長 |

**所要時間**: 1-2分

**詳細ドキュメント**: `docs/SCHEDULE_UPDATE_GUIDE.md`

---

## 🎯 完全な実行例（エンドツーエンド）

### シナリオ: 新規プロジェクトの立ち上げ

```bash
# ============================================
# STEP 1: 仕様書作成
# ============================================
/spec-refine
# → 対話形式でSPEC.mdを作成（30分）

# ============================================
# STEP 2: タスク分解と計画
# ============================================
/plan-project
# → tasks.json と PLAN.md を生成（10分）

# ============================================
# STEP 3: スケジューリング
# ============================================
/schedule-tasks
# → schedule.json と SCHEDULE.md を生成（5分）

# ============================================
# STEP 4: GitHub連携
# ============================================
/github-sync
# → GitHubリポジトリ、Issues、Projects V2を作成（10分）

# ============================================
# STEP 5: Roadmap設定
# ============================================
# 1. GitHub Projects V2でStart Date / End Dateフィールドを追加（手動、2分）
# 2. Roadmapビューを作成（手動、1分）
# 3. 日付を一括設定:
python3 scripts/set-issue-dates.py --project-number=3
# → 全Issueに日付設定（2分）

# ============================================
# STEP 6: 週次レポート設定
# ============================================
# 1. SendGridアカウント作成（15分）
# 2. GitHub Secrets設定（5分）
# 3. GitHubにプッシュして自動実行開始（1分）

# ============================================
# STEP 7: プロジェクト実行
# ============================================
# タスクを実行してステータス更新
code tasks.json  # status を "done" に変更
git add tasks.json
git commit -m "Complete TASK-001"
git push

# スケジュール変更が必要になったら
python3 scripts/update-schedule.py --task TASK-007 --extend-deadline 7
```

**総所要時間**: 約1.5時間（初回セットアップ）

---

## 📊 各ステップのコマンド一覧

| ステップ | コマンド | 所要時間 | 出力 |
|---------|---------|---------|------|
| 1. 仕様書作成 | `/spec-refine` | 30-60分 | SPEC.md |
| 2. タスク分解 | `/plan-project` | 10-15分 | tasks.json, PLAN.md |
| 3. スケジューリング | `/schedule-tasks` | 5-10分 | schedule.json, SCHEDULE.md |
| 4. GitHub連携 | `/github-sync` | 5-10分 | リポジトリ, Issues, Projects V2 |
| 5. Roadmap設定 | 手動+スクリプト | 5-10分 | Roadmapビュー、日付設定 |
| 6. レポート設定 | 手動設定 | 20-30分 | 週次自動メール |
| 7. スケジュール変更 | `update-schedule.py` | 1-2分 | 全ファイル+GitHub更新 |

---

## 🔧 使用するツールとスクリプト

### Slash Commands（エージェント）

| コマンド | 用途 | ディレクトリ |
|---------|------|-------------|
| `/spec-refine` | 仕様書の対話的洗練 | `.claude/commands/spec-refine.md` |
| `/plan-project` | タスク分解とWBS作成 | `.claude/commands/plan-project.md` |
| `/schedule-tasks` | スケジューリング | `.claude/commands/schedule-tasks.md` |
| `/github-sync` | GitHub連携 | `.claude/commands/github-sync.md` |

### Pythonスクリプト

| スクリプト | 用途 | 実行タイミング |
|-----------|------|---------------|
| `scripts/sync-github.py` | GitHub初回同期 | STEP 4 |
| `scripts/set-issue-dates.py` | Projects V2日付一括設定 | STEP 5 |
| `scripts/update-schedule.py` | スケジュール変更 | プロジェクト実行中 |
| `scripts/send-progress-report.py` | 週次レポート送信 | 毎週月曜日（自動） |

### GitHub Actions

| ワークフロー | 用途 | スケジュール |
|-------------|------|-------------|
| `.github/workflows/weekly-progress-report.yml` | 週次レポート自動送信 | 毎週月曜日 00:00 UTC |

---

## 📁 生成されるファイル一覧

### プロジェクト計画ファイル

| ファイル | 説明 | 生成タイミング |
|---------|------|---------------|
| `SPEC.md` | プロジェクト仕様書 | STEP 1 |
| `tasks.json` | 25タスクの完全定義 | STEP 2 |
| `PLAN.md` | WBS、工数見積もり、リスク管理 | STEP 2（STEP 7で自動更新） |
| `schedule.json` | 日付付きタスク、週次スケジュール | STEP 3（STEP 7で自動更新） |
| `SCHEDULE.md` | 人間が読めるスケジュール | STEP 3（STEP 7で自動更新） |
| `github-issue-mapping.json` | TASK-ID → Issue番号マッピング | STEP 4 |

### ドキュメント

| ファイル | 説明 |
|---------|------|
| `README.md` | プロジェクト概要 |
| `docs/GITHUB_SYNC_SETUP.md` | GitHub連携セットアップ手順 |
| `docs/PROGRESS_REPORT_SETUP.md` | 週次レポート初期設定 |
| `docs/PROGRESS_REPORT_USAGE.md` | 週次レポート利用ガイド |
| `docs/SCHEDULE_UPDATE_GUIDE.md` | スケジュール更新ガイド |
| `docs/PROJECT_WORKFLOW_GUIDE.md` | このファイル |

---

## 💡 ベストプラクティス

### 1. 仕様書作成時

✅ **Do**:
- 複数回 `/spec-refine` を実行して段階的に洗練する
- 曖昧な要件はエージェントに質問してもらう
- 技術スタック、制約事項を明確にする

❌ **Don't**:
- 一度で完璧な仕様書を作ろうとしない
- 要件が曖昧なままタスク化に進まない

### 2. タスク分解時

✅ **Do**:
- 自動生成されたタスクを確認する
- 必要に応じてtasks.jsonを微調整する
- 依存関係が正しいか確認する

❌ **Don't**:
- タスク数や工数を手動で大幅に変更しない（バランスが崩れる）

### 3. スケジューリング時

✅ **Do**:
- 現実的な開始日を設定する
- 並行実行数は稼働体制に合わせる（1名なら1-2）
- バッファ日数は保守的に設定する

❌ **Don't**:
- 過度に楽観的な日程を設定しない

### 4. GitHub連携時

✅ **Do**:
- Private リポジトリを使用する（機密情報保護）
- Projects V2のカスタムフィールドは必ず作成する
- Roadmapビューで全体像を確認する

❌ **Don't**:
- GitHub Issues を手動で大量編集しない（スクリプトを使う）

### 5. プロジェクト実行時

✅ **Do**:
- タスクのステータスをこまめに更新する
- 週次レポートを毎週確認する
- 遅延が発生したら早めにスケジュール調整する
- スケジュール変更は `update-schedule.py` を使う

❌ **Don't**:
- tasks.jsonを手動編集してGitHubと不整合にしない
- PLAN.mdやSCHEDULE.mdを手動編集しない（自動生成される）

---

## 🆘 トラブルシューティング

### Q1: `/spec-refine` が動作しない

**A**: Slash commandが正しく登録されているか確認:
```bash
ls -la .claude/commands/spec-refine.md
```

### Q2: GitHub CLI認証エラー

**A**: 再認証を実行:
```bash
gh auth login
```

### Q3: Projects V2に日付が設定されない

**A**: 以下を確認:
1. Projects V2に「Start Date」「End Date」フィールドが存在するか
2. github-issue-mapping.jsonにタスクのマッピングがあるか
3. Project Numberが正しいか

### Q4: 週次レポートが届かない

**A**: 以下を確認:
1. SendGrid API Keyが有効か
2. GitHub Secretsが正しく設定されているか
3. メールアドレスがSendGridで認証済みか
4. 迷惑メールフォルダを確認

### Q5: スケジュール変更後にエラー

**A**: バックアップから復元:
```bash
# バックアップは .backups/ に保存されている
ls -la .backups/
# 最新のバックアップから復元
cp .backups/20260115_143052/tasks.json ./
```

---

## 📚 関連ドキュメント

| ドキュメント | 説明 |
|-------------|------|
| [README.md](../README.md) | プロジェクト概要とクイックスタート |
| [SPEC.md](../SPEC.md) | プロジェクト仕様書（例） |
| [PLAN.md](../PLAN.md) | 実行計画書（例） |
| [SCHEDULE.md](../SCHEDULE.md) | スケジュール（例） |
| [GITHUB_SYNC_SETUP.md](GITHUB_SYNC_SETUP.md) | GitHub連携詳細手順 |
| [PROGRESS_REPORT_SETUP.md](PROGRESS_REPORT_SETUP.md) | 週次レポート初期設定 |
| [PROGRESS_REPORT_USAGE.md](PROGRESS_REPORT_USAGE.md) | 週次レポート利用方法 |
| [SCHEDULE_UPDATE_GUIDE.md](SCHEDULE_UPDATE_GUIDE.md) | スケジュール更新詳細ガイド |

---

## 🎓 まとめ

このプロジェクト要件システムを使用することで：

✅ **効率化**: 仕様書からGitHub Roadmapまで自動生成（手作業なら数日 → 1.5時間）
✅ **一貫性**: 全ファイルとGitHubが常に同期（更新漏れゼロ）
✅ **可視性**: Roadmapビューでプロジェクト全体を視覚化
✅ **柔軟性**: 自然言語でスケジュール変更が可能
✅ **自動化**: 週次レポートが自動送信される
✅ **安全性**: 自動バックアップとロールバック機能

**このワークフローにより、プロジェクト管理の時間を80%削減し、計画の精度を大幅に向上できます。**

---

**最終更新**: 2026-01-15
**バージョン**: 1.0
**作成者**: Claude AI (Sonnet 4.5)
