# 基本イメージとしてPythonの公式イメージを使用
FROM python:3.8-slim

# 作業ディレクトリを設定
WORKDIR /app

# 必要なPythonライブラリをインストール
# FlaskとAzure Open AIのPython SDKをインストール
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコピー
COPY . .

# ポート5000を開放
EXPOSE 5001

ENV FLASK_APP=app.py

# アプリケーションを起動
CMD ["flask", "run", "--host=0.0.0.0"]
