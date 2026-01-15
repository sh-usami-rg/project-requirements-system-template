# PDCAレビューサイクルコマンド

PDCAサイクルに基づいてプロジェクトの進捗をレビューし、改善アクションを提案します。

## 実行する処理

### 1. 前準備
- progress.jsonを読み込み
- 前回のPDCAサイクルレビュー日時を確認
- 今回のサイクルIDを生成（例: CYCLE-20260115-001）

### 2. Plan (計画) - 計画と実績の差分分析

#### 2.1 スケジュール差異の分析
```python
for task in tasks:
    if task.actual_end_date and task.planned_end_date:
        variance_days = (actual_end_date - planned_end_date).days
        if variance_days > 0:
            # 遅延を記録
        elif variance_days < 0:
            # 前倒しを記録
```

#### 2.2 工数差異の分析
```python
total_planned_hours = sum(task.estimated_hours)
total_actual_hours = sum(task.actual_hours)
effort_variance = ((actual - planned) / planned) * 100
```

#### 2.3 スコープ変更の検出
- 新規追加されたタスク
- キャンセルされたタスク
- 優先度が変更されたタスク

#### 2.4 計画レビュー結果の生成
```json
{
  "plan": {
    "plannedTasks": <計画タスク数>,
    "plannedHours": <計画工数>,
    "deviations": [
      {
        "taskId": "TASK-001",
        "description": "3日遅延 - 要件定義に想定外の時間が必要だった",
        "impact": "high"
      }
    ]
  }
}
```

### 3. Do (実行) - 完了タスクのレビュー

#### 3.1 期間内の成果を集計
- 前回レビュー以降に完了したタスク
- 前回レビュー以降の実績工数
- 新たに開始されたタスク

#### 3.2 達成事項の抽出
ユーザーに以下を確認：
```
【達成事項を入力してください】
期間中に達成した主要な成果を箇条書きで入力してください：
1. [成果1]
2. [成果2]
...
```

#### 3.3 問題・課題の記録
以下の情報を収集：
```
【発生した問題を記録してください】
各問題について以下の情報を入力：
- 問題の説明: [テキスト]
- 深刻度: [low/medium/high/critical]
- 関連タスクID: [TASK-XXX]
- 対処状況: [テキスト]
```

#### 3.4 実行レビュー結果の生成
```json
{
  "do": {
    "completedTasks": <完了タスク数>,
    "actualHours": <実績工数>,
    "achievements": [
      "APIの基本設計とプロトタイプ実装が完了",
      "ユニットテストカバレッジ80%を達成"
    ],
    "issues": [
      {
        "description": "外部APIのレート制限により開発が一時停止",
        "severity": "medium",
        "taskId": "TASK-005"
      }
    ]
  }
}
```

### 4. Check (評価) - 進捗状況の評価

#### 4.1 進捗メトリクスの評価
```python
# 進捗率
progress_rate = metrics.overall_progress

# スケジュール差異（日数）
project_duration = (end_date - start_date).days
elapsed_days = (today - start_date).days
expected_progress = (elapsed_days / project_duration) * 100
schedule_variance = progress_rate - expected_progress

# 工数差異率
effort_variance = ((actual_hours - planned_hours) / planned_hours) * 100
```

#### 4.2 遅延タスクの特定
- 遅延中のタスク（計画終了日を過ぎたタスク）
- 遅延リスクのあるタスク（残り時間と進捗のバランス）

#### 4.3 品質メトリクスの評価
ユーザーに確認：
```
【品質メトリクスを入力してください】
- 発見された不具合数: [数値]
- 手戻り工数（時間）: [数値]
- コードレビュー指摘事項数: [数値] (オプション)
- テストカバレッジ: [%] (オプション)
```

#### 4.4 リスク評価
以下の基準でリスクレベルを判定：
- **Critical**: 進捗率 < 50% かつ経過率 > 60%、または重大な問題が3件以上
- **High**: 進捗率 < 経過率-20%、または遅延タスクが5件以上
- **Medium**: 進捗率 < 経過率-10%、または遅延タスクが3件以上
- **Low**: 上記以外

#### 4.5 評価結果の生成
```json
{
  "check": {
    "progressRate": <進捗率>,
    "scheduleVariance": <スケジュール差異>,
    "effortVariance": <工数差異率>,
    "delayedTasks": ["TASK-003", "TASK-007"],
    "qualityMetrics": {
      "defectCount": 5,
      "reworkHours": 12.5
    },
    "riskAssessment": "medium"
  }
}
```

### 5. Act (改善) - 改善アクションの提案

#### 5.1 問題分析に基づく改善提案
自動的に生成される改善提案：

```python
improvements = []

# 工数超過の場合
if effort_variance > 20:
    improvements.append({
        "description": "見積精度向上: 過去の実績データを基に見積手法を見直す",
        "priority": "high"
    })

# 遅延タスクが多い場合
if len(delayed_tasks) > 3:
    improvements.append({
        "description": "リソース配分の最適化: 遅延タスクへの人員増強を検討",
        "priority": "high"
    })

# 品質問題がある場合
if defect_count > 10:
    improvements.append({
        "description": "品質管理強化: レビュープロセスの見直しとテスト工程の充実",
        "priority": "medium"
    })

# スケジュール遅延の場合
if schedule_variance < -15:
    improvements.append({
        "description": "スケジュール調整: マイルストーンの見直しと優先順位の再設定",
        "priority": "high"
    })
```

#### 5.2 ユーザーによる追加改善アクション
```
【追加の改善アクションを入力してください】
改善アクション:
- 説明: [改善内容]
- 優先度: [low/medium/high]
- 担当者: [名前]
- 期限: [YYYY-MM-DD]
```

#### 5.3 教訓・学びの記録
```
【教訓・学びを記録してください】
今回のサイクルから得られた教訓を箇条書きで入力：
1. [教訓1]
2. [教訓2]
...
```

#### 5.4 次サイクルの目標設定
```
【次サイクルの目標を設定してください】
次のレビューまでに達成したい目標：
1. [目標1]
2. [目標2]
...
```

#### 5.5 改善アクション結果の生成
```json
{
  "act": {
    "improvements": [
      {
        "id": "IMP-001",
        "description": "見積精度向上のため、タスク完了時に見積と実績の乖離要因を記録",
        "priority": "high",
        "assignee": "プロジェクトマネージャー",
        "dueDate": "2026-01-22",
        "status": "pending"
      }
    ],
    "lessonsLearned": [
      "外部依存があるタスクは余裕を持ったバッファを設定すべき",
      "週次での進捗確認が遅延の早期発見に有効"
    ],
    "nextCycleGoals": [
      "全タスクの進捗率を85%以上に到達",
      "遅延タスクを2件以下に削減",
      "コードレビュー体制を確立"
    ]
  }
}
```

### 6. PDCAサイクルデータの保存

#### 6.1 サイクルデータの構築
Plan、Do、Check、Actの各セクションを統合

#### 6.2 progress.jsonへの追加
```python
pdca_cycle = {
    "cycleId": cycle_id,
    "date": current_datetime,
    "plan": plan_result,
    "do": do_result,
    "check": check_result,
    "act": act_result
}

progress_data["pdcaCycles"].append(pdca_cycle)
save_json(progress_data, "progress.json")
```

### 7. レビューレポートの生成

以下の形式でMarkdownレポートを生成し、表示：

```markdown
# PDCAサイクルレビューレポート
**サイクルID**: {cycle_id}
**レビュー日時**: {date}

## Plan (計画) - 計画と実績の差分

### スケジュール差異
- 計画タスク数: {planned_tasks}
- 計画工数: {planned_hours}時間

### 主な差異
{deviations}

---

## Do (実行) - 期間中の実績

### 完了実績
- 完了タスク数: {completed_tasks}
- 実績工数: {actual_hours}時間

### 達成事項
{achievements}

### 発生した問題
{issues}

---

## Check (評価) - 進捗状況の評価

### 進捗メトリクス
- 全体進捗率: {progress_rate}%
- スケジュール差異: {schedule_variance}日
- 工数差異: {effort_variance}%

### 遅延タスク
{delayed_tasks}

### 品質メトリクス
- 不具合数: {defect_count}
- 手戻り工数: {rework_hours}時間

### リスク評価
**レベル**: {risk_assessment}

---

## Act (改善) - 改善アクションと次サイクル目標

### 改善アクション
{improvements}

### 教訓・学び
{lessons_learned}

### 次サイクルの目標
{next_cycle_goals}

---

## サマリー

{総合的な評価コメント}

**次回レビュー推奨日**: {next_review_date}
```

### 8. レポートファイルの保存

レポートを以下のパスに保存：
```
reports/pdca-{cycle_id}.md
```

## エラーハンドリング

- progress.jsonが存在しない場合、エラーメッセージと初期化手順を表示
- ユーザー入力が不正な形式の場合、再入力を促す
- 前回レビューから期間が短い場合（1日未満）、警告を表示

## 使用例

```bash
# コマンド実行
/review-cycle

# 対話形式で情報を入力
【達成事項を入力してください】
1. ユーザー認証機能の実装完了
2. データベース設計のレビュー完了

【発生した問題を記録してください】
問題の説明: テスト環境のセットアップに想定以上の時間がかかった
深刻度: medium
関連タスクID: TASK-008

【品質メトリクスを入力してください】
発見された不具合数: 3
手戻り工数: 4.5

【教訓・学びを記録してください】
1. 環境セットアップは別タスクとして明示的に計画すべき
2. 依存関係のあるタスクは並行作業が難しい

【次サイクルの目標を設定してください】
1. テストカバレッジ90%達成
2. 全機能の統合テスト完了
```

## 関連ファイル

- `progress.json`: 進捗データとPDCAサイクル履歴
- `templates/progress-template.json`: データスキーマ定義
- `reports/pdca-*.md`: 生成されたレビューレポート
- `.claude/commands/update-progress.md`: 進捗更新コマンド
