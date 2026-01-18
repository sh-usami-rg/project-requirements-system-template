# tasks.json スキーマ定義

このドキュメントは、`tasks.json` ファイルの構造とフィールドの説明を提供します。

## 概要

`tasks.json` は、プロジェクトのタスク管理に使用されるJSONファイルで、以下の情報を含みます：

- プロジェクト情報（名前、期間、工数など）
- タスク一覧（WBS、依存関係、ステータスなど）
- マイルストーン
- リスク管理

---

## ファイル構造

```json
{
  "project": { ... },
  "tasks": [ ... ],
  "milestones": [ ... ],
  "risks": [ ... ],
  "metadata": { ... }
}
```

---

## プロジェクト（project）

プロジェクト全体の情報を定義します。

### フィールド

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `name` | string | ✅ | プロジェクト名 |
| `description` | string | ✅ | プロジェクトの説明 |
| `startDate` | string | ✅ | 開始日（YYYY-MM-DD形式） |
| `estimatedEndDate` | string | ✅ | 終了予定日（YYYY-MM-DD形式） |
| `totalEffort` | number | ⬜ | 総工数（人日） |
| `totalEffortHours` | number | ⬜ | 総工数（時間） |
| `totalWeight` | number | ⬜ | 総ウェイト（進捗率計算用） |
| `workingDays` | number | ⬜ | 稼働日数 |
| `workingHoursPerDay` | number | ⬜ | 1日あたりの稼働時間 |
| `teamSize` | string | ⬜ | チームサイズ（例: "1名兼任（50%稼働）"） |

### 例

```json
{
  "project": {
    "name": "プロジェクト名",
    "description": "プロジェクトの説明",
    "startDate": "2026-01-06",
    "estimatedEndDate": "2026-03-30",
    "totalEffort": 28.5,
    "totalEffortHours": 199.5,
    "totalWeight": 100,
    "workingDays": 56,
    "workingHoursPerDay": 7,
    "teamSize": "1名兼任（50%稼働）"
  }
}
```

---

## タスク（tasks）

プロジェクトのタスク一覧を定義します。

### フィールド

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `id` | string | ✅ | タスクID（例: "TASK-001"） |
| `title` | string | ✅ | タスク名 |
| `description` | string | ✅ | タスクの詳細説明 |
| `phase` | string | ✅ | フェーズ（大カテゴリ）（例: "Phase 1", "Phase 2"） |
| `midCategory` | string | ⬜ | 中カテゴリ（例: "計画策定", "要件定義", "設計", "実装"） |
| `category` | string | ✅ | カテゴリ（例: "design", "development", "testing"） |
| `priority` | string | ✅ | 優先度（"critical", "high", "medium", "low"） |
| `effort` | number | ✅ | 工数（人日） |
| `effortHours` | number | ✅ | 工数（時間） |
| `weight` | number | ✅ | ウェイト（進捗率計算用、合計100） |
| `dependencies` | array | ✅ | 依存タスクIDの配列（例: ["TASK-001", "TASK-002"]） |
| `assignee` | string | ⬜ | 担当者 |
| `labels` | array | ⬜ | ラベルの配列（例: ["phase-1", "design"]） |
| `milestone` | string | ⬜ | マイルストーン（例: "Week 4 (1/31)"） |
| `status` | string | ✅ | ステータス（"pending", "in_progress", "done"） |

### 中カテゴリ（midCategory）について

**中カテゴリ**は、Phase（大カテゴリ）とTask（小カテゴリ）の中間層として、プロジェクトを適切な粒度で管理するためのフィールドです。

#### 用途

- **プロジェクト全体の把握**: Phaseよりも細かい粒度で進捗を可視化
- **GitHub Projects V2でのグループ化**: ロードマップビューで中カテゴリごとにグループ化・フィルタリング
- **ガントチャート**: 中カテゴリ単位で進捗を確認
- **チーム間の調整**: 中カテゴリごとに担当チームを分けて並行作業を促進

#### 設定例

**Webアプリ開発プロジェクト**:
- 計画策定
- 要件定義
- 設計
- 環境構築
- フロントエンド実装
- バックエンド実装
- テスト
- デプロイ・リリース

**データ分析プロジェクト**:
- 調査・分析
- データモデル設計
- 環境構築
- 学習
- PoC
- BigQuery実装
- LookerML実装
- 精度検証
- ユーザーテスト
- 本番リリース

#### GitHub連携

中カテゴリを設定すると、以下のようにGitHubに反映されます：

1. **ラベル**: `mid:計画策定`, `mid:要件定義` などのラベルが作成されます
2. **Issueタイトル**: `TASK-001: タスク名` → `計画策定：タスク名` に変更されます
3. **Projects V2フィールド**: 「Mid Category」Single Selectフィールドが追加され、各Issueに値が設定されます

詳細は [中カテゴリ管理ガイド](MID_CATEGORY_GUIDE.md) を参照してください。

### タスクの例

```json
{
  "id": "TASK-001",
  "title": "プロジェクト計画策定",
  "description": "プロジェクトの全体計画を策定する",
  "phase": "Phase 1",
  "midCategory": "計画策定",
  "category": "documentation",
  "priority": "high",
  "effort": 0.5,
  "effortHours": 3.5,
  "weight": 2,
  "dependencies": [],
  "assignee": "PM",
  "labels": ["phase-1", "documentation"],
  "milestone": "Week 1 (1/10)",
  "status": "pending"
}
```

---

## マイルストーン（milestones）

プロジェクトの主要なマイルストーンを定義します。

### フィールド

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `name` | string | ✅ | マイルストーン名（例: "Week 4 (1/31)"） |
| `date` | string | ✅ | 日付（YYYY-MM-DD形式） |
| `description` | string | ✅ | 説明 |
| `deliverables` | array | ⬜ | 成果物の配列 |

### 例

```json
{
  "name": "Week 4 (1/31)",
  "date": "2026-01-31",
  "description": "Phase 1完了: 基盤整備・設計完了",
  "deliverables": [
    "プロジェクト計画書",
    "要件定義書",
    "システム設計書"
  ]
}
```

---

## リスク（risks）

プロジェクトのリスク管理情報を定義します。

### フィールド

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `id` | string | ✅ | リスクID（例: "RISK-001"） |
| `description` | string | ✅ | リスクの説明 |
| `impact` | string | ✅ | 影響度（"high", "medium", "low"） |
| `probability` | string | ✅ | 発生確率（"high", "medium", "low"） |
| `mitigation` | string | ✅ | 対策 |
| `owner` | string | ⬜ | 責任者 |

### 例

```json
{
  "id": "RISK-001",
  "description": "技術習熟度不足による開発遅延",
  "impact": "high",
  "probability": "medium",
  "mitigation": "トレーニング期間を設定し、外部リソースを活用",
  "owner": "PM"
}
```

---

## メタデータ（metadata）

ファイルのメタ情報を定義します。

### フィールド

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `createdAt` | string | ✅ | 作成日（YYYY-MM-DD形式） |
| `updatedAt` | string | ✅ | 更新日（YYYY-MM-DD形式） |
| `version` | string | ✅ | バージョン |
| `specVersion` | string | ⬜ | SPEC.mdバージョン |
| `createdBy` | string | ⬜ | 作成者 |

### 例

```json
{
  "createdAt": "2026-01-15",
  "updatedAt": "2026-01-15",
  "version": "1.0",
  "specVersion": "2.0",
  "createdBy": "Claude AI (Sonnet 4.5)"
}
```

---

## 完全な例

```json
{
  "project": {
    "name": "Webアプリケーション開発",
    "description": "新規Webアプリケーションの開発プロジェクト",
    "startDate": "2026-01-06",
    "estimatedEndDate": "2026-03-30",
    "totalEffort": 28.5,
    "totalEffortHours": 199.5,
    "totalWeight": 100,
    "workingDays": 56,
    "workingHoursPerDay": 7,
    "teamSize": "3名"
  },
  "tasks": [
    {
      "id": "TASK-001",
      "title": "プロジェクト計画策定",
      "description": "プロジェクトの全体計画を策定する",
      "phase": "Phase 1",
      "midCategory": "計画策定",
      "category": "documentation",
      "priority": "high",
      "effort": 0.5,
      "effortHours": 3.5,
      "weight": 2,
      "dependencies": [],
      "assignee": "PM",
      "labels": ["phase-1", "documentation"],
      "milestone": "Week 1 (1/10)",
      "status": "pending"
    }
  ],
  "milestones": [
    {
      "name": "Week 4 (1/31)",
      "date": "2026-01-31",
      "description": "Phase 1完了",
      "deliverables": ["計画書", "設計書"]
    }
  ],
  "risks": [
    {
      "id": "RISK-001",
      "description": "リスクの説明",
      "impact": "high",
      "probability": "medium",
      "mitigation": "対策",
      "owner": "PM"
    }
  ],
  "metadata": {
    "createdAt": "2026-01-15",
    "updatedAt": "2026-01-15",
    "version": "1.0",
    "createdBy": "Claude AI"
  }
}
```

---

## 関連ドキュメント

- [中カテゴリ管理ガイド](MID_CATEGORY_GUIDE.md) - 中カテゴリ機能の詳細説明
- [README.md](../README.md) - プロジェクト概要
- [PLAN.md](../PLAN.md) - 実行計画書
- [SCHEDULE.md](../SCHEDULE.md) - スケジュール管理
