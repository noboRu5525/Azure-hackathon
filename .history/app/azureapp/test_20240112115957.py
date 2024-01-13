import os
from openai import AzureOpenAI
from flask import Flask,render_template, request, redirect, url_for, session
import mysql.connector
from datetime import timedelta, datetime
import json
import re

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

import re

# テキストデータ
text_data = """
Day 1: 1. プロジェクトの概要を考える 2. 必要な機能を洗い出す 3. 優先度を設定する
Day 2 - Day 7: 1. Pythonの学習 2. Pythonを使用した画像処理の基礎を学ぶ
...（他のテキスト）...
Day 106 - Day 120: 1. テストとバグ修正を行い、最終的なアプリケーションを完成させる
"""

# 正規表現パターン
task_pattern = r"(\d+\. [^\d]+)"
date_pattern = r"Day \d+( - Day \d+)?"

# 辞書に格納
tasks = {}
for line in text_data.split("\n"):
    date_match = re.search(date_pattern, line)
    task_matches = re.findall(task_pattern, line)
    if date_match and task_matches:
        date = date_match.group()
        for task in task_matches:
            tasks[task] = date

# 結果を表示
for task, date in tasks.items():
    print(f"タスク: {task}, 日数: {date}")
