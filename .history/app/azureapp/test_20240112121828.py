import re

# テキストデータ
text_data = """
...（テキストデータ）...
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
