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
                {"role": "user", "content": "以下は、80日間の開発期間を最大限に活用するためのタスクと計画の提案です。 Day 1-5: - Pythonの基礎学習 - カメラでの画像の撮影と処理についての調査と学習 Day 6-7: - Firebaseの基礎学習とアカウントの設定 Day 8-10: - FirebaseのAuthentication機能の学習と実装 - ユーザーの登録とログイン機能を作成 Day 11-14: - FirebaseのCloud Firestoreを利用したデータベースの設計と学習 - 食材のデータベースを作成し、データの追加と照会の実装 Day 15-20: - カメラで撮影した画像をもとに食材を検出する機能の調査と学習 - OpenCVやTensorFlowなどのライブラリを使用して画像処理を実装 Day 21-30: - レシピ生成機能の開発のために、食材データベースからレシピを参照する機能の実装 - レシピの提案方法についての考察と実装方法の検討 Day 31-40: - 食材の相性判定についての調査と学習 - 食材の相性を考慮してレシピを提案する機能の実装 Day 41-45: - HTML、CSS、JavaScriptを用いたWebアプリケーションのフロントエンドの学習 - ユーザーインターフェース（UI）の設計と実装 Day 46-60: - Flaskなどのフレームワークを使用したバックエンドの設計と実装 - データベースとの連携やAPIの作成 Day 61-70: - システムのテストとバグ修正 - ユーザーフィードバックを受けての機能の改善と追加 Day 71-80: - ドキュメンテーションの作成（ユーザーマニュアル、開発者ドキュメントなど） - アプリケーションのデプロイとサポート この計画では、異なる言語やツールの学習や実装タスクを段階的に進めることにより、より効率的な目標達成を図っています。また、余裕をもって80日間の期間を設定しており、詳細なタスクの分割を行っているため、スケジュールの調整や進捗管理がしやすくなっています。 \n この文章の計画の部分を以下の形式に修正してください。 \n ⚪︎日目-⚪︎日目：タスク -詳細1。 -詳細2。・・・ \n具体例は次のような感じです: 1日目-3日目：Pythonの基礎学習 - Pythonの文法、データ型、制御構造などの基本的な概念を学習します。 - Pythonの開発環境のセットアップを行います。"}
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
                {"role": "user", "content": "・制作したいもの：食材管理アプリケーション\n・具体的な機能: カメラで撮影した画像をもとに冷蔵庫の中にある食材を検出して管理、データベースに搭載されている食材からレシピを生成、相性の良い食材を考えて、買うべき食材を提案する\n・制作日数：80日（1週間を7日とする）\n・使用する言語：Python、HTML、CSS、JavaScript \n・使用ツール：Firebases \n・使用したことのある言語：Python・使用したことのある言語：Python、HTML、CSS \n 個人開発をしているのですが、目標を効率的に達成するためのタスクとその計画を考えて欲しいです。目標を効率よく達成するための学習計画を作成してください。また計画は、日単位の活動を作成してください。計画では、使用する具体的なプログラム言語やツール（APIなど）を詳細に記載してください。また、使用したことのある言語の学習は計画に入れないでください。また、個人開発であるため余裕を持った計画を立てて欲しいです。また、指定された制作日数を最大限に使用し細かくタスクを分け、できるだけ詳細に記述してください。"}
                """