# ベースイメージとしてPython 3.11の軽量版を使用
FROM python:3.11-slim

# 作業ディレクトリを/appに設定
WORKDIR /app

# 依存関係ファイルをコピー
COPY requirements.txt .
# 必要なPythonパッケージをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションの全ファイルをコピー
COPY . .

# Flaskアプリで使用する8000番ポートを公開
EXPOSE 8000

# Azure Web Appモードを有効化する環境変数を設定
ENV AZURE_WEBAPP_MODE=true

# アプリケーションを起動
CMD ["python", "app.py"]