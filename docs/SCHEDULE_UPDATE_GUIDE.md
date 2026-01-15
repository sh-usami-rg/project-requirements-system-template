# スケジュール更新ガイド

## 概要

このガイドでは、タスクのスケジュール変更を簡単に行い、全ての関連ファイルとGitHubを自動で更新する方法を説明します。

`update-schedule.py` スクリプトを使用することで、以下の処理が自動で実行されます：

1. **ローカルファイルの更新**
   - `tasks.json` - タスク定義、優先度、依存関係
   - `schedule.json` - スケジュールデータ、日付、週次スケジュール
   - **`PLAN.md`** - 実行計画書（WBS、工数サマリー、マイルストーン）
   - **`SCHEDULE.md`** - 人間が読めるスケジュール（週次計画）
   - `github-issue-mapping.json` - Issue番号マッピング（削除時のみ）

2. **GitHubの更新**
   - GitHub Issues のマイルストーン更新
   - Projects V2 の Start Date / End Date フィールド更新
   - 依存タスクの自動調整

3. **安全性**
   - 全ファイルの自動バックアップ
   - エラー時の自動ロールバック
   - 変更サマリーの表示

---

## 前提条件

- GitHub CLI (`gh`) がインストールされていること
- `gh auth login` で認証済みであること
- `github-issue-mapping.json` が存在すること
- GitHub Projects V2 が作成済みであること

---

## 基本的な使い方

### 1. インタラクティブモード（推奨）

対話形式で操作を選択できます：

```bash
python3 scripts/update-schedule.py --interactive
```

実行すると、以下のメニューが表示されます：

```
実行する操作を選択してください:
  1. タスクの期限を延長
  2. タスクの開始日を変更
  3. タスクを削除
  4. タスクの優先度を変更
  5. 終了

選択 (1-5):
```

---

### 2. コマンドラインモード

直接コマンドで操作を指定できます。

#### タスクの期限を延長

```bash
python3 scripts/update-schedule.py --task TASK-007 --extend-deadline 7
```

**例**: TASK-007の期限を7日延長する

**自動で実行される処理**:
- TASK-007の終了日を7日後に変更
- TASK-007に依存するタスクも自動的に7日延長
- 週次スケジュールを再計算
- SCHEDULE.mdを再生成
- GitHub IssueのMilestoneを更新
- Projects V2のEnd Dateを更新

#### タスクの開始日を変更

```bash
python3 scripts/update-schedule.py --task TASK-015 --start-date 2026-02-10
```

**例**: TASK-015の開始日を2026-02-10に変更する

**自動で実行される処理**:
- TASK-015の開始日を指定日に変更
- 工数に基づいて終了日を自動再計算
- 週次スケジュールを再計算
- SCHEDULE.mdを再生成
- GitHub IssueのMilestoneを更新
- Projects V2のStart Date / End Dateを更新

#### タスクを削除

```bash
python3 scripts/update-schedule.py --task TASK-010 --action delete
```

**例**: TASK-010を削除する

**確認プロンプトが表示されます**:
```
本当にTASK-010を削除しますか？ (yes/no):
```

**自動で実行される処理**:
- tasks.jsonからTASK-010を削除
- schedule.jsonからTASK-010を削除
- 他のタスクの依存関係からTASK-010を削除
- 週次スケジュールを再計算
- SCHEDULE.mdを再生成
- GitHub IssueをクローズしてProjects V2から削除

#### タスクの優先度を変更

```bash
python3 scripts/update-schedule.py --task TASK-005 --priority high
```

**例**: TASK-005の優先度をhighに変更する

**自動で実行される処理**:
- tasks.jsonの優先度を更新
- schedule.jsonの優先度を更新
- ファイルを保存

---

## ユースケース別の使用例

### ユースケース 1: タスクが予定より遅れている

**状況**: TASK-012が3日遅れていて、期限を延長したい

```bash
python3 scripts/update-schedule.py --task TASK-012 --extend-deadline 3
```

**結果**:
- TASK-012の終了日が3日後に変更される
- TASK-012に依存するタスク（例: TASK-015）も自動的に3日延長される
- 週次スケジュールが再計算され、各週の累積進捗率が更新される
- GitHubのロードマップビューにも変更が反映される

---

### ユースケース 2: タスクの開始を前倒ししたい

**状況**: リソースに余裕ができたので、TASK-020を1週間早く開始したい

```bash
python3 scripts/update-schedule.py --task TASK-020 --start-date 2026-03-02
```

**結果**:
- TASK-020の開始日が2026-03-02に変更される
- 工数（3日）に基づいて終了日が自動計算される（2026-03-04）
- 週次スケジュールが再計算され、TASK-020がWeek 9に移動
- GitHubのマイルストーンとロードマップが更新される

---

### ユースケース 3: 不要なタスクを削除

**状況**: TASK-008（BigQuery Spreadsheetテンプレート作成）が不要になった

```bash
python3 scripts/update-schedule.py --task TASK-008 --action delete
```

**確認プロンプト**:
```
本当にTASK-008を削除しますか？ (yes/no): yes
```

**結果**:
- TASK-008がtasks.jsonとschedule.jsonから削除される
- 他のタスクの依存関係からTASK-008が削除される
- GitHub Issue #23がクローズされる
- Projects V2からTASK-008が削除される
- 週次スケジュールと累積進捗率が再計算される

---

### ユースケース 4: 優先度を上げる

**状況**: TASK-010の重要性が増したので、優先度をmediumからhighに変更

```bash
python3 scripts/update-schedule.py --task TASK-010 --priority high
```

**結果**:
- tasks.jsonとschedule.jsonの優先度がhighに更新される
- SCHEDULE.mdで🔴（高優先度）のアイコンで表示される

---

## 安全機能

### 自動バックアップ

スクリプト実行時に、以下のファイルが自動的にバックアップされます：

- `tasks.json`
- `schedule.json`
- `SCHEDULE.md`
- `github-issue-mapping.json`

バックアップは `.backups/YYYYmmdd_HHMMSS/` ディレクトリに保存されます。

**例**:
```
.backups/
  20260115_143052/
    tasks.json
    schedule.json
    SCHEDULE.md
    github-issue-mapping.json
```

### 自動ロールバック

エラーが発生した場合、自動的にバックアップから復元されます：

```
ERROR: 無効な日付形式: 2026-13-40（YYYY-MM-DD形式で指定してください）

⚠️  エラーが発生したため、バックアップから復元します: .backups/20260115_143052
✅ バックアップから復元完了
```

### 変更サマリー

全ての変更が完了すると、サマリーが表示されます：

```
====================================================================
📋 変更サマリー
====================================================================
  ✓ TASK-012: 終了日 2026-02-15 → 2026-02-18
  ✓ TASK-015: 依存関係により自動延長 2026-02-16 → 2026-02-19
  ✓ TASK-018: 依存関係により自動延長 2026-02-20 → 2026-02-23

====================================================================
✅ スケジュール更新完了
====================================================================
```

---

## オプション

### GitHub同期をスキップ

ローカルファイルのみを更新したい場合：

```bash
python3 scripts/update-schedule.py --task TASK-007 --extend-deadline 7 --no-github-sync
```

このオプションを使用すると：
- ローカルファイル（tasks.json, schedule.json, PLAN.md, SCHEDULE.md）のみ更新される
- GitHub IssueやProjects V2は更新されない

**注意**: 後でGitHubと同期する場合は、`scripts/set-issue-dates.py` を実行してください。

---

## トラブルシューティング

### エラー: "gh: command not found"

**原因**: GitHub CLIがインストールされていない

**解決方法**:
```bash
# macOS
brew install gh

# Linux (Ubuntu/Debian)
sudo apt install gh

# Linux (Fedora/RHEL)
sudo yum install gh
```

### エラー: "GitHub CLI認証エラー"

**原因**: GitHub CLIが認証されていない

**解決方法**:
```bash
gh auth login
```

### エラー: "TASK-XXX が schedule.json に見つかりません"

**原因**: 指定したタスクIDが存在しない

**解決方法**:
- `schedule.json` を確認して、正しいタスクIDを指定してください
- タスク一覧を確認: `cat schedule.json | jq '.tasks[] | .id'`

### エラー: "Milestone 'Week X' not found"

**原因**: GitHubにマイルストーンが作成されていない

**解決方法**:
```bash
# マイルストーンを再作成
python3 scripts/sync-github.py
```

### エラー: "Projects V2のフィールドが見つかりません"

**原因**: Projects V2に「Start Date」「End Date」フィールドが作成されていない

**解決方法**:
1. https://github.com/users/sh-usami-rg/projects/3 を開く
2. 右上の「...」→「Settings」をクリック
3. 「+ New field」をクリック
4. Field type: 「Date」を選択
5. Field name: 「Start Date」を入力して作成
6. 同様に「End Date」も作成

---

## 依存タスクの自動調整について

タスクの期限を延長すると、そのタスクに依存する他のタスクも自動的に延長されます。

**例**:

```
TASK-001 (1/6 - 1/6)
  ↓ 依存
TASK-002 (1/7 - 1/10)
  ↓ 依存
TASK-003 (1/13 - 1/17)
```

この状態で `TASK-001` の期限を3日延長すると：

```bash
python3 scripts/update-schedule.py --task TASK-001 --extend-deadline 3
```

**結果**:
```
TASK-001 (1/6 - 1/9)   ← 3日延長
  ↓ 依存
TASK-002 (1/10 - 1/13) ← 自動的に3日延長
  ↓ 依存
TASK-003 (1/16 - 1/20) ← 自動的に3日延長
```

変更サマリー:
```
📋 変更サマリー
====================================================================
  ✓ TASK-001: 終了日 2026-01-06 → 2026-01-09
  ✓ TASK-002: 依存関係により自動延長 2026-01-07 → 2026-01-10
  ✓ TASK-003: 依存関係により自動延長 2026-01-13 → 2026-01-16
```

---

## 週次スケジュールの再計算

タスクの日付を変更すると、週次スケジュールが自動的に再計算されます。

**例**:

変更前（Week 2）:
```
Week 2 (2026-01-13 〜 2026-01-17)
- 累積進捗率: 24%
- タスク数: 3個
- タスク: TASK-003, TASK-005, TASK-009
```

TASK-005を1週間延長した後:
```
Week 2 (2026-01-13 〜 2026-01-17)
- 累積進捗率: 19%
- タスク数: 2個
- タスク: TASK-003, TASK-009

Week 3 (2026-01-20 〜 2026-01-24)
- 累積進捗率: 29%
- タスク数: 4個
- タスク: TASK-006, TASK-008, TASK-005 ← 移動
```

---

## Claude Codeでの自然言語による操作

このスクリプトは、Claude Codeに自然言語でリクエストすることで実行できます。

### 例1: 期限延長

**ユーザー**: 「TASK-007の期限を1週間延ばしたい」

**Claude Code**:
```bash
python3 scripts/update-schedule.py --task TASK-007 --extend-deadline 7
```

### 例2: 開始日変更

**ユーザー**: 「TASK-015を2月10日から開始するように変更したい」

**Claude Code**:
```bash
python3 scripts/update-schedule.py --task TASK-015 --start-date 2026-02-10
```

### 例3: タスク削除

**ユーザー**: 「TASK-010は不要になったので削除したい」

**Claude Code**:
```bash
python3 scripts/update-schedule.py --task TASK-010 --action delete
```

### 例4: 優先度変更

**ユーザー**: 「TASK-005の優先度を高くしたい」

**Claude Code**:
```bash
python3 scripts/update-schedule.py --task TASK-005 --priority high
```

---

## 推奨ワークフロー

### 日常的なスケジュール変更

1. **変更が必要になったら**:
   - Claude Codeに自然言語でリクエスト
   - または `update-schedule.py --interactive` を実行

2. **変更内容を確認**:
   - 変更サマリーを確認
   - `SCHEDULE.md` を開いて週次スケジュールを確認

3. **GitHubで視覚的に確認**:
   - Projects V2のRoadmapビューを開く
   - ガントチャートで変更を確認
   - https://github.com/users/sh-usami-rg/projects/3

### 週次レビュー時

1. **現在の進捗を確認**:
   - GitHubのMilestonesページを開く
   - 今週のタスクの完了状況を確認

2. **遅延タスクを調整**:
   - 遅れているタスクの期限を延長
   - 依存タスクが自動調整されることを確認

3. **次週の計画を確認**:
   - `SCHEDULE.md` で来週のタスクを確認
   - 必要に応じて優先度を調整

---

## ファイル更新の完全性

`update-schedule.py` は、以下の全てのファイルを漏れなく更新します：

| ファイル | 更新内容 |
|---------|---------|
| `tasks.json` | タスク定義、優先度、依存関係 |
| `schedule.json` | 開始日、終了日、週番号、週次スケジュール |
| **`PLAN.md`** | **実行計画書（WBS、タスク一覧、工数サマリー、マイルストーン）** |
| **`SCHEDULE.md`** | **人間が読める形式のスケジュール（週次計画）** |
| `github-issue-mapping.json` | タスク削除時にマッピングから削除 |
| GitHub Issues | マイルストーンの更新 |
| Projects V2 | Start Date / End Date フィールドの更新 |

**PLAN.mdの自動更新内容**:
- WBS（作業分解構造）：Phase別、カテゴリ別のタスク詳細
- タスク一覧テーブル：GitHub Projects用の完全なタスクリスト
- 依存関係マップ：Phase別のタスク依存関係
- 工数サマリー：Phase別・メンバー別の総工数、総Weight、余裕率
- マイルストーン：Week 4, Week 8, Week 12の日付
- プロジェクト概要：開始日、終了日、総工数、総Weight

**保証**:
- どのファイルも更新漏れが発生しません
- エラー時は全てのファイルがロールバックされます
- 変更サマリーで全ての変更を確認できます

---

## まとめ

このスケジュール更新システムを使用することで：

✅ **簡単**: 自然言語またはシンプルなコマンドで操作
✅ **安全**: 自動バックアップとロールバック機能
✅ **完全**: 全てのファイルとGitHubを自動更新
✅ **視覚的**: GitHubのロードマップビューで変更を確認
✅ **自動**: 依存タスクの連鎖的な調整
✅ **一貫性**: ファイル間の不整合が発生しない

**困った時は**:
- このドキュメントの「トラブルシューティング」セクションを確認
- Claude Codeに質問する
- GitHub Issues: https://github.com/sh-usami-rg/dashboard-migration-project/issues
