
import re


# テキストデータ
text_data = """
以下は、80日間の開発期間を最大限に活用するためのタスクと計画の提案です。 Day 1-5: - Pythonの基礎学習 - カメラでの画像の撮影と処理についての調査と学習 Day 6-7: - Firebaseの基礎学習とアカウントの設定 Day 8-10: - FirebaseのAuthentication機能の学習と実装 - ユーザーの登録とログイン機能を作成 Day 11-14: - FirebaseのCloud Firestoreを利用したデータベースの設計と学習 - 食材のデータベースを作成し、データの追加と照会の実装 Day 15-20: - カメラで撮影した画像をもとに食材を検出する機能の調査と学習 - OpenCVやTensorFlowなどのライブラリを使用して画像処理を実装 Day 21-30: - レシピ生成機能の開発のために、食材データベースからレシピを参照する機能の実装 - レシピの提案方法についての考察と実装方法の検討 Day 31-40: - 食材の相性判定についての調査と学習 - 食材の相性を考慮してレシピを提案する機能の実装 Day 41-45: - HTML、CSS、JavaScriptを用いたWebアプリケーションのフロントエンドの学習 - ユーザーインターフェース（UI）の設計と実装 Day 46-60: - Flaskなどのフレームワークを使用したバックエンドの設計と実装 - データベースとの連携やAPIの作成 Day 61-70: - システムのテストとバグ修正 - ユーザーフィードバックを受けての機能の改善と追加 Day 71-80: - ドキュメンテーションの作成（ユーザーマニュアル、開発者ドキュメントなど） - アプリケーションのデプロイとサポート この計画では、異なる言語やツールの学習や実装タスクを段階的に進めることにより、より効率的な目標達成を図っています。また、余裕をもって80日間の期間を設定しており、詳細なタスクの分割を行っているため、スケジュールの調整や進捗管理がしやすくなっています。
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
            detail_pattern = rf"{date}：{task} - (.*?)(?=[\d+日目]|[以上]|$)|{date}:{task} - (.*?)(?=[\d+日目]|[以上]|$)"
            detail_matches = re.findall(detail_pattern, line)

            # 空でない詳細を抽出
            details = []
            for match in detail_matches:
                detail = next((t for t in match if t), None)
                if detail:
                    details.extend([d.strip() for d in detail.split('-') if d.strip()])

                tasks[date][task.strip()] = details

if flag == 0:
    print("nononononnononononononononon")

# 結果を表示
for date, task_info in tasks.items():
    print(f"日数: {date}")
    for task, details in task_info.items():
        print(f"  タスク: {task}")
        for i, detail in enumerate(details):
            print(f"    詳細{i+1}: {detail}")
