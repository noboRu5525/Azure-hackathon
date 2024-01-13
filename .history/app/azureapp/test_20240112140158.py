
import re


# テキストデータ
text_data = """
以下は、80日間の期間内に食材管理アプリケーションを制作するための学習計画です。 1日目-3日目：Pythonの基礎学習 - Pythonの文法、データ型、制御構造などの基本的な概念を学習します。 - Pythonの開発環境のセットアップを行います。 4日目-8日目：HTMLとCSSの学習 - HTMLの基本構造、タグ、属性などを学習します。 - CSSのセレクタ、プロパティなどの基礎を学びます。 9日目-11日目：JavaScriptの基礎学習 - JavaScriptの文法、変数、関数、イベントハンドリングなどの基本を学習します。 12日目-17日目：PythonとFirebaseの連携 - Firebaseの基本的な機能を学習します。具体的には、データベースの作成、データの追加・取得・削除などを学びます。 - PythonからFirebaseにアクセスする方法を学びます。 18日目-20日目：画像処理関連のライブラリの学習 - Pythonの画像処理ライブラリ（例：OpenCV）を学習します。 - 画像の読み込み、処理、保存などの基本的な操作を学びます。 21日目-29日目：画像認識の学習 - 画像認識についての基本的な理論を学びます。 - Pythonを使用して画像からオブジェクトを検出する方法を学びます。 30日目-39日目：データベースへの食材情報の追加・管理機能の実装 - カメラで撮影した画像から検出した食材情報をFirebaseデータベースに追加する機能を実装します。 - 食材の管理（追加・更新・削除）機能を実装します。 40日目-54日目：レシピ生成機能の実装 - データベースに搭載されている食材からレシピを生成する機能を実装します。 - 食材の相性を考慮してレシピを生成するロジックを実装します。 55日目-66日目：買うべき食材の提案機能の実装 - 冷蔵庫の中にある食材の情報とデータベースに搭載されている食材情報を比較し、買うべき食材を提案する機能を実装します。 - 食材の相性や頻度、賞味期限などを考慮して提案を行うロジックを実装します。 67日目-80日目：動作確認とデバッグ、UI/UXの改善 - 実装した機能の動作確認を行い、必要に応じてデバッグを行います。 - アプリケーションのユーザビリティを高めるために、UI/UXの改善を行います。 以上が制作日数内でアプリケーションを完成させるための学習計画です。始める前に、各期間の間隔や内容を調整し、自分のペースに合わせることをお勧めします。
"""

# 正規表現パターンの更新
date_pattern = r"\d+日目-\d+日目"  # 日付範囲のパターン
task_pattern = r"：(.*?) - "
detail_pattern = r"- (.*?)[。]"

# 辞書に格納
tasks = {}
for line in text_data.split("\n"):
    date_match = re.search(date_pattern, line)
    if date_match:
        date = date_match.group()
        tasks[date] = {}

        task_matches = re.finditer(task_pattern, line)
        for match in task_matches:
            task = match.group(1)
            start = match.end()

            # 次のタスクの位置を見つける
            next_task = re.search(task_pattern, line[start:])
            if next_task:
                end = start + next_task.start()
            else:
                end = len(line)

            # タスクの詳細を抽出
            details = re.findall(detail_pattern, line[start:end])
            tasks[date][task] = details

# 結果を表示
for date, task_info in tasks.items():
    print(f"日数: {date}")
    for task, details in task_info.items():
        print(f"  タスク: {task}")
        for detail in details:
            print(f"    詳細: {detail}")