import os
from openai import AzureOpenAI
from flask import Flask,render_template, request, redirect, url_for, session
import mysql.connector
from datetime import timedelta, datetime
import json

app = Flask(__name__)
app.secret_key="fjkjfgkdkjkd"
app.permanent_session_lifetime = timedelta(minutes=180)


#APIキー
client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_KEY"),  
  api_version="2023-05-15"
)




#データベース接続情報
config = {
        'user': 'root',
        'password': 'hackathon78864',
        'host': 'db',
        'port': '3306',
        'database': 'records',
        }

#アカウント情報取得
def get_account():
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    cur.execute('select * from account')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

#アカウント管理(要変更)
@app.route("/admin")
def admin():
    return render_template("admin.html", accounts=get_account())

#ログイン機能
@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/check_login", methods=['POST'])
def check_login():
    user, pw = (None, None)
    if 'user' in request.form:
        user = request.form['user']
    if 'pw' in request.form:
        pw = request.form['pw']
    if (user is None) or (pw is None):
        return redirect('/')
    if try_login(user, pw) == False:
        return """
        <h1>ユーザー名かパスワードの間違い</h1>
        <p><a href="/">→戻る</a></p>
        """
    return redirect("/home")

@app.route("/signup")
def signup_page():
    return render_template("signup.html")

@app.route("/check_signup", methods=['POST'])
def check_signup():
    user, pw= (None, None)
    if 'user' in request.form:
        user = request.form['user']
    if 'pw' in request.form:
        pw = request.form['pw']
    if (user is None) or (pw is None):
        return redirect('/')
    if user_checker(user) == False:
        return """
        <h1>同じユーザー名が存在します。違うユーザー名にしてください。</h1>
        <p><a href="/">→戻る</a></p>
        """
    if try_signup(user, pw) == False:
        return """
        <h1>ユーザー名かパスワードかメールアドレスが不正です</h1>
        <p><a href="/login">→戻る</a></p>
        """
    return redirect('/login')

@app.route('/logout')
def logout_page():
    try_logout()
    return """
    <h1>ログアウトしました</h1>
    <p><a href="/login">→戻る</a></p>
    """

def is_login():
    if 'login'  in session:
        return True
    return False

def try_login(user,password):
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    cur.execute('select * from account')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    rows_dict = {rows[i][0]: rows[i][1] for i in range(len(rows))}
    if not user in rows_dict:
        return False
    if rows_dict[user] != password:
        return False
    session['login'] = user
    return True

def try_signup(user,password):
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    cur.execute('INSERT INTO account VALUES (%s, %s)',(user,password))
    conn.commit()
    cur.close()
    conn.close()
    return True

def try_logout():
    session.pop('login', None)
    return True

def get_user():
    if is_login():
        return session['login']
    return 'not login'

def user_checker(user):
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    cur.execute('select * from account')
    results = cur.fetchall()
    cur.close()
    conn.close()
    for result in results:
        if user in result:
            return False
    return True

#ホーム画面
@app.route("/home")
def home():
    if not is_login():
        return """
        <h1>ログインしてください</h1>
        <p><a href="/">→ログインする</a></p>
        """
    return render_template('home.html', username=get_user())

#Azure APIキー接続確認
@app.route('/test')
def test():
    try:
        response = client.chat.completions.create(
            model="GPT35TURBO16K",  # model = "deployment_name".
            messages=[
                {"role": "system", "content": "ユーザーから与えられた条件の文章構成に修正する"},
                {"role": "user", "content": "以下は、80日間の学習計画の例です。この計画では、Pythonと関連する技術、Firebase、HTML、CSS、JavaScriptに焦点を当てます。学習計画を立てる際には、自身のスキルレベルや以前の経験に基づいて調整してください。 Day 1-10: - Pythonの基本構文、データ型、制御フロー、関数などの復習 - Pythonの標準ライブラリの学習と実践 - Firebaseの基本的な使い方の学習とデータベースのセットアップ Day 11-20: - Pythonのオブジェクト指向プログラミング（OOP）の復習と応用 - Firebaseを使用してデータの読み書きを行う方法の学習 - カメラ撮影した画像から食材を検出するための画像認識モデルの学習 Day 21-30: - Flaskフレームワークを使用したWebアプリケーションの作成方法の学習 - ユーザー認証のためのFirebase Authenticationの導入 - HTMLとCSSの基礎の学習 Day 31-40: - Flaskアプリケーションにユーザー認証機能の統合 - 冷蔵庫にある食材をデータベースに追加するためのフォームの作成と連携 - データベースから食材情報を取得して表示する機能の実装 Day 41-50: - レシピ生成機能のためのデータベースに含まれる食材を用いたアルゴリズムの開発 - レシピ詳細情報の表示と保存機能の追加 - Webアプリケーションのデザインの改善とユーザビリティの向上 Day 51-60: - ユーザーの買い物リスト機能の実装 - 食材の相性の良い組み合わせを考慮して、買うべき食材の提案機能の開発 - テストとバグ修正 Day 61-80: - ユーザビリティテストとフィードバックの収集 - プロジェクトのデプロイとホスティング - ドキュメンテーションの作成とプロジェクトの完了 この計画はあくまで一例です。個人開発のため、自身のスケジュールとペースに合わせて調整してください。また、新しい技術やコンセプトに取り組む際には、オンラインチュートリアルやドキュメント、コミュニティフォーラムなどの情報源を活用してください。 \n この文章の計画の部分を以下の形式に修正してください。 \n ⚪︎日目-⚪︎日目:タスク -詳細1。 -詳細2。・・・"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return "An error occurred while processing your request."

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

"""
{"role": "system", "content": "You provide support in planning based on the user's goals."},
                {"role": "user", "content": "・制作したいもの：食材管理アプリケーション\n・具体的な機能: カメラで撮影した画像をもとに冷蔵庫の中にある食材を検出して管理、データベースに搭載されている食材からレシピを生成、相性の良い食材を考えて、買うべき食材を提案する\n・制作日数：80日（1週間を7日とする）\n・使用する言語：Python、HTML、CSS、JavaScript \n・使用ツール：Firebases \n・使用したことのある言語：Python・使用したことのある言語：Python、HTML、CSS \n 個人開発をしているのですが、目標を効率的に達成するためのタスクとその計画を考えて欲しいです。目標を効率よく達成するための学習計画を作成してください。また計画は、日単位の活動を作成してください。計画では、使用する具体的なプログラム言語やツール（APIなど）を詳細に記載してください。また、使用したことのある言語の学習は計画に入れないでください。また、個人開発であるため余裕を持った計画を立てて欲しいです。また、指定された制作日数を最大限に使用してください。"}
                """