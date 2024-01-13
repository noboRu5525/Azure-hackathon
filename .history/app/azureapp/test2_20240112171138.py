
import re


# テキストデータ
text_data = """

"""

# 正規表現パターンの更新
date_pattern = r"\d+日目-\d+日目|Day \d+-+\d+" # 日付範囲のパターン
task_pattern = r" ：(.*?) - "
detail_pattern = r"- (.*?)[。]"

flag = 0
# 辞書に格納
tasks = {}
for line in text_data.split("\n"):
    date_match = re.findall(date_pattern, line)
    for date in date_match:
        task_pattern = rf"{date}：(.*?) - |{date}:(.*?) - "
        task_matches = re.findall(task_pattern, line)
        tasks[date] = {}

        for match in task_matches:
            # 空でないタスク名を取得
            task = next((t for t in match if t), None)
            if task:
                detail_pattern = rf"{date}：{task} - (.*?)(?=[\d+日目]|[以上]|$)"
                detail_matches = re.findall(detail_pattern, line)
                
                # 詳細が複数ある場合は分割してリストに格納
                details = [d.strip() for d in detail_matches[0].split('-') if d.strip()] if detail_matches else []

                tasks[date][task.strip()] = details

                flag = 1

if flag == 0:
    print(2)

# 結果を表示
for date, task_info in tasks.items():
    print(f"日数: {date}")
    for task, details in task_info.items():
        print(f"  タスク: {task}")
        for i, detail in enumerate(details):
            print(f"    詳細{i+1}: {detail}")
