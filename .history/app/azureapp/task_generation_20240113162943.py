import re

def task(text_data):
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
                detail_pattern = rf"{date}：{task} - (.*?)(?=[\d+日目]|[以上]|$)|{date}:{task} - (.*?)(?=[\d+日目]|[以上]|$)"
                detail_matches = re.findall(detail_pattern, line)

                # 空でない詳細を抽出
                details = []
                for match in detail_matches:
                    detail = next((t for t in match if t), None)
                    if detail:
                        details.extend([d.strip() for d in detail.split('-') if d.strip()])
                        flag = 1

                    tasks[date][task.strip()] = details
                    
    #指定の形式外の場合の処理
    if flag == 0:
        return False

    return tasks

# 結果を表示
for date, task_info in tasks.items():
    print(f"日数: {date}")
    for task, details in task_info.items():
        print(f"  タスク: {task}")
        for i, detail in enumerate(details):
            print(f"    詳細{i+1}: {detail}")
