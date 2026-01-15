# 週次進捗レポート自動送信 セットアップ手順

このドキュメントでは、週次進捗レポートの自動送信機能をセットアップする手順を説明します。

## 概要

- **送信頻度**: 毎週月曜日の朝9時（日本時間）
- **送信方法**: GitHub Actions + SendGrid API
- **レポート内容**: 進捗率（予定vs実績）、完了タスク、進行中タスク、来週予定タスク

## 前提条件

- GitHubリポジトリが作成されている
- `tasks.json` と `schedule.json` がリポジトリに存在する
- SendGridアカウント（または代替メールサービス）

## セットアップ手順

### 1. SendGridアカウントの作成

#### 1.1 アカウント登録

1. [SendGrid公式サイト](https://sendgrid.com/)にアクセス
2. 「Start for Free」をクリック
3. 必要情報を入力してアカウントを作成
   - Email
   - Password
   - Company Name（個人の場合は「Individual」等）

**無料プラン**: 月間100通まで送信可能（週次レポートなら十分）

#### 1.2 Sender Identityの設定

メール送信には送信元アドレスの認証が必要です。

1. SendGridダッシュボードにログイン
2. 左メニューから「Settings」→「Sender Authentication」を選択
3. **Single Sender Verification**（推奨）を選択:
   - 「Create New Sender」をクリック
   - From Name: プロジェクト名（例: "顧問ミドル運用PJ"）
   - From Email Address: 送信元メールアドレス
   - Reply To: 返信先メールアドレス
   - Company Address等を入力
   - 「Create」をクリック
4. 入力したメールアドレスに確認メールが届くので、リンクをクリックして認証

#### 1.3 API Keyの作成

1. SendGridダッシュボードで「Settings」→「API Keys」を選択
2. 「Create API Key」をクリック
3. API Key情報を入力:
   - API Key Name: `weekly-progress-report`（任意の名前）
   - API Key Permissions: **Full Access**（または「Mail Send」のみ）
4. 「Create & View」をクリック
5. **重要**: 表示されたAPI Keyをコピーして安全な場所に保管
   - この画面を閉じると二度と表示されません
   - 例: `SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 2. GitHub Secretsの設定

GitHubリポジトリにSecrets（機密情報）を登録します。

#### 2.1 リポジトリのSettings画面を開く

1. GitHubリポジトリのページを開く
2. 「Settings」タブをクリック
3. 左メニューから「Secrets and variables」→「Actions」を選択

#### 2.2 Secretsを追加

「New repository secret」をクリックして、以下の3つのSecretを追加します。

**Secret 1: SENDGRID_API_KEY**
- Name: `SENDGRID_API_KEY`
- Secret: SendGridで作成したAPI Key
  ```
  SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  ```

**Secret 2: REPORT_TO_EMAIL**
- Name: `REPORT_TO_EMAIL`
- Secret: レポート送信先のメールアドレス
  ```
  your-email@example.com
  ```
  - 複数の宛先に送る場合はカンマ区切り:
    ```
    user1@example.com, user2@example.com, user3@example.com
    ```

**Secret 3: REPORT_FROM_EMAIL**
- Name: `REPORT_FROM_EMAIL`
- Secret: SendGridで認証した送信元メールアドレス
  ```
  noreply@yourdomain.com
  ```
  - **注意**: SendGridのSender Authenticationで認証したアドレスと同じである必要があります

### 3. GitHub Actionsの有効化

#### 3.1 リポジトリにコードをpush

```bash
# リポジトリをclone（まだの場合）
git clone https://github.com/your-username/project-requirements-system.git
cd project-requirements-system

# 変更をcommit & push
git add .github/workflows/weekly-progress-report.yml
git add scripts/send-progress-report.py
git add docs/PROGRESS_REPORT_SETUP.md
git commit -m "Add weekly progress report automation"
git push origin main
```

#### 3.2 Actionsの権限確認

1. GitHubリポジトリの「Settings」→「Actions」→「General」を開く
2. 「Workflow permissions」で以下を確認:
   - 「Read and write permissions」が選択されているか
   - 「Allow GitHub Actions to create and approve pull requests」がチェックされているか（必須ではない）

### 4. 動作テスト

#### 4.1 手動実行でテスト

1. GitHubリポジトリの「Actions」タブを開く
2. 左側のワークフロー一覧から「Weekly Progress Report」を選択
3. 「Run workflow」ボタンをクリック
4. ブランチを選択して「Run workflow」を実行

#### 4.2 実行ログの確認

1. ワークフローの実行が開始されます
2. ジョブ名「send-progress-report」をクリックして詳細を確認
3. 各ステップの実行状況とログを確認:
   - ✅ Checkout repository
   - ✅ Set up Python
   - ✅ Install dependencies
   - ✅ Generate and send progress report

#### 4.3 メール受信確認

- 設定したメールアドレスに進捗レポートが届くことを確認
- 迷惑メールフォルダも確認してください

### 5. 自動実行の確認

- 設定完了後、**毎週月曜日の午前9時（日本時間）**に自動実行されます
- 初回の自動実行は次の月曜日です
- GitHub Actionsの「Actions」タブで実行履歴を確認できます

## トラブルシューティング

### メールが送信されない

**原因1: SendGrid API Keyが無効**
- 解決策: SendGridダッシュボードでAPI Keyが有効か確認
- 必要に応じて新しいAPI Keyを作成してGitHub Secretsを更新

**原因2: Sender Authenticationが未完了**
- 解決策: SendGridで送信元アドレスの認証を完了させる
- 認証メールのリンクをクリックしたか確認

**原因3: GitHub Secretsの設定ミス**
- 解決策: GitHub Secrets の名前が正確か確認
  - `SENDGRID_API_KEY` (スペースや大文字小文字に注意)
  - `REPORT_TO_EMAIL`
  - `REPORT_FROM_EMAIL`

**原因4: 送信元アドレスが未認証**
- 解決策: `REPORT_FROM_EMAIL` が SendGridで認証済みのアドレスか確認

### GitHub Actionsが実行されない

**原因1: cronスケジュールの設定ミス**
- 確認: `.github/workflows/weekly-progress-report.yml` の `cron` 設定
- デフォルト: `'0 0 * * 1'`（毎週月曜日 00:00 UTC = 日本時間 9:00）

**原因2: リポジトリが非アクティブ**
- GitHub Actionsは非アクティブなリポジトリでは実行されません
- 解決策: リポジトリに定期的にcommitする、または手動実行で確認

**原因3: Actionsが無効化されている**
- 確認: Settings → Actions → General で Actions が有効か確認

### Python依存関係のエラー

**エラー: `ModuleNotFoundError: No module named 'sendgrid'`**
- 原因: sendgridパッケージがインストールされていない
- 解決策: ワークフローファイルで `pip install sendgrid` が実行されているか確認

### ローカルテスト方法

```bash
# 環境変数を設定
export SENDGRID_API_KEY="SG.your-api-key"
export REPORT_TO_EMAIL="your-email@example.com"
export REPORT_FROM_EMAIL="noreply@yourdomain.com"

# Pythonパッケージをインストール
pip install sendgrid

# スクリプトを実行
cd /path/to/project-requirements-system
python scripts/send-progress-report.py
```

## 代替方法（SendGrid以外）

SendGridが使えない場合の代替手段を紹介します。

### オプション1: Gmail SMTPを使用

Gmail アカウントの「アプリパスワード」機能を使用してメール送信できます。

#### 前提条件
- Gmailアカウントで2段階認証が有効
- アプリパスワードを生成

#### スクリプトの変更

`scripts/send-progress-report.py` を以下のように変更:

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email_smtp(from_email: str, to_emails: List[str], subject: str, html_content: str):
    """Gmail SMTPを使用してメール送信"""
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_password = os.environ.get("GMAIL_APP_PASSWORD")

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ', '.join(to_emails)

    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_email, smtp_password)
        server.send_message(msg)
```

#### GitHub Secretsの変更
- `SENDGRID_API_KEY` の代わりに `GMAIL_APP_PASSWORD` を設定
- `REPORT_FROM_EMAIL` にGmailアドレスを設定

### オプション2: AWS SES (Simple Email Service)

AWS アカウントをお持ちの場合、SESを使用できます。

- 無料枠: 月間62,000通（EC2からの送信）
- 料金: $0.10 per 1,000 emails

詳細は [AWS SESドキュメント](https://aws.amazon.com/ses/) を参照してください。

### オプション3: Azure Communication Services

Microsoft Azure アカウントをお持ちの場合、Azure Communication Servicesを使用できます。

詳細は [Azure Communication Services](https://azure.microsoft.com/services/communication-services/) を参照してください。

## よくある質問（FAQ）

### Q1: 送信頻度を変更できますか？

はい。`.github/workflows/weekly-progress-report.yml` の `cron` 設定を変更してください。

```yaml
# 毎週月曜日 9:00 JST
- cron: '0 0 * * 1'

# 毎週金曜日 17:00 JST (8:00 UTC)
- cron: '0 8 * * 5'

# 毎日 9:00 JST
- cron: '0 0 * * *'
```

### Q2: 複数の宛先に送信できますか？

はい。`REPORT_TO_EMAIL` Secretをカンマ区切りで設定してください。

```
user1@example.com, user2@example.com, user3@example.com
```

### Q3: レポートの内容をカスタマイズできますか？

はい。`scripts/send-progress-report.py` の `generate_html_report` メソッドを編集してください。

例: バッファ消費状況を追加
```python
# バッファ消費状況を取得
buffer_info = self.get_buffer_consumption()

# HTMLテンプレートに追加
html_content += f"""
    <h3>📊 バッファ消費状況</h3>
    <p>Phase 1: {buffer_info['phase1']}日消費</p>
    <p>Phase 2: {buffer_info['phase2']}日消費</p>
    <p>Phase 3: {buffer_info['phase3']}日消費</p>
"""
```

### Q4: SendGridの無料プランで十分ですか？

はい。週次送信なら月4通程度なので、無料プラン（月100通）で十分です。

### Q5: プロジェクト終了後も送信され続けますか？

はい。GitHub Actionsは設定を無効化するまで継続します。

プロジェクト終了後は以下のいずれかを実施:
1. ワークフローファイルを削除
2. ワークフローを無効化（GitHubのActionsタブから）
3. リポジトリをアーカイブ

## サポート

問題が解決しない場合:

1. [GitHub Issues](https://github.com/your-repo/project-requirements-system/issues) で質問
2. SendGrid公式ドキュメント: https://docs.sendgrid.com/
3. GitHub Actions公式ドキュメント: https://docs.github.com/actions

---

**最終更新**: 2026-01-15
**バージョン**: 1.0
