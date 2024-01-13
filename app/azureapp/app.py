import os
from openai import AzureOpenAI
from flask import Flask,render_template, request, redirect, url_for, session, jsonify, current_app
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

response = client.chat.completions.create(
    model="GPT35TURBO", # model = "deployment_name".
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
        {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
        {"role": "user", "content": "Do other Azure AI services support this too?"}
    ]
)

res = response.choices[0].message.content


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

def try_login(username, password):
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    cur.execute('SELECT id, password FROM account WHERE name = %s', (username,))
    account = cur.fetchone()
    cur.close()
    conn.close()
    if account and account[1] == password:
        session['user_id'] = account[0]  # ユーザーIDをセッションに保存
        return True
    return False

# セッションからユーザーIDを取得
def get_user_id_from_session():
    return session.get('user_id')

def try_signup(username, password):
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    # ユーザー名が既に存在するかどうかをチェック
    cur.execute('SELECT id FROM account WHERE name = %s', (username,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return False  # 既に存在するユーザー名
    # 新しいアカウントを作成
    cur.execute('INSERT INTO account (name, password) VALUES (%s, %s)', (username, password))
    user_id = cur.lastrowid  # 新しいユーザーIDを取得
    conn.commit()
    cur.close()
    conn.close()
    session['user_id'] = user_id  # ユーザーIDをセッションに保存
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
    return render_template('home.html', username=get_user(), projects=projects())

#Create Newボタンを押したときの処理
@app.route('/goal')
def goal():
    return render_template('goal.html')

#目標設定
@app.route('/create_project', methods=['POST'])
def create_project():
    try:
        # セッションからユーザーIDを取得
        user_id = get_user_id_from_session()
        if not user_id:
            current_app.logger.error('User not logged in')
            return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

        # JSONデータを取得
        data = request.get_json()
        if not data:
            current_app.logger.error('No JSON data sent')
            return jsonify({'status': 'error', 'message': 'No JSON data sent'}), 400

        # JSONデータから各フィールドを取得
        system_name = data.get('systemName')
        days_to_make = data.get('makeDay')
        features = data.get('features')
        print(features)
        features = str(features)
        print(features)
        
        # 必須フィールドの存在を確認
        if not all([system_name, days_to_make, features]):
            current_app.logger.error('Missing data for required fields')
            return jsonify({'status': 'error', 'message': 'Missing data for required fields'}), 400
        
        # リストデータをJSON文字列に変換してデータベースに保存
        features_json = json.dumps(data.get('features'))
        
        # データベースに接続してプロジェクト情報を挿入
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
        cur.execute('INSERT INTO projects (user_id, system_name, days_to_make, features) VALUES (%s, %s, %s, %s)', 
                    (user_id, system_name, days_to_make, features_json))
        conn.commit()
        cur.close()
        conn.close()
        
        current_app.logger.info('Project created successfully')
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        current_app.logger.error(f'Error creating project: {e}')
        # 例外が発生した場合は、エラーメッセージを返す
        return jsonify({'status': 'error', 'message': str(e)}), 500


#目標のリスト生成
def projects():
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    cur.execute('SELECT id, system_name FROM projects WHERE user_id = %s', (session.get('user_id'),))
    project_list = cur.fetchall()
    cur.close()
    conn.close()
    return project_list



#目標削除
@app.route('/delete_goal/<int:goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    # ユーザー認証の確認
    user_id = get_user_id_from_session()
    if user_id is None:
        return jsonify({'status': 'error', 'message': 'Authentication required'}), 401

    # データベース接続
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()

    # ユーザーIDとgoal_idが一致するタスクを確認
    cur.execute('SELECT id FROM goals WHERE id = %s AND user_id = %s', (goal_id, user_id))
    goal = cur.fetchone()
    if goal is None:
        cur.close()
        conn.close()
        return jsonify({'status': 'error', 'message': 'Goal not found'}), 404

    # タスクの削除
    cur.execute('DELETE FROM goals WHERE id = %s', (goal_id,))
    conn.commit()
    
    cur.close()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Goal deleted successfully'}), 200

#カレンダーに目標を追加するための処理
@app.route('/get_goals_for_calendar', methods=['GET'])
def get_goals_for_calendar():
    user_id = get_user_id_from_session()
    conn = mysql.connector.connect(**config)
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT id, objective AS title, deadline AS start FROM goals WHERE user_id = %s', (user_id,))
    events = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(events)


#Azure APIキー接続確認
@app.route('/openai')
def openai():
    
    return res

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

