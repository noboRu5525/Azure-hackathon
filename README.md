# Azure-hackathon
# はじめに
任意ディレクトリにて
git clone https://github.com/noboRu5525/Azure-hackathon.git
でダウンロード

# 起動
**docker compose up --build**すると起動する

起動後**http://localhost/**
にアクセス

http://localhost/test
でAPI接続確認できた

# モジュール
必要なモジュールがあったら**requirements.txt**に追記する
その後**docker compose up --build**する

# バックエンド
基本的にはapp.pyを書いて実装　ファイル分けした方が可読性アップかな？

# フロントエンド
基本的には
Azure-hackathon/app/azureapp/**templates**
と
Azure-hackathon/app/azureapp/static/**css**
の中のファイルを弄ることになるかと
