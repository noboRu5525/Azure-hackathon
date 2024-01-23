# 基本イメージとしてPythonの公式イメージを使用
FROM python:3.9.7

# 作業ディレクトリを設定
WORKDIR /app

ENV FLASK_APP=app

# 必要なPythonライブラリをインストール
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install Authlib
RUN pip install google-api-python-client
RUN pip install google-auth 
RUN pip install google-auth-oauthlib 
RUN pip install google-auth-httplib2
