import os
from flask import Flask,render_template, request, redirect, url_for, session
import mysql.connector
from datetime import timedelta, datetime
import json
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
