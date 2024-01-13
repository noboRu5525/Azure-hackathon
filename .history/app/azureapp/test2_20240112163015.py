
import re


# テキストデータ
text_data = """
以下は、80日間の学習計画の例です。この計画では、Pythonと関連する技術、Firebase、HTML、CSS、JavaScriptに焦点を当てます。学習計画を立てる際には、自身のスキルレベルや以前の経験に基づいて調整してください。 Day 1-10: - Pythonの基本構文、データ型、制御フロー、関数などの復習 - Pythonの標準ライブラリの学習と実践 - Firebaseの基本的な使い方の学習とデータベースのセットアップ Day 11-20: - Pythonのオブジェクト指向プログラミング（OOP）の復習と応用 - Firebaseを使用してデータの読み書きを行う方法の学習 - カメラ撮影した画像から食材を検出するための画像認識モデルの学習 Day 21-30: - Flaskフレームワークを使用したWebアプリケーションの作成方法の学習 - ユーザー認証のためのFirebase Authenticationの導入 - HTMLとCSSの基礎の学習 Day 31-40: - Flaskアプリケーションにユーザー認証機能の統合 - 冷蔵庫にある食材をデータベースに追加するためのフォームの作成と連携 - データベースから食材情報を取得して表示する機能の実装 Day 41-50: - レシピ生成機能のためのデータベースに含まれる食材を用いたアルゴリズムの開発 - レシピ詳細情報の表示と保存機能の追加 - Webアプリケーションのデザインの改善とユーザビリティの向上 Day 51-60: - ユーザーの買い物リスト機能の実装 - 食材の相性の良い組み合わせを考慮して、買うべき食材の提案機能の開発 - テストとバグ修正 Day 61-80: - ユーザビリティテストとフィードバックの収集 - プロジェクトのデプロイとホスティング - ドキュメンテーションの作成とプロジェクトの完了 この計画はあくまで一例です。個人開発のため、自身のスケジュールとペースに合わせて調整してください。また、新しい技術やコンセプトに取り組む際には、オンラインチュートリアルやドキュメント、コミュニティフォーラムなどの情報源を活用してください。
"""

# 正規表現パターンの更新
date_pattern = r"\d+日目-\d+日目|Day \d+-+\d" # 日付範囲のパターン
task_pattern = r"：(.*?) - "
detail_pattern = r"- (.*?)[。]"

# 辞書に格納
tasks = {}
for line in text_data.split("\n"):
    date_match = re.findall(date_pattern, line)
    for date in date_match:
        task_pattern = rf"{date}：(.*?) - "
        task_matches = re.findall(task_pattern, line)
        tasks[date] = {}

        for task in task_matches:
            detail_pattern = rf"{date}：{task} - (.*?)(?=[\d+日目]|[以上]|$ )"
            detail_matches = re.findall(detail_pattern, line)
            
            # 詳細が複数ある場合は分割してリストに格納
            details = []
            for detail in detail_matches:
                details.extend([d.strip() for d in detail.split('-') if d.strip()])

            tasks[date][task] = details
            flag = o0



# 結果を表示
for date, task_info in tasks.items():
    print(f"日数: {date}")
    for task, details in task_info.items():
        print(f"  タスク: {task}")
        for i, detail in enumerate(details):
            print(f"    詳細{i+1}: {detail}")

