# 進捗可視化機能ガイド

プロジェクトの進捗をEVM（Earned Value Management）方式で計算し、視覚的に表示する機能のガイドです。

---

## 📊 概要

このシステムでは、以下の3つのツールで進捗を可視化します：

1. **`calculate-progress.py`**: EVM方式で進捗を計算し、README.mdに自動埋め込み
2. **`generate-mindmap.py`**: タスクをマインドマップ形式で可視化
3. **進捗バッジ**: README.mdに進捗率、SPI、CPIバッジを表示

---

## 🎯 EVM（Earned Value Management）とは？

EVMは、プロジェクト管理で広く使われる進捗管理手法です。以下の指標を使用します：

### 主要指標

| 指標 | 名称 | 説明 |
|------|------|------|
| **PV** | Planned Value (予定出来高) | 予定通りの進捗であれば、この時点で達成しているはずの出来高 |
| **EV** | Earned Value (実績出来高) | 実際に完了したタスクの出来高（進捗率の基準） |
| **AC** | Actual Cost (実コスト) | 実際にかかった工数やコスト |
| **SPI** | Schedule Performance Index | スケジュール効率指数 = EV / PV<br>1.0以上で予定より進んでいる |
| **CPI** | Cost Performance Index | コスト効率指数 = EV / AC<br>1.0以上で予算内で進んでいる |

### 判定基準

- **SPI >= 1.0**: スケジュール通りまたは前倒し ✅
- **SPI < 1.0**: スケジュール遅延 ⚠️
- **CPI >= 1.0**: 予算内で進行中 ✅
- **CPI < 1.0**: コストオーバーラン ⚠️

---

## 🚀 使い方

### 1. 進捗計算とREADME.md更新

```bash
# 進捗を計算してREADME.mdに埋め込む
python3 scripts/calculate-progress.py
```

**実行結果:**
- README.mdに `<!-- PROGRESS_START -->` 〜 `<!-- PROGRESS_END -->` セクションが追加/更新される
- 進捗率、SPI、CPIのバッジが表示される
- Phase別、中カテゴリ別の進捗テーブルが表示される

### 2. マインドマップ生成

```bash
# タスクをマインドマップ形式で可視化
python3 scripts/generate-mindmap.py
```

**出力:**
- `docs/MINDMAP.md` に階層構造のマインドマップが生成される
- Phase > Mid Category > Task の3階層で表示
- ステータス、優先度の絵文字付き
- Phase別・中カテゴリ別のサマリーテーブル

### 3. 定期的な更新

進捗を定期的に更新して、常に最新の状態を保ちます：

```bash
# 毎日、またはタスク完了時に実行
python3 scripts/calculate-progress.py
python3 scripts/generate-mindmap.py

# 変更をコミット
git add README.md docs/MINDMAP.md
git commit -m "Update progress: $(date +%Y-%m-%d)"
git push
```

---

## 📋 README.mdへの埋め込み例

`calculate-progress.py` を実行すると、README.mdに以下のようなセクションが追加されます：

```markdown
<!-- PROGRESS_START -->

## 📊 プロジェクト進捗状況

**更新日時**: 2026-01-18

### 全体進捗

![Progress](https://img.shields.io/badge/progress-45.5%25-yellow) ![SPI](https://img.shields.io/badge/SPI-1.02-brightgreen) ![CPI](https://img.shields.io/badge/CPI-0.98-green)

| 指標 | 値 | 説明 |
|------|-----|------|
| **進捗率** | 45.5% | 完了したタスクのウェイト割合 |
| **PV (予定出来高)** | 44.5 | スケジュール通りの進捗 |
| **EV (実績出来高)** | 45.5 | 実際の進捗 |
| **SPI (スケジュール効率)** | 1.02 | 1.0以上で予定より進んでいる |
| **CPI (コスト効率)** | 0.98 | 1.0以上で予算内で進んでいる |

### Phase別進捗

| Phase | 進捗率 | SPI | CPI | ステータス |
|-------|--------|-----|-----|-----------|
| Phase 1 | 100.0% | 1.05 | 1.00 | ✅ |
| Phase 2 | 60.0% | 1.10 | 0.95 | 🔄 |
| Phase 3 | 10.0% | 0.90 | 1.05 | 📝 |

<!-- PROGRESS_END -->
```

---

## 🎨 進捗バッジの色分け

### 進捗率バッジ

| 進捗率 | 色 | 意味 |
|--------|-----|------|
| 80%以上 | 🟢 Bright Green | 順調 |
| 60-80% | 🟢 Green | 良好 |
| 40-60% | 🟡 Yellow | やや遅れ |
| 20-40% | 🟠 Orange | 遅れ |
| 20%未満 | 🔴 Red | 大幅遅れ |

### SPI/CPIバッジ

| 値 | 色 | 意味 |
|----|-----|------|
| 1.0以上 | 🟢 Bright Green | 優秀 |
| 0.9-1.0 | 🟢 Green | 良好 |
| 0.8-0.9 | 🟡 Yellow | やや懸念 |
| 0.7-0.8 | 🟠 Orange | 懸念 |
| 0.7未満 | 🔴 Red | 深刻 |

---

## 🌳 マインドマップの見方

`docs/MINDMAP.md` には以下の情報が含まれます：

### 1. 階層構造

```
プロジェクト名
├── Phase 1
│   ├── 計画策定 (2/2タスク完了, 100%)
│   │   ├── ✅ 🟠 [TASK-001] プロジェクト憲章作成
│   │   └── ✅ 🟠 [TASK-002] キックオフミーティング開催
│   └── 要件定義 (1/2タスク完了, 50%)
│       ├── ✅ 🟠 [TASK-003] ユーザーヒアリング実施
│       └── 🔄 🟠 [TASK-004] 要件定義書作成
```

### 2. 絵文字の意味

**ステータス:**
- ✅ 完了
- 🔄 進行中
- 📝 未着手
- 🚫 ブロック中
- ❌ キャンセル

**優先度:**
- 🔴 Critical
- 🟠 High
- 🟡 Medium
- 🟢 Low

### 3. サマリーテーブル

Phase別、中カテゴリ別のタスク数と完了率が表形式で表示されます。

---

## 🔧 カスタマイズ

### 進捗計算のロジックを変更

`scripts/calculate-progress.py` の以下の関数を編集：

```python
def calculate_ev(task: Dict) -> float:
    """Earned Value (実績出来高) を計算"""
    status = task.get('status', 'pending')
    weight = task.get('weight', 0)

    # ステータスごとの完了率を変更可能
    status_completion = {
        'done': 1.0,
        'completed': 1.0,
        'in_progress': 0.5,  # 進行中は50%として計算
        'pending': 0.0,
        # ...
    }

    return weight * status_completion.get(status, 0.0)
```

### バッジの色を変更

`generate_progress_badge()`, `generate_spi_badge()`, `generate_cpi_badge()` 関数で色を調整できます。

---

## 📊 活用シーン

### 1. 週次レビューミーティング

```bash
# 週次ミーティング前に実行
python3 scripts/calculate-progress.py
python3 scripts/generate-mindmap.py

# README.mdを開いて進捗を確認
# docs/MINDMAP.mdでタスク全体を俯瞰
```

### 2. ステークホルダー報告

- README.mdの進捗セクションをそのまま報告資料に使用
- SPIとCPIで客観的な進捗を説明

### 3. リスク管理

- SPI < 1.0 のPhaseや中カテゴリを特定
- CPI < 1.0 のタスクで工数超過を検知
- ブロック中のタスクを早期発見

---

## 🔁 GitHub Actionsとの連携

定期的に自動更新する場合は、GitHub Actionsを設定します：

```yaml
name: Update Progress

on:
  schedule:
    # 毎週月曜日 9:00 JSTに実行
    - cron: '0 0 * * 1'
  workflow_dispatch:

jobs:
  update-progress:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Calculate progress
        run: python3 scripts/calculate-progress.py

      - name: Generate mindmap
        run: python3 scripts/generate-mindmap.py

      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add README.md docs/MINDMAP.md
          git commit -m "Update progress: $(date +%Y-%m-%d)" || echo "No changes"
          git push
```

---

## ❓ FAQ

### Q1: 進捗率が正しく計算されない

**A**: tasks.jsonの以下を確認してください：
- 各タスクに `weight` フィールドが設定されている
- 各タスクの `status` が正しい（done, in_progress, pending など）
- `start_date`, `end_date` フィールドが設定されている

### Q2: README.mdに進捗セクションが追加されない

**A**: README.mdが存在することを確認してください。存在しない場合はスキップされます。

### Q3: SPIやCPIが0.00になる

**A**: 以下の原因が考えられます：
- すべてのタスクが未着手（PV, EVが0）
- タスクに `weight` が設定されていない
- タスクに日付が設定されていない

---

## 📚 関連ドキュメント

- [中カテゴリ管理ガイド](MID_CATEGORY_GUIDE.md)
- [日次レポートガイド](DAILY_REPORT_GUIDE.md)
- [スケジュール更新ガイド](SCHEDULE_UPDATE_GUIDE.md)

---

**作成日**: 2026-01-18
**更新日**: 2026-01-18
