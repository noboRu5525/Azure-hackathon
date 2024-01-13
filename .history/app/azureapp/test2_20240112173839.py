
import re


# テキストデータ
text_data = """
1日目-25日目: 学習フェーズ - 1. Pythonの基礎学習とWeb開発フレームワークの学習（5日） - Pythonの基本構文やプログラムの制御フローについて学習する。 - FlaskなどのWeb開発フレームワークの基礎を学ぶ。 - 2. HTMLとCSSの学習（5日） - HTMLの構造とタグについて学習する。 - CSSを使ったデザインの基礎を学ぶ。 - 3. JavaScriptの学習（5日） - JavaScriptの基本構文やDOM操作について学習する。 - 4. Firebaseの学習（5日） - Firebaseの基本的な機能やデータベースの使い方について学習する。 - 5. 食材管理アプリケーションの概要設計（5日） - 必要な機能やデータベースの構造などを考えて、アプリケーションの概要設計を行う。 26日目-85日目: 開発フェーズ - 1. 冷蔵庫内の食材検出機能の実装（10日） - OpenCVや機械学習のライブラリを使用して、冷蔵庫の中にある食材を検出する機能を実装する。 - 2. 食材データベースの実装（15日） - Firebaseを使用して、食材情報をデータベースに格納する機能を実装する。 - 3. レシピ生成機能の実装（10日） - 食材データベースから相性の良い食材を選んでレシピを生成する機能を実装する。 - 4. 買うべき食材の提案機能の実装（10日） - レシピや冷蔵庫の中の食材情報をもとに、買うべき食材の提案をする機能を実装する。 - 5. ログイン機能の実装（5日） - ユーザー別の食材情報を管理するためのログイン機能を実装する。 - 6. 栄養素計算機能の実装（10日） - 生成されたレシピ情報から栄養素を計算し、ユーザーの健康管理をする機能を実装する。 86日目-90日目: テスト、デバッグ、ドキュメンテーション - 1. アプリケーションのテストとデバッグ（3日） - 全体の機能をテストし、バグを修正する。 - 2. ユーザーマニュアルと開発ドキュメントの作成（2日） - アプリケーションの使い方を説明するユーザーマニュアルと、開発に関するドキュメントを作成する。
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
