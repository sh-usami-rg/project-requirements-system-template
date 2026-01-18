# Project Requirements System Template

プロジェクト要件整理から計画自動化、GitHub連携、ガントチャート管理をテンプレート化したシステムです。

## 🚀 このシステムでできること

このプロジェクト要件システムを使用することで、以下が**完全自動化**されます：

1. **📝 仕様書の精緻化** - `/spec-refine` で対話形式でSPEC.mdを作成
2. **📋 タスク自動分解** - `/plan-project` で25タスクとWBSを自動生成
3. **📅 自動スケジューリング** - `/schedule-tasks` で12週間のスケジュールを作成
4. **🔗 GitHub完全連携** - `/github-sync` でIssues・Milestones・Projects V2・Roadmapを自動作成
5. **🔄 スケジュール変更管理** - 自然言語でスケジュール変更→全ファイル+GitHub自動更新

**所要時間**: 仕様書からGitHub Roadmapまで約1.5時間（手作業なら数日）

**詳細ワークフロー**: [docs/PROJECT_WORKFLOW_GUIDE.md](docs/PROJECT_WORKFLOW_GUIDE.md) を参照

---

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
│   ├── GITHUB_SYNC_SETUP.md          # GitHub同期セットアップ手順
│   ├── SCHEDULE_UPDATE_GUIDE.md      # スケジュール更新ガイド
│   ├── SYSTEM_MANAGEMENT_GUIDE.md    # システム管理ガイド
│   ├── MID_CATEGORY_GUIDE.md         # 中カテゴリ管理ガイド
│   └── SCHEMA.md                     # tasks.jsonスキーマ定義
│
├── scripts/                           # 自動化スクリプト
│   ├── sync-github.py                # GitHub Issues & Projects同期
│   ├── update-schedule.py            # スケジュール更新オーケストレーション
│   ├── set-issue-dates.py            # Projects V2日付一括設定
│   ├── create-missing-issues.py      # 不足しているIssueを作成
│   ├── add-mid-category.py           # 中カテゴリ一括追加
│   ├── update-mid-category-to-github.py  # 中カテゴリGitHub同期
│   └── add-mid-category-field-to-projects.py  # Projects V2フィールド追加
│
├── examples/                          # プロジェクト例
│   ├── web-app-project/              # Webアプリ開発プロジェクト例
│   │   ├── tasks.json                # 中カテゴリ設定済みタスク定義
│   │   └── mid-categories.md         # 中カテゴリ定義説明
│   └── data-analysis-project/        # データ分析プロジェクト例
│       ├── tasks.json                # 中カテゴリ設定済みタスク定義
│       └── mid-categories.md         # 中カテゴリ定義説明
│
└── .github/
    └── workflows/
        └── github-sync.yml           # GitHub Actions（GitHub同期）
```

---

## 中カテゴリ管理機能

プロジェクトを**3階層**で管理し、より適切な粒度で進捗を把握できます。

### 階層構造

```
プロジェクト
├── Phase 1（大カテゴリ）
│   ├── 計画策定（中カテゴリ）
│   │   ├── TASK-001: キックオフミーティング開催
│   │   └── TASK-002: プロジェクト憲章作成
│   └── 要件定義（中カテゴリ）
│       ├── TASK-003: ユーザーヒアリング実施
│       └── TASK-004: 要件定義書作成
├── Phase 2（大カテゴリ）
│   ├── 設計（中カテゴリ）
│   │   └── TASK-005: システム設計書作成
│   └── 実装（中カテゴリ）
│       └── TASK-006: 機能実装
...
```

### 中カテゴリの設定方法

#### 1. tasks.jsonに追加

各タスクに `midCategory` フィールドを追加：

```json
{
  "id": "TASK-001",
  "title": "プロジェクト計画策定",
  "phase": "Phase 1",
  "midCategory": "計画策定",
  "category": "documentation",
  ...
}
```

#### 2. GitHubに同期

```bash
# 中カテゴリラベル作成 & Issueタイトル変更
python3 scripts/update-mid-category-to-github.py

# Projects V2にフィールド追加
python3 scripts/add-mid-category-field-to-projects.py
```

#### 3. GitHub Projects V2で可視化

- ロードマップビューで「Mid Category」でグループ化
- フィルタで特定の中カテゴリのみ表示
- 中カテゴリ単位でガントチャート確認

### 中カテゴリの例

プロジェクトタイプに応じて適切な中カテゴリを定義してください：

#### Webアプリ開発プロジェクト
- 計画策定、要件定義、設計、環境構築、フロントエンド実装、バックエンド実装、テスト、デプロイ・リリース

#### データ分析プロジェクト
- 調査・分析、データモデル設計、環境構築、学習、PoC、実装、精度検証、ユーザーテスト、本番リリース

#### インフラ構築プロジェクト
- 計画策定、要件定義、設計、環境構築、ネットワーク設定、セキュリティ設定、監視設定、テスト、本番移行

**詳細は [中カテゴリ管理ガイド](docs/MID_CATEGORY_GUIDE.md) を参照してください。**

---

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

### 2. GitHub Issues & Projectsでの管理（オプション）

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

### 3. スケジュールの変更管理

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
4. GitHub Issues & Projectsセットアップ (オプション・推奨)
   ↓
5. プロジェクトキックオフ
```

### プロジェクト実行中（毎週のサイクル）

```
月曜日:
  - 週次レビューミーティング
    ├─ 進捗確認
    ├─ 課題・リスクの洗い出し
    └─ 来週の予定確認

火〜金曜日:
  - タスクを実行
  - タスク着手時: tasks.json のステータスを "in_progress" に更新
  - タスク完了時: tasks.json のステータスを "done" に更新
  - git commit & push

金曜日:
  - 週の振り返り
  - tasks.json のステータス最終確認
  - 来週の準備
```

### Phase終了時

```
Phase 1終了:
  ├─ 成果物レビュー
  ├─ マイルストーン達成確認
  └─ Phase 2移行判定

Phase 2終了:
  ├─ 成果物レビュー
  ├─ ユーザーレビュー
  └─ Phase 3移行判定

Phase 3終了:
  ├─ 最終成果物レビュー
  ├─ 本番リリース
  └─ プロジェクト完了判定
```

## タスクステータスの更新方法

タスクのステータスを適切に更新してください。

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
  "title": "タスク名",
  "status": "done",  ← "in_progress" から "done" に変更
  ...
}
```

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
        │  プロジェクト実行       │
        └────────┬────────────────┘
                 │
                 ▼
        ┌─────────────────────────┐
        │  タスク実行             │
        │  & ステータス更新        │
        └────────┬────────────────┘
                 │
                 ▼
        ┌─────────────────────────┐
        │  Phase 終了レビュー     │
        └────────┬────────────────┘
                 │
                 ▼
        ┌─────────────────────────┐
        │  プロジェクト完了       │
        └─────────────────────────┘
```

## よくある質問（FAQ）

### Q1: スケジュールを変更できますか？

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

## トラブルシューティング

問題が発生した場合は、以下のドキュメントを参照してください：

- GitHub同期の問題: [docs/GITHUB_SYNC_SETUP.md](docs/GITHUB_SYNC_SETUP.md)
- スケジュール管理の問題: [docs/SCHEDULE_UPDATE_GUIDE.md](docs/SCHEDULE_UPDATE_GUIDE.md)
- タスク管理の問題: [SCHEDULE.md](SCHEDULE.md)

## コントリビューション

このテンプレートへの貢献を歓迎します。

変更を行う場合:
1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/improvement`)
3. 変更をコミット (`git commit -am 'Add some improvement'`)
4. ブランチにプッシュ (`git push origin feature/improvement`)
5. プルリクエストを作成

## ライセンス

MIT License

このテンプレートは自由に使用、変更、配布できます。

## サポート・お問い合わせ

質問や問題がある場合は、[GitHub Issues](../../issues)で報告してください。

## バージョン履歴

| バージョン | 日付 | 変更内容 |
|-----------|------|---------|
| 2.0.0 | 2026-01-18 | 中カテゴリ管理機能追加、テンプレート汎用化 |
| 1.1.0 | 2026-01-15 | 完全ワークフローガイド追加、PLAN.md自動更新機能追加 |
| 1.0.0 | 2026-01-15 | 初版作成 |

---

**作成者**: Claude AI (Sonnet 4.5)
