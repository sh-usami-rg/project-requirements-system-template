# 顧問ミドル運用ダッシュボード移行プロジェクト

Google Spreadsheetsで行っているデータ管理・分析を、BigQueryを基盤としたLooker / Looker Studio環境へ移行し、運用の効率化と分析の高度化を実現するプロジェクトです。

## 🚀 このシステムでできること

このプロジェクト要件システムを使用することで、以下が**完全自動化**されます：

1. **📝 仕様書の精緻化** - `/spec-refine` で対話形式でSPEC.mdを作成
2. **📋 タスク自動分解** - `/plan-project` で25タスクとWBSを自動生成
3. **📅 自動スケジューリング** - `/schedule-tasks` で12週間のスケジュールを作成
4. **🔗 GitHub完全連携** - `/github-sync` でIssues・Milestones・Projects V2・Roadmapを自動作成
5. **🔄 スケジュール変更管理** - 自然言語でスケジュール変更→全ファイル+GitHub自動更新
6. **📊 週次進捗レポート** - 毎週月曜日に自動メール送信

**所要時間**: 仕様書からGitHub Roadmapまで約1.5時間（手作業なら数日）

**詳細ワークフロー**: [docs/PROJECT_WORKFLOW_GUIDE.md](docs/PROJECT_WORKFLOW_GUIDE.md) を参照

---

## プロジェクト概要

- **プロジェクト名**: 顧問ミドル運用ダッシュボード移行
- **期間**: 2026年1月6日 〜 2026年3月30日（12週間）
- **稼働体制**: 1名兼任（50%稼働）
- **総工数**: 28.5人日（199.5時間）
- **目標**: スプレッドシート管理工数を80%削減、リアルタイム分析の実現

## 主要成果物

### Phase 1: 基盤整備と設計（Week 1-4）
- BigQueryテーブルドキュメント
- データマッピング表
- KPI定義書
- LookerML設計書

### Phase 2: 実装と技術検証（Week 5-8）
- Looker Studioダッシュボード×3（経営、稼働状況、財務）
- LookerML基本構造
- GitHubリポジトリ
- トレーニング資料

### Phase 3: フル移行と展開（Week 9-12）
- Lookerダッシュボード×4（中・低優先度）
- システム設計書
- 運用手順書
- 本番リリース

## ファイル構成

```
project-requirements-system/
├── README.md                          # このファイル（プロジェクト概要）
├── QUICK_REFERENCE.md                 # クイックリファレンス（コマンド一覧）
│
├── SPEC.md                            # プロジェクト仕様書（詳細要件）
├── PLAN.md                            # 実行計画書（WBS、工数見積もり）
├── SCHEDULE.md                        # スケジュール管理（週次計画）
│
├── tasks.json                         # タスク定義ファイル（25タスク）
├── schedule.json                      # スケジュールデータ（日付付き）
│
├── docs/                              # ドキュメント
│   ├── PROJECT_WORKFLOW_GUIDE.md     # 完全ワークフローガイド（SPEC→GitHub Roadmap）
│   ├── PROGRESS_REPORT_SETUP.md      # 進捗レポート初期セットアップ手順
│   ├── PROGRESS_REPORT_USAGE.md      # 進捗レポート利用ガイド
│   ├── GITHUB_SYNC_SETUP.md          # GitHub同期セットアップ手順
│   └── SCHEDULE_UPDATE_GUIDE.md      # スケジュール更新ガイド
│
├── scripts/                           # 自動化スクリプト
│   ├── send-progress-report.py       # 週次進捗レポート生成・送信
│   ├── sync-github.py                # GitHub Issues & Projects同期
│   ├── update-schedule.py            # スケジュール更新オーケストレーション
│   └── set-issue-dates.py            # Projects V2日付一括設定
│
└── .github/
    └── workflows/
        └── weekly-progress-report.yml # GitHub Actions（週次レポート自動送信）
```

## クイックスタート

### 0. 完全ワークフローガイドを確認（推奨）

**初めての方は、まずこちらを読んでください**：

📖 **[docs/PROJECT_WORKFLOW_GUIDE.md](docs/PROJECT_WORKFLOW_GUIDE.md)**

このガイドでは、仕様書作成（STEP 1）からGitHub Roadmap連携（STEP 5）まで、完全なエンドツーエンドのワークフローを説明しています。

**所要時間**: 読むだけなら15分、実際に実行すると1.5時間でGitHub Roadmapまで完成します。

**急いでいる方**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) でコマンド一覧を確認

---

### 1. プロジェクト情報の確認

既に作成されているプロジェクトの場合、以下のドキュメントで全体像を把握してください：

```bash
# プロジェクト仕様書を確認
cat SPEC.md

# 実行計画を確認
cat PLAN.md

# スケジュールを確認
cat SCHEDULE.md
```

### 2. 週次進捗レポートのセットアップ

プロジェクト開始前に、進捗レポートの自動送信を設定してください：

```bash
# セットアップ手順を確認
cat docs/PROGRESS_REPORT_SETUP.md
```

**手順サマリー**:
1. SendGridアカウント作成（無料プラン）
2. GitHub Secretsに以下を設定:
   - `SENDGRID_API_KEY`
   - `REPORT_TO_EMAIL`
   - `REPORT_FROM_EMAIL`
3. GitHubにコードをpush
4. GitHub Actionsで手動実行してテスト

### 3. 週次レポートの活用

毎週月曜日 9:00（JST）に進捗レポートがメールで届きます：

```bash
# レポートの見方と活用方法を確認
cat docs/PROGRESS_REPORT_USAGE.md
```

### 4. GitHub Issues & Projectsでの管理（オプション）

tasks.jsonのタスクをGitHub Issues・Projects V2に同期して、GitHub上でプロジェクト管理できます。

#### セットアップ手順

```bash
# 1. セットアップ手順を確認
cat docs/GITHUB_SYNC_SETUP.md

# 2. GitHub CLI認証
gh auth login

# 3. 同期スクリプトを実行
python scripts/sync-github.py
```

#### 作成されるもの

- ✅ **GitHubリポジトリ**（Private）
- ✅ **25個のIssues**（各タスクに対応）
- ✅ **12個のMilestones**（Week 1-12）
- ✅ **ラベル一式**（Phase, Priority, Category等）
- ✅ **GitHub Projects V2**（プロジェクト管理ボード）

#### メリット

- 📊 **視覚的な管理**: ボード・テーブル・ロードマップビューでタスク管理
- 🔗 **依存関係の追跡**: Issue本文で依存タスクを確認
- 📅 **週次マイルストーン**: Week 1-12でタスクをグループ化
- 🏷️ **ラベルフィルタ**: Phase・Priority・Categoryで絞り込み
- 👥 **チーム共有**: GitHubアカウントがあれば誰でもアクセス可能

詳細は [docs/GITHUB_SYNC_SETUP.md](docs/GITHUB_SYNC_SETUP.md) を参照してください。

### 5. スケジュールの変更管理

プロジェクト実行中にタスクの日程変更が必要になった場合、自然言語またはシンプルなコマンドで全てのファイルとGitHubを自動更新できます。

#### 使い方

**インタラクティブモード（推奨）**:
```bash
python3 scripts/update-schedule.py --interactive
```

**コマンドラインモード**:
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

#### 自動更新される項目

✅ **ローカルファイル**:
- `tasks.json` - タスク定義、優先度、依存関係
- `schedule.json` - スケジュールデータ、日付、週次スケジュール
- **`PLAN.md`** - 実行計画書（WBS、工数サマリー、マイルストーン）
- **`SCHEDULE.md`** - 人間が読めるスケジュール（週次計画）
- `github-issue-mapping.json` - Issue番号マッピング（削除時のみ）

✅ **GitHub**:
- GitHub Issues のマイルストーン
- Projects V2 の Start Date / End Date
- 依存タスクの自動調整

✅ **安全機能**:
- 全ファイルの自動バックアップ
- エラー時の自動ロールバック
- 変更サマリーの表示

#### Claude Codeでの自然言語操作

Claude Codeに以下のようにリクエストするだけで、スケジュール変更が完了します：

- 「TASK-007の期限を1週間延ばしたい」
- 「TASK-015を2月10日から開始するように変更したい」
- 「TASK-010は不要になったので削除したい」
- 「TASK-005の優先度を高くしたい」

詳細は [docs/SCHEDULE_UPDATE_GUIDE.md](docs/SCHEDULE_UPDATE_GUIDE.md) を参照してください。

---

## 🤖 利用可能なエージェント（Slash Commands）

このシステムでは、以下のslash commandsを使用してワークフローを実行できます：

| コマンド | 用途 | 所要時間 | 詳細ドキュメント |
|---------|------|---------|----------------|
| `/spec-refine` | SPEC.mdの対話的洗練 | 30-60分 | [PROJECT_WORKFLOW_GUIDE.md](docs/PROJECT_WORKFLOW_GUIDE.md#step-1-仕様書作成spec-refine) |
| `/plan-project` | タスク分解とWBS作成 | 10-15分 | [PROJECT_WORKFLOW_GUIDE.md](docs/PROJECT_WORKFLOW_GUIDE.md#step-2-タスク分解と計画plan-project) |
| `/schedule-tasks` | スケジューリング | 5-10分 | [PROJECT_WORKFLOW_GUIDE.md](docs/PROJECT_WORKFLOW_GUIDE.md#step-3-スケジューリングschedule-tasks) |
| `/github-sync` | GitHub連携 | 5-10分 | [GITHUB_SYNC_SETUP.md](docs/GITHUB_SYNC_SETUP.md) |

**使い方**:
```bash
# Claude Codeで実行
/spec-refine
```

**完全なワークフロー**: [docs/PROJECT_WORKFLOW_GUIDE.md](docs/PROJECT_WORKFLOW_GUIDE.md) を参照

---

## ドキュメントガイド

### 🚀 ワークフローガイド（必読）

| ドキュメント | 目的 | 参照タイミング |
|-------------|------|---------------|
| **[docs/PROJECT_WORKFLOW_GUIDE.md](docs/PROJECT_WORKFLOW_GUIDE.md)** | **仕様書作成からGitHub Roadmap連携までの完全ワークフロー** | **プロジェクト開始時（必読）** |

### 📋 計画・仕様系ドキュメント

| ドキュメント | 目的 | 参照タイミング |
|-------------|------|---------------|
| [SPEC.md](SPEC.md) | プロジェクトの詳細仕様、要件定義、技術要件 | プロジェクト開始時、要件確認時 |
| [PLAN.md](PLAN.md) | WBS、工数見積もり、リスク管理、成果物一覧 | プロジェクト開始時、Phase開始時 |
| [SCHEDULE.md](SCHEDULE.md) | 週次スケジュール、ガントチャート、マイルストーン | 毎週、進捗確認時 |

### 📊 進捗管理系ドキュメント

| ドキュメント | 目的 | 参照タイミング |
|-------------|------|---------------|
| [docs/PROGRESS_REPORT_SETUP.md](docs/PROGRESS_REPORT_SETUP.md) | 週次レポート自動送信の初期設定手順 | プロジェクト開始時（初回のみ）、トラブル時 |
| [docs/PROGRESS_REPORT_USAGE.md](docs/PROGRESS_REPORT_USAGE.md) | レポートの見方、活用方法、ステータス更新手順 | 毎週、レビュー時 |
| [docs/GITHUB_SYNC_SETUP.md](docs/GITHUB_SYNC_SETUP.md) | GitHub Issues & Projects同期セットアップ手順 | プロジェクト開始時（オプション） |
| [docs/SCHEDULE_UPDATE_GUIDE.md](docs/SCHEDULE_UPDATE_GUIDE.md) | スケジュール変更の自動更新手順、使用例 | スケジュール変更時、遅延発生時 |

### 📁 データファイル

| ファイル | 目的 | 更新タイミング |
|---------|------|---------------|
| [tasks.json](tasks.json) | 25タスクの定義、ステータス、依存関係 | タスク着手時・完了時に更新 |
| [schedule.json](schedule.json) | 週次スケジュール、日付、進捗率 | 通常は更新不要（自動生成） |

## 使い方の流れ

### プロジェクト開始前

```
1. SPEC.md を読む
   ↓
2. PLAN.md を読む
   ↓
3. SCHEDULE.md を読む
   ↓
4. 週次進捗レポートをセットアップ (docs/PROGRESS_REPORT_SETUP.md)
   ↓
5. GitHub Issues & Projectsセットアップ (オプション・推奨)
   ↓
6. プロジェクトキックオフ
```

### プロジェクト実行中（毎週のサイクル）

```
月曜日:
  09:00 - 週次進捗レポートがメールで届く
          ↓
  10:00 - 週次レビューミーティング
          ├─ レポートを元に進捗確認
          ├─ 課題・リスクの洗い出し
          └─ 来週の予定確認

火〜金曜日:
  - タスクを実行
  - タスク着手時: tasks.json のステータスを "in_progress" に更新
  - タスク完了時: tasks.json のステータスを "done" に更新
  - git commit & push （重要！）

金曜日:
  - 週の振り返り
  - tasks.json のステータス最終確認
  - 来週の準備
```

### Phase終了時

```
Phase 1終了 (Week 4: 1/31):
  ├─ 成果物レビュー
  ├─ マイルストーン達成確認
  └─ Phase 2移行判定

Phase 2終了 (Week 9: 3/5):
  ├─ 成果物レビュー
  ├─ ユーザーレビュー
  └─ Phase 3移行判定

Phase 3終了 (Week 12: 3/30):
  ├─ 最終成果物レビュー
  ├─ 本番リリース
  └─ プロジェクト完了判定
```

## タスクステータスの更新方法

進捗レポートの精度を保つため、タスクのステータスを適切に更新してください。

### 更新手順

```bash
# 1. tasks.json を編集
code tasks.json

# 2. タスクのステータスを変更
#    "status": "pending"      # 未着手
#    "status": "in_progress"  # 進行中
#    "status": "done"         # 完了

# 3. GitHubにプッシュ（重要！）
git add tasks.json
git commit -m "Update TASK-XXX status to done"
git push origin main
```

**例**: TASK-001を完了にする場合

```json
{
  "id": "TASK-001",
  "title": "既存BigQuery DWHテーブルの整合性確認",
  "status": "done",  ← "in_progress" から "done" に変更
  ...
}
```

詳細は [docs/PROGRESS_REPORT_USAGE.md](docs/PROGRESS_REPORT_USAGE.md) を参照してください。

## 週次進捗レポートについて

### レポート内容

毎週月曜日の朝9時に以下の情報がメールで届きます：

- ✅ 予定進捗率 vs 実績進捗率
- ✅ ステータス判定（🟢予定通り / 🟡やや遅延 / 🔴要注意）
- ✅ 今週完了したタスク
- ✅ 進行中のタスク
- ✅ 来週予定のタスク

### ステータスの意味

| ステータス | 意味 | 対応 |
|-----------|------|------|
| 🟢 **予定通り** | 実績 ≥ 予定 | 現在のペースを維持 |
| 🟡 **やや遅延** | 予定 - 5% ≤ 実績 < 予定 | 原因分析、リカバリープラン策定 |
| 🔴 **要注意** | 実績 < 予定 - 5% | 緊急対応、エスカレーション |

詳細は [docs/PROGRESS_REPORT_USAGE.md](docs/PROGRESS_REPORT_USAGE.md) を参照してください。

## プロジェクトワークフロー図

```
┌─────────────────────────────────────────────────────────────┐
│                    プロジェクト開始                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  SPEC.md を読んで       │
        │  プロジェクト理解       │
        └────────┬────────────────┘
                 │
                 ▼
        ┌─────────────────────────┐
        │  PLAN.md & SCHEDULE.md  │
        │  で計画を確認           │
        └────────┬────────────────┘
                 │
                 ▼
        ┌─────────────────────────┐
        │  週次レポート           │
        │  セットアップ           │
        └────────┬────────────────┘
                 │
                 ▼
        ┌─────────────────────────┐
        │  プロジェクト実行       │
        │  (Week 1-12)            │
        └────────┬────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
  ┌─────────┐      ┌─────────────┐
  │ タスク  │      │ 週次レポート │
  │ 実行    │◄────►│ 確認・レビュー│
  └─────────┘      └─────────────┘
        │                 │
        │    tasks.json   │
        │    ステータス    │
        │    更新         │
        │                 │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────────────┐
        │  Phase 終了レビュー     │
        │  (Week 4, 9, 12)        │
        └────────┬────────────────┘
                 │
                 ▼
        ┌─────────────────────────┐
        │  プロジェクト完了       │
        │  (2026-03-30)           │
        └─────────────────────────┘
```

## 主要マイルストーン

| # | 日付 | マイルストーン | 成果物 |
|---|------|---------------|--------|
| M1 | 2026-01-31 | Phase 1完了: 基盤整備・設計完了 | BigQueryドキュメント、マッピング表、KPI定義書、LookerML設計書 |
| M2 | 2026-03-05 | Phase 2完了: Looker Studio高優先度DB完成 | ダッシュボード×3、LookerML基本構造、開発ガイドライン |
| M3 | 2026-03-30 | Phase 3完了: 全ダッシュボード完成、本番リリース | ダッシュボード×4、設計書、運用手順書、本番環境 |

## クリティカルパス（要注意タスク）

以下のタスクは、プロジェクト納期に直接影響します。優先的に進めてください。

```
TASK-001 → TASK-005 → TASK-006 → TASK-007 → TASK-008
   ↓
TASK-015
   ↓
TASK-018
   ↓
TASK-022 → TASK-023 → TASK-024 → TASK-025
```

- **TASK-007**: KPI定義・分析軸の明確化（2.5日）⚠️
- **TASK-008**: LookerML設計方針策定（2.5日）⚠️
- **TASK-015**: LookerML基本構造実装（1.5日）⚠️

## リスク管理

| リスク | 影響度 | 発生確率 | 対策 |
|--------|-------|---------|------|
| LookerML習熟度不足 | 高 | 中 | Phase 2でトライアル期間設定、外部トレーニング活用 |
| データ品質問題 | 高 | 中 | Phase 1で徹底的なデータ検証、自動チェック導入 |
| ユーザー要件変更 | 中 | 高 | 優先度による段階的実装、変更管理プロセス明確化 |
| 50%稼働による遅延 | 高 | 中 | クリティカルパス厳格管理、早期リスク検知 |

## GitHub連携（自動化）

### 週次進捗レポート自動送信

GitHub Actionsにより、以下が自動実行されます：

- **実行タイミング**: 毎週月曜日 00:00 UTC（日本時間 9:00）
- **実行内容**:
  1. tasks.json と schedule.json を読み込み
  2. 進捗率を計算（完了タスクのWeight合計）
  3. HTML形式のレポートを生成
  4. SendGrid APIでメール送信

### 手動実行方法

```bash
# GitHub Actionsで手動実行
# 1. リポジトリの Actions タブを開く
# 2. "Weekly Progress Report" を選択
# 3. "Run workflow" をクリック

# ローカルで実行
cd /path/to/project-requirements-system
export SENDGRID_API_KEY="your-api-key"
export REPORT_TO_EMAIL="your-email@example.com"
export REPORT_FROM_EMAIL="noreply@yourdomain.com"
python scripts/send-progress-report.py
```

## よくある質問（FAQ）

### Q1: tasks.jsonを更新したのにレポートに反映されない

**A**: GitHubにプッシュする必要があります。

```bash
git add tasks.json
git commit -m "Update task status"
git push origin main
```

次回の自動実行時（次の月曜日）に反映されます。今すぐ確認したい場合は、GitHub Actionsで手動実行してください。

### Q2: レポートが届きません

**A**: 以下を確認してください：
1. 迷惑メールフォルダを確認
2. GitHub Secretsの設定を確認（SENDGRID_API_KEY, REPORT_TO_EMAIL, REPORT_FROM_EMAIL）
3. GitHub Actionsの実行ログを確認

詳細は [docs/PROGRESS_REPORT_SETUP.md](docs/PROGRESS_REPORT_SETUP.md) のトラブルシューティングを参照してください。

### Q3: 進捗率の計算方法は？

**A**: 完了したタスク（status: "done"）のWeight合計が実績進捗率です。

例:
- TASK-001 (Weight: 2, status: "done")
- TASK-002 (Weight: 5, status: "done")
- → 実績進捗率 = 2 + 5 = 7%

### Q4: スケジュールを変更できますか？

**A**: はい。`update-schedule.py` スクリプトを使用することで、全てのファイルとGitHubを自動的に更新できます。

```bash
# インタラクティブモードで操作
python3 scripts/update-schedule.py --interactive

# または、直接コマンドで指定
python3 scripts/update-schedule.py --task TASK-007 --extend-deadline 7
```

詳細は [docs/SCHEDULE_UPDATE_GUIDE.md](docs/SCHEDULE_UPDATE_GUIDE.md) を参照してください。

**注意**: 手動でファイルを編集する場合は、以下の全てを更新する必要があります：
- tasks.json、schedule.json、**PLAN.md**、SCHEDULE.md、github-issue-mapping.json
- GitHub Issues（マイルストーン）、Projects V2（Start Date / End Date）

スクリプトを使用することで、更新漏れを防ぐことができます。特にPLAN.mdはWBS、工数サマリー、マイルストーンなど多くのセクションがあるため、手動更新は困難です。

### Q5: プロジェクト終了後、週次レポートは停止されますか？

**A**: いいえ。GitHub Actionsは設定を無効化するまで継続します。

プロジェクト終了後は：
1. `.github/workflows/weekly-progress-report.yml` を削除、または
2. GitHub Actionsタブからワークフローを無効化

## トラブルシューティング

問題が発生した場合は、以下のドキュメントを参照してください：

- 週次レポートのセットアップ問題: [docs/PROGRESS_REPORT_SETUP.md](docs/PROGRESS_REPORT_SETUP.md)
- レポートの見方や活用方法: [docs/PROGRESS_REPORT_USAGE.md](docs/PROGRESS_REPORT_USAGE.md)
- タスク管理の問題: [SCHEDULE.md](SCHEDULE.md)

## コントリビューション

このプロジェクトは顧問名鑑サービスの内部プロジェクトです。

変更を行う場合:
1. ブランチを作成
2. 変更をコミット
3. プルリクエストを作成
4. レビュー後にマージ

## ライセンス

社内プロジェクト - All Rights Reserved

## サポート・お問い合わせ

- **プロジェクトマネージャー**: [未定]
- **BI Engineer**: [未定]
- **Slack**: #project-dashboard-migration
- **GitHub Issues**: 問題報告・質問はこちら

## バージョン履歴

| バージョン | 日付 | 変更内容 |
|-----------|------|---------|
| 1.1 | 2026-01-15 | 完全ワークフローガイド追加、PLAN.md自動更新機能追加 |
| 1.0 | 2026-01-15 | 初版作成 |

---

**最終更新**: 2026-01-15
**作成者**: Claude AI (Sonnet 4.5)
**プロジェクト開始**: 2026-01-06
**プロジェクト終了予定**: 2026-03-30
