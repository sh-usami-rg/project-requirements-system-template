# クイックスタートガイド - 5分で始めるプロジェクト要件システム

このガイドを読めば、5分でプロジェクト要件システムの利用を開始できます。

## 目次

1. [システムの4ステップワークフロー](#システムの4ステップワークフロー)
2. [ステップ1: 仕様書の作成](#ステップ1-仕様書の作成)
3. [ステップ2: タスク計画の生成](#ステップ2-タスク計画の生成)
4. [ステップ3: スケジュールの作成](#ステップ3-スケジュールの作成)
5. [ステップ4: 進捗管理の開始](#ステップ4-進捗管理の開始)
6. [次のステップ](#次のステップ)

---

## システムの4ステップワークフロー

```
SPEC.md → tasks.json → schedule.json → progress.json
   ↓          ↓             ↓              ↓
仕様書    タスク計画    スケジュール    進捗管理
```

このシステムは、仕様書作成からプロジェクト完了まで、4つの段階で管理します：

1. **仕様書作成** (`/spec-refine`): 対話形式で高品質な仕様書を作成
2. **タスク計画** (`/plan-project`): SPEC.mdから自動的にタスク一覧を生成
3. **スケジュール作成** (`/schedule-tasks`): タスクから日次・週次・月次スケジュールを生成
4. **進捗管理** (`/update-progress`, `/review-cycle`): PDCAサイクルで進捗を追跡

---

## ステップ1: 仕様書の作成

### 1.1 仕様書洗練コマンドを実行

まず、以下のスラッシュコマンドを実行してください：

```bash
/spec-refine
```

このコマンドを実行すると、Claudeが対話形式で仕様書の作成を開始します。

### 1.2 プロジェクトの概要を説明

コマンド実行後、Claudeがプロジェクトについて質問しますので、簡潔に説明してください：

```
「ECサイトを構築したいです。ユーザー登録、商品カタログ、
ショッピングカート、決済機能が必要です。」
```

### 1.3 質問に答える

Claudeが以下のような質問をします（2〜3問ずつ）：

- ターゲットユーザーは誰ですか？
- 月間の想定ユーザー数は？
- 決済方法は何を想定していますか？
- セキュリティ要件はありますか？

### 1.4 仕様書の完成

回答を繰り返すと、`SPEC.md` が作成されます。

**所要時間**: 15〜30分（プロジェクトの複雑さによる）

**成果物**: `/home/sh-usami/project-requirements-system/SPEC.md`

---

## ステップ2: タスク計画の生成

### 2.1 タスク計画コマンドを実行

```bash
/plan-project
```

このコマンドは以下を自動実行します：

- SPEC.mdの分析
- Work Breakdown Structure（WBS）の作成
- 各タスクの工数見積もり
- タスク間の依存関係の識別
- 開始日・完了日の設定

### 2.2 生成されたタスクを確認

```bash
cat tasks.json
```

**tasks.jsonの内容**:
- プロジェクト情報（名前、開始日、終了日）
- タスク一覧（ID、名前、カテゴリ、優先度、工数、依存関係）
- メタデータ（生成日時、バージョン）

### 2.3 必要に応じて調整

タスクの調整が必要な場合は、`tasks.json`を直接編集できます：

```bash
vim tasks.json
```

**所要時間**: 1〜2分（自動生成）

**成果物**: `/home/sh-usami/project-requirements-system/tasks.json`

---

## ステップ3: スケジュールの作成

### 3.1 スケジュール生成コマンドを実行

```bash
/schedule-tasks
```

このコマンドは以下を自動実行します：

- 日次スケジュールの作成（タスクを日付に割り当て）
- 週次スケジュールの作成（週ごとの集計）
- 月次スケジュールの作成（月ごとの集計）
- Ganttチャートの生成（タイムラインの視覚化）

### 3.2 生成されたスケジュールを確認

```bash
cat schedule.json
```

**schedule.jsonの内容**:
- プロジェクト概要（総タスク数、進捗率）
- 日次スケジュール（各日のタスク一覧）
- 週次スケジュール（週ごとの進捗）
- 月次スケジュール（月ごとの進捗）
- Ganttチャート（視覚的なタイムライン）

**所要時間**: 1〜2分（自動生成）

**成果物**: `/home/sh-usami/project-requirements-system/schedule.json`

---

## ステップ4: 進捗管理の開始

### 4.1 進捗データファイルの作成

サンプルファイルをコピー：

```bash
cp progress.json.example progress.json
```

プロジェクト情報を編集：

```bash
vim progress.json
```

### 4.2 tasks.jsonのデータを統合（オプション）

`tasks.json`のタスクを`progress.json`に統合できます。
手動でコピーするか、Claudeに依頼してください：

```
「tasks.jsonのタスクをprogress.jsonに統合してください」
```

### 4.3 日次の進捗更新

毎日の終業時に進捗を更新：

```bash
/update-progress
```

対話形式で以下を入力：
- タスクID
- 現在のステータス（not_started, in_progress, completed, blocked）
- 進捗率（0〜100%）
- 実績工数（オプション）

### 4.4 週次のPDCAレビュー

毎週金曜日にレビューを実施：

```bash
/review-cycle
```

PDCAサイクルに基づいて以下を記録：
- **Plan**: スケジュール差異、スコープ変更
- **Do**: 完了タスク、達成事項、問題
- **Check**: 進捗率、リスク評価
- **Act**: 改善アクション、教訓、次週の目標

### 4.5 ダッシュボードの確認

日次レポート：

```bash
./scripts/progress-dashboard.py daily
```

週次レポート：

```bash
./scripts/progress-dashboard.py weekly -o reports/weekly-$(date +%Y%m%d).md
```

**所要時間**:
- 初回セットアップ: 5〜10分
- 日次更新: 2〜3分
- 週次レビュー: 15〜20分

**成果物**:
- `/home/sh-usami/project-requirements-system/progress.json`
- `/home/sh-usami/project-requirements-system/reports/pdca-*.md`
- `/home/sh-usami/project-requirements-system/reports/weekly-*.md`

---

## 次のステップ

### 日常的な運用

1. **毎朝**: 日次ダッシュボードで今日のフォーカスを確認
   ```bash
   ./scripts/progress-dashboard.py daily
   ```

2. **毎日終業時**: 進捗を更新
   ```bash
   /update-progress
   ```

3. **毎週金曜**: PDCAレビューを実施
   ```bash
   /review-cycle
   ```

4. **毎月初**: 月次レポートで前月の総括
   ```bash
   ./scripts/progress-dashboard.py monthly -o reports/monthly.md
   ```

### さらに学ぶ

- **詳細なドキュメント**: [README.md](README.md)
- **英語版ドキュメント**: [README_EN.md](README_EN.md)
- **GitHub連携**: [docs/GITHUB_SETUP.md](docs/GITHUB_SETUP.md)

### カスタマイズ

- **仕様書テンプレート**: `templates/SPEC.md`を編集
- **タスク生成ルール**: `.claude/commands/plan-project.md`を編集
- **スケジュール設定**: `.claude/commands/schedule-tasks.md`を編集

---

## トラブルシューティング

### Q: スクリプトが実行できません

A: 実行権限を付与してください：

```bash
chmod +x scripts/*.py scripts/*.sh
```

### Q: jqコマンドが見つかりません（Shell版ダッシュボード使用時）

A: jqをインストールしてください：

```bash
# Ubuntu/Debian
sudo apt-get install jq

# macOS
brew install jq
```

### Q: Python版ダッシュボードが動作しません

A: Python 3.7以降がインストールされていることを確認してください：

```bash
python3 --version
```

---

## まとめ

これで、プロジェクト要件システムの基本的な使い方を理解できました。

**4つのステップ**:
1. `/spec-refine` で仕様書を作成
2. `/plan-project` でタスク計画を生成
3. `/schedule-tasks` でスケジュールを作成
4. `/update-progress` と `/review-cycle` で進捗を管理

**日常的な運用**:
- 毎朝: ダッシュボード確認
- 毎日: 進捗更新
- 毎週: PDCAレビュー
- 毎月: 月次総括

このシステムを活用して、プロジェクトを成功に導きましょう！
