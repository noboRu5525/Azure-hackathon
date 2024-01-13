import os
from openai import AzureOpenAI
from flask import Flask,render_template, request, redirect, url_for, session
import mysql.connector
from datetime import timedelta, datetime
import json

#APIキー
client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_KEY"),  
  api_version="2023-05-15"
)

def test():
        response = client.chat.completions.create(
            model="GPT35TURBO16K",  # model = "deployment_name".
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "個人開発をしているのですが、目標を達成するためのタスクとその計画を考えて欲しいです。目標を達成するための学習計画を作成してください。また計画は、全体的な戦略と日単位の活動を作成してください。計画では、使用する具体的なプログラム言語やツール（APIなど）を詳細に記載してください。また、使用したことのある言語の学習は必要ありません。\n・制作したいもの：食材管理アプリケーション\n・具体的な機能: カメラで撮影した画像をもとに冷蔵庫の中にある食材を検出して管理、データベースに搭載されている食材からレシピを生成、相性の良い食材を考えて、買うべき食材を提案する\n・制作日数：120日（1週間を7日とする）\n・使用したことのある言語：Python、HTML、CSS"}
            ]
        )
        return response.choices[0].message.content
