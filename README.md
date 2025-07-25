# PMアシスタント

PMアシスタントは、会議の録音データを分析し、会議のサマリーや議事録を自動生成するSlackアプリケーションです。Azure Blob StorageとHULFT Squareを連携させて、音声データの処理と分析を行います。

## 機能概要

- Slackコマンドから会議録音データのアップロードと分析リクエスト
- Azure Blob Storageを使用した音声ファイルの保存
- HULFT Squareを利用した音声の文字起こしと分析
- 会議のサマリーと議事録の自動生成
- Slackへの分析結果の通知

## 技術仕様

### 環境変数

以下の環境変数が必要です：

- `SLACK_BOT_TOKEN`: Slackボットトークン (xoxb- から始まる)
- `SLACK_APP_TOKEN`: Slackアプリトークン (xapp- から始まる)
- `AZURE_STORAGE_ACCOUNT_NAME`: Azure Storageアカウント名
- `AZURE_STORAGE_ACCOUNT_KEY`: Azure Storageアカウントキー
- `HSQ_SIGNING_SECRET`: HULFT Square認証用パスワード
- `AZURE_WEBAPP_MODE`: Azure Web Appモードで実行する場合は "true" に設定

### Slack権限

- `commands`: スラッシュコマンド実行
- `chat:write`: メッセージ送信
- `users:read`: ユーザー情報取得
- `views:open`: モーダル表示
- `channels:read`: チャンネル情報取得
- `groups:read`: プライベートチャンネル情報取得
- `mpim:read`: マルチパーソンDM情報取得
- `im:read`: DM情報取得

### 個別分析エリアの入力例
```
1. 変更管理の追加費用について合意する
2. 6月中に検収する方針で合意する
3. UIの仕様を確定させる
```

## インストール方法

1. リポジトリをクローン
   ```
   git clone <repository-url>
   cd pmassistant
   ```

2. 依存関係のインストール
   ```
   pip install -r requirements.txt
   ```

3. 環境変数の設定
   ```
   # .envファイルを作成して環境変数を設定
   ```

4. アプリケーションの実行
   ```
   python app.py
   ```

## 実行モード

このアプリケーションは2つの実行モードをサポートしています：

1. **ローカルモード**: デフォルトのモードで、Socket Modeのみで実行されます。
2. **Azure Web Appモード**: `AZURE_WEBAPP_MODE=true` を設定すると、Socket ModeとFlaskサーバーのハイブリッドモードで実行されます。

## Azure Blob Storage

このアプリケーションはAzure Blob Storageを使用して、以下の2つのコンテナを利用します：

- `audio`: 音声ファイルを保存するコンテナ
- `transcriptions`: 文字起こし結果を保存するコンテナ

SAS (Shared Access Signature) URLを生成して、これらのコンテナへの一時的なアクセスを提供します。

## フォーム構造

現在のフォームには以下の入力フィールドが含まれています：

- `box_url`: Box上の録画/音声ファイルの共有リンク（URL）
- `agenda`: MTGアウトライン（会議の計画）

注意: 以前のバージョンに含まれていた以下のフィールドは現在コメントアウトされています：
- `project_name`: プロジェクト名
- `manager_name`: プロジェクト責任者
- `member_name`: プロジェクトメンバー

## HULFT Square連携

HULFT Squareと連携して以下の処理を行います：

1. 認証とトークン取得
   - `get_access_token()`: ログインAPIを使用してアクセストークンを取得
   - `update_refresh_token()`: アクセストークンを更新

2. API呼び出し
   - `invoke_hsq_translation_api()`: 音声ファイル変換APIを呼び出し

## トラブルシューティング

- **SAS URL認証エラー**: アカウントキーが最新であることを確認し、時刻のずれを考慮して開始時間を現在時刻より5分前に設定
- **Slack権限エラー**: 必要な権限がすべて付与されていることを確認
- **HULFT Square認証エラー**: 
  - アクセストークンが有効であることを確認
  - 401 Unauthorized エラーの場合、トークンが無効または期限切れの可能性があります
  - リクエストパラメータの形式を確認（特に配列を文字列に変換しているか）
- **データ型エラー**: 
  - `slack_channel_member`パラメータが文字列形式であることを確認
  - 配列データを送信する場合は、適切に文字列に変換（例: `", ".join(array)`）
- **フォーム送信エラー**:
  - `KeyError: 'member_name'`などのエラーが発生した場合は、フォーム定義（`pm_assistant_form_block.py`）と処理コード（`app.py`）の整合性を確認してください
  - フォームフィールドがコメントアウトされている場合、対応する処理コードもコメントアウトする必要があります

## デバッグモード

`DEBUG_MODE = True` に設定することで、詳細なログ出力と追加のSlackメッセージが表示されます。トラブルシューティング時に有効にしてください。