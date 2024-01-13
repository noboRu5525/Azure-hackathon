
import re


# テキストデータ
text_data = """
1日目-10日目: Pythonの基礎学習 - Pythonの基本構文、データ型、制御フロー、関数などの復習 - Pythonの標準ライブラリの学習と実践 - Firebaseの基本的な使い方の学習とデータベースのセットアップ 11日目-20日目: Pythonの応用とFirebaseの学習 - Pythonのオブジェクト指向プログラミング（OOP）の復習と応用 - Firebaseを使用してデータの読み書きを行う方法の学習 - カメラ撮影した画像から食材を検出するための画像認識モデルの学習 21日目-30日目: FlaskとWebデザインの学習 - Flaskフレームワークを使用したWebアプリケーションの作成方法の学習 - ユーザー認証のためのFirebase Authenticationの導入 - HTMLとCSSの基礎の学習 31日目-40日目: フロントエンドとデータベースの連携 - Flaskアプリケーションにユーザー認証機能の統合 - 冷蔵庫にある食材をデータベースに追加するためのフォームの作成と連携 - データベースから食材情報を取得して表示する機能の実装 41日目-50日目: レシピ機能の開発とデザインの改善 - レシピ生成機能のためのデータベースに含まれる食材を用いたアルゴリズムの開発 - レシピ詳細情報の表示と保存機能の追加 - Webアプリケーションのデザインの改善とユーザビリティの向上 51日目-60日目: 買い物リスト機能の実装とテスト - ユーザーの買い物リスト機能の実装 - 食材の相性の良い組み合わせを考慮して、買うべき食材の提案機能の開発 - テストとバグ修正 61日目-80日目: プロジェクトの最終段階 - ユーザビリティテストとフィードバックの収集 - プロジェクトのデプロイとホスティング - ドキュメンテーションの作成とプロジェクトの完了 この計画はあくまで一例です。個人開発のため、自身のスケジュールとペースに合わせて調整してください。また、新しい技術やコンセプトに取り組む際には、オンラインチュートリアルやドキュメント、コミュニティフォーラムなどの情報源を活用してください。
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
            flag = 1

#if flag == 0:
    

# 結果を表示
for date, task_info in tasks.items():
    print(f"日数: {date}")
    for task, details in task_info.items():
        print(f"  タスク: {task}")
        for i, detail in enumerate(details):
            print(f"    詳細{i+1}: {detail}")

