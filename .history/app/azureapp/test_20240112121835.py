import re

# テキストデータ
text_data = """
目標: 食材管理アプリケーションの制作 全体的な戦略: 1. 必要な機能を洗い出し、優先度を設定する 2. プログラミング言語やツールの選定と学習 3. プロジェクトの構造やデータベースの設計 4. 機能ごとに開発を進めていく 5. テストとバグ修正を行い、最終的なアプリケーションを完成させる 日単位の活動: Day 1: 1. プロジェクトの概要を考える 2. 必要な機能を洗い出す 3. 優先度を設定する Day 2 - Day 7: 1. Pythonの学習 2. Pythonを使用した画像処理の基礎を学ぶ Day 8 - Day 14: 1. Pythonの学習を続ける 2. プロジェクトに必要なデータベースの設計を行う Day 15 - Day 21: 1. プログラミング言語PythonでのGUI開発を学習する 2. 必要な画面の設計を考える Day 22 - Day 42: 1. 冷蔵庫の中の食材を検出するための画像処理プログラムを開発する - 使用するプログラム言語: Python - 使用するツール: OpenCV Day 43 - Day 63: 1. データベースに搭載されている食材からレシピを生成するプログラムを開発する - 使用するプログラム言語: Python - 使用するツール: SQL, Pandas Day 64 - Day 84: 1. 相性の良い食材を考え、買うべき食材を提案するプログラムを開発する - 使用するプログラム言語: Python - 使用するツール: Pandas Day 85 - Day 105: 1. ユーザーインターフェースの開発を行う - 使用するプログラム言語: Python, HTML, CSS - 使用するツール: Flask Day 106 - Day 120: 1. テストとバグ修正を行い、最終的なアプリケーションを完成させる 以上が、120日間の学習計画です。一つ一つのタスクを着実にこなしていくことで、目標である食材管理アプリケーションの制作を達成できるでしょう。頑張ってください！
"""

# 正規表現パターン
task_pattern = r"(\d+\. [^\d]+)"
date_pattern = r"Day \d+( - Day \d+)?"

# 辞書に格納
tasks = {}
current_date = None  # 現在の日付範囲を保持

for line in text_data.split("\n"):
    date_match = re.search(date_pattern, line)
    if date_match:
        current_date = date_match.group()  # 日付範囲を更新
        continue  # 日付行の処理が完了したので、次の行へ

    task_matches = re.findall(task_pattern, line)
    for task in task_matches:
        if current_date:  # 有効な日付範囲がある場合のみ
            tasks[task] = current_date

# 結果を表示
for task, date in tasks.items():
    print(f"タスク: {task}, 日数: {date}")
