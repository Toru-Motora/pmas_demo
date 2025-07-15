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

- `SLACK_BOT_TOKEN`: Slackボットトークン
- `SLACK_APP_TOKEN`: Slackアプリトークン
- `AZURE_STORAGE_ACCOUNT_NAME`: Azure Storageアカウント名
- `AZURE_STORAGE_ACCOUNT_KEY`: Azure Storageアカウントキー
- `HSQ_SIGNING_SECRET`: HULFT Square認証用シークレット
- `HSQ_REFRESH_TOKEN`: HULFT Squareトークン更新用トークン

### Slack権限

- `commands`: スラッシュコマンド実行
- `chat:write`: メッセージ送信
- `users:read`: ユーザー情報取得
- `views:open`: モーダル表示
- `channels:read`: チャンネル情報取得
- `groups:read`: プライベートチャンネル情報取得
- `mpim:read`: マルチパーソンDM情報取得
- `im:read`: DM情報取得

### アウトラインの例
```
# 打ち合わせアウトライン

## 1. はじめに (5分)
- **目的とアジェンダ確認**  
  本日のゴールと話し合う内容を共有します。
- **時間配分**  
  各議題に割り当てる時間の確認をします。

## 2. 議題 (残り時間の大部分)
### 議題1: [議題名]（例: プロジェクトA 進捗と課題）
- 現状を共有し、懸念点を提示します。
- 議論を行い、決定事項と次の行動を確認します。

### 議題2: [議題名]（例: 新規案件B 概要と方向性）
- 提案内容を説明します。
- 質疑応答と意見交換を行います。
- 決定事項と次の行動を確認します。

## 3. まとめとネクストアクション (5分)
- **決定事項の再確認**  
  本日決まったことを簡潔に共有し、認識を合わせます。
- **ネクストアクションと担当・期限**  
  誰が、何を、いつまでにやるのかを明確にします。
- 閉会の挨拶
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

## Azure Blob Storage

このアプリケーションはAzure Blob Storageを使用して、以下の2つのコンテナを利用します：

- `audio`: 音声ファイルを保存するコンテナ
- `transcriptions`: 文字起こし結果を保存するコンテナ

SAS (Shared Access Signature) URLを生成して、これらのコンテナへの一時的なアクセスを提供します。

## HULFT Square連携

HULFT Squareと連携して以下の処理を行います：

1. 音声ファイルの文字起こし
2. 会議内容の分析
3. サマリーと議事録の生成

## トラブルシューティング

- **SAS URL認証エラー**: アカウントキーが最新であることを確認し、時刻のずれを考慮して開始時間を現在時刻より5分前に設定
- **Slack権限エラー**: 必要な権限がすべて付与されていることを確認
- **HULFT Square認証エラー**: リフレッシュトークンが有効であることを確認