import re

#生成された文章からタスクに分割する関数
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
        return "tasks"

    return tasks



#テスト用
text_data = """
1日目-5日目：Pythonの基礎学習 - Pythonの文法、データ型、制御構造などの基本的な概念を学習します。 - Pythonの開発環境のセットアップを行います。 6日目-7日目：Firebaseの基礎学習とアカウントの設定 - Firebaseの基本的な機能やアカウントの作成方法を学習します。 8日目-10日目：FirebaseのAuthentication機能の学習と実装 - FirebaseのAuthentication機能について学習し、ユーザーの登録とログイン機能を作成します。 11日目-14日目：FirebaseのCloud Firestoreを利用したデータベースの設計と学習 - FirebaseのCloud Firestoreを使ってデータベースの設計方法を学習し、食材のデータベースを作成します。 - データの追加と照会の機能を実装します。 15日目-20日目：カメラで撮影した画像をもとに食材を検出する機能の調査と学習 - カメラで撮影した画像を処理して食材を検出する方法について調査し学習します。 - OpenCVやTensorFlowを使用して画像処理を実装します。 21日目-30日目：レシピ生成機能の開発のための食材データベース参照機能の実装 - 食材データベースからレシピを参照する機能を実装します。 - レシピの提案方法についての考察と実装方法の検討を行います。 31日目-40日目：食材の相性判定についての調査と学習 - 食材の相性判定について調査し学習します。 - 食材の相性を考慮してレシピを提案する機能を実装します。 41日目-45日目：Webアプリケーションのフロントエンドの学習とUIの設計と実装 - HTML、CSS、JavaScriptを用いたWebアプリケーションのフロントエンドの学習を行います。 - ユーザーインターフェース（UI）の設計と実装を行います。 46日目-60日目：バックエンドの設計と実装 - Flaskなどのフレームワークを使用したバックエンドの設計と実装を行います。 - データベースとの連携やAPIの作成を行います。 61日目-70日目：システムのテストとバグ修正、機能の改善と追加 - システムのテストとバグ修正を行います。 - ユーザーフィードバックを受けて機能の改善と追加を行います。 71日目-80日目：ドキュメンテーションの作成とアプリケーションのデプロイとサポート - ユーザーマニュアルや開発者ドキュメントなどのドキュメンテーションを作成します。 - アプリケーションのデプロイとサポートを行います。
"""
print(task)
tasks=task(text_data)
# 結果を表示
for date, task_info in tasks.items():
    print(f"日数: {date}")
    for task, details in task_info.items():
        print(f"  タスク: {task}")
        for i, detail in enumerate(details):
            print(f"    詳細{i+1}: {detail}")
