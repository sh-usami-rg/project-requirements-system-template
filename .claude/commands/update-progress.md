# 進捗更新コマンド

タスクの進捗を更新し、プロジェクトの状態を最新化します。

## 実行する処理

### 1. 現在の進捗状況を確認
- progress.jsonを読み込み
- タスク一覧を表示
- 現在の全体進捗率を表示

### 2. ユーザーに更新内容を確認

以下の情報をユーザーに確認してください：

```
更新するタスクの情報を入力してください：
- タスクID: [既存のタスクIDまたは新規]
- タスク名: [タスク名]
- ステータス: [not_started/in_progress/completed/blocked/cancelled]
- 進捗率: [0-100]
- 実績開始日: [YYYY-MM-DD] (オプション)
- 実績終了日: [YYYY-MM-DD] (オプション)
- 実績工数: [時間] (オプション)
- 備考: [テキスト] (オプション)
```

### 3. タスク情報を更新

- 指定されたタスクの情報を更新
- ステータスが"completed"の場合、進捗率を自動的に100%に設定
- ステータスが"in_progress"で実績開始日が未設定の場合、今日の日付を設定
- ステータスが"completed"で実績終了日が未設定の場合、今日の日付を設定

### 4. 進捗率を再計算

以下の計算を実行：

```python
# タスクベースの進捗率
task_based_progress = (完了タスク数 / 総タスク数) * 100

# 工数ベースの進捗率（見積工数がある場合）
effort_based_progress = (実績工数の合計 / 見積工数の合計) * 100

# 加重平均進捗率（進捗率フィールドの平均）
weighted_progress = Σ(各タスクの進捗率 * 見積工数) / Σ(見積工数)

# 全体進捗率（上記3つの平均）
overall_progress = (task_based + effort_based + weighted_progress) / 3
```

### 5. 遅延タスクを検出

以下の条件でタスクを検出：

- **遅延タスク**: 計画終了日 < 今日 かつ status != "completed"
- **遅延リスク**: 計画終了日まで残り3日以内 かつ progress < 80%
- **開始遅延**: 計画開始日 < 今日 かつ status == "not_started"

### 6. メトリクスを更新

以下の情報を更新：

```json
{
  "metrics": {
    "overallProgress": <計算した進捗率>,
    "completedTasks": <完了タスク数>,
    "totalTasks": <総タスク数>,
    "onTimeRate": <予定通り完了したタスクの割合>,
    "effortEfficiency": <実績工数/見積工数 * 100>,
    "predictedEndDate": <完了予測日>,
    "lastUpdated": <現在日時>
  }
}
```

完了予測日の計算方法：
```python
remaining_effort = 総見積工数 - 実績工数
current_velocity = 実績工数 / 経過日数
predicted_days = remaining_effort / current_velocity
predicted_end_date = 今日 + predicted_days
```

### 7. progress.jsonに保存

- バックアップを作成（progress.json.backup）
- 更新内容をprogress.jsonに保存
- JSONフォーマットを整形（インデント2スペース）

### 8. 結果レポートを表示

以下の形式で結果を表示：

```markdown
## 進捗更新完了

### 更新されたタスク
- タスクID: {id}
- タスク名: {name}
- ステータス: {status}
- 進捗率: {progress}%

### 全体進捗
- 全体進捗率: {overall_progress}%
- 完了タスク: {completed}/{total} ({completion_rate}%)
- 工数効率: {effort_efficiency}%
- 完了予測日: {predicted_end_date}

### 警告事項
{遅延タスクがある場合}
- ⚠️ 遅延タスク ({count}件):
  - {task_id}: {task_name} (計画終了日: {planned_end_date})

{遅延リスクがある場合}
- ⚡ 遅延リスク ({count}件):
  - {task_id}: {task_name} (残り{days}日, 進捗{progress}%)
```

## エラーハンドリング

- progress.jsonが存在しない場合、テンプレートから新規作成を提案
- 不正なタスクIDが指定された場合、エラーメッセージを表示
- 不正な日付形式の場合、再入力を促す
- JSONパースエラーの場合、バックアップからの復元を提案

## 使用例

```bash
# コマンド実行
/update-progress

# 対話形式でタスク情報を入力
タスクID: TASK-001
ステータス: in_progress
進捗率: 65
備考: APIの基本実装が完了、テスト作成中
```

## 関連ファイル

- `progress.json`: 進捗データ（このコマンドで更新）
- `templates/progress-template.json`: データスキーマ定義
- `scripts/progress-dashboard.py`: ダッシュボード生成スクリプト
