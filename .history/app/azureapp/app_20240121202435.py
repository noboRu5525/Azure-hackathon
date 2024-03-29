import os
from openai import AzureOpenAI
from flask import Flask,render_template, request, redirect, url_for, session, jsonify, current_app
import mysql.connector, random
from datetime import timedelta, datetime
import json
from task_generation import make_task, make_task2, make_task3, extract_languages_from_ai_response, extract_all_languages

app = Flask(__name__)
app.secret_key="fjkjfgkdkjkd"
app.permanent_session_lifetime = timedelta(minutes=180)

#デバックモード追加
# 環境変数 FLASK_ENV を取得し、設定に適用する
flask_env = os.environ.get('FLASK_ENV')
if flask_env == "development":
    app.config['DEBUG'] = True
    # その他の開発環境特有の設定
else:
    app.config['DEBUG'] = False


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

def convert_days_range_to_dates(days_range, start_date):
    start_day, end_day = [int(day) for day in days_range.replace('日目', '').split('-')]
    start_date = start_date + timedelta(days=start_day - 1)
    end_date = start_date + timedelta(days=end_day - 1)
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

#生成AIの作成した文章をさらに整える
def formatting(text_data, text_lang):
    # Decide which messages to use based on the language
    if text_lang == "英語でテキスト生成してください":
        messages = [
            {"role": "system", "content": "Modify the text structure as per user's condition"},
            {"role": "user", "content": f"{text_data}\nPlease modify the plan part of this text so that it does not break into a new line. Use the following format:\n 〇 day-〇 : Task - Detail 1. - Detail 2. ...\n\nAn example would be like this:\nDay 1-3: Learning Python Basics - Learn the basic concepts of Python syntax, data types, and control structures. - Set up the Python development environment."}
        ]
    else:
        messages = [
            {"role": "system", "content": "ユーザーから与えられた条件の文章構成に修正する"},
            {"role": "user", "content": f"{text_data} \n この文章の計画の部分を改行しないように以下の形式に修正してください。 \n 〇日目-〇日目：タスク -詳細1。 -詳細2。・・・ \n具体例は次のような感じです: 1日目-3日目：Pythonの基礎学習 - Pythonの文法、データ型、制御構造などの基本的な概念を学習します。 - Pythonの開発環境のセットアップを行います。"}
        ]
    # Call the function with the prepared messages
    response = client.chat.completions.create(
        model="GPT35TURBO",
        messages=messages
    )
    return response.choices[0].message.content

def advice(text):
    messages = [
            {"role": "system", "content": "タスクについてアドバイスをしてください"},
            {"role": "user", "content": f"{text} \n このタスクはどのように取り組むべきでしょうか？英語で答えてください。"}
        ]
    # Call the function with the prepared messages
    response = client.chat.completions.create(
        model="GPT35TURBO",
        messages=messages
    )
    return response.choices[0].message.content

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
        <h1>Wrong username or password</h1>
        <p><a href="/">→Return</a></p>
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
        <h1>Same username exists. Please use a different username.</h1>
        <p><a href="/">→Reruen</a></p>
        """
    if try_signup(user, pw) == False:
        return """
        <h1>Invalid username, password, or email address</h1>
        <p><a href="/login">→Return</a></p>
        """
    return redirect('/login')

@app.route('/logout')
def logout_page():
    try_logout()
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ログアウト</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f0f0f0;
                text-align: center;
                padding-top: 50px;
            }

            h1 {
                color: #333;
                font-size: 24px;
            }

            p {
                margin-top: 20px;
                font-size: 18px;
            }

            a {
                text-decoration: none;
                color: #007bff;
                font-weight: bold;
            }

            a:hover {
                color: #0056b3;
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>Logged out</h1>
        <p><a href="/login">→return</a></p>
    </body>
    </html>
    """

def is_login():
    if 'user_id'  in session:
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
    session.pop('user_id', None)
    return True

def get_user():
    if is_login():
        return session['user_id']
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
        <h1>Please login</h1>
        <p><a href="/">→Log in</a></p>
        """

    user_id = session.get('user_id')

    # データベースに接続して、ユーザーに関連するタスクとその詳細を取得
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    cur.execute('''
        SELECT t.id, t.days_range, t.task_name, td.detail
        FROM tasks t
        JOIN task_details td ON t.id = td.task_id
        JOIN learning_plans lp ON t.plan_id = lp.id
        WHERE lp.user_id = %s
    ''', (user_id,))
    raw_tasks = cur.fetchall()
    cur.close()
    conn.close()

    # タスクデータを整理
    tasks = {}
    for task_id, days_range, task_name, detail in raw_tasks:
        if task_id not in tasks:
            tasks[task_id] = {
                'task_id': task_id,
                'days_range': days_range,
                'task_name': task_name,
                'details': []
            }
        tasks[task_id]['details'].append(detail)
    first_four_tasks = {k: tasks[k] for k in list(tasks)[:4]} # 最初の4要素を取得

    # get_projects 関数の呼び出し
    project_response = get_projects()
    projects = json.loads(project_response.data)
    
    #list_projects関数の呼び出し
    projects = list_projects()

    return render_template('home.html', username=get_user(), projects=projects, tasks=first_four_tasks.values())

#Create Newボタンを押したときの処理
@app.route('/goal')
def goal():
    return render_template('goal.html')

#プロジェクトを押したときの処理
@app.route('/projects')
def projects():
    return render_template('projects.html')

#FAQを押したときの処理
@app.route('/faq')
def faq():
    return render_template('faq.html')

#Contactを押したときの処理
@app.route('/contact')
def contact():
    return render_template('contact.html')

#目標設定
@app.route('/create_project', methods=['POST'])
def create_project():
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
    language = data.get('language', '')
    category = data.get('category', '')
    systemName = data.get('systemName', '')
    makeDay = data.get('makeDay', '')
    features = data.get('functions', [])
    languages = data.get('languages', [])
    tools = data.get('tools', [])
    selectedColor = data.get("selectedColor", "")
    startDate = data.get("startDate", "")
    
    if(language == "English"):
        text_lang = "英語でテキスト生成してください"
        text_lang_eng="Please generate the text in English."
    else:
        text_lang = ""

    # 必須フィールドの存在を確認
    if not all([category, systemName, makeDay, features, languages, tools]):
        current_app.logger.error('Missing data for required fields')
        return jsonify({'status': 'error', 'message': 'Missing data for required fields'}), 400
        
    # リストデータをJSON文字列に変換してデータベースに保存
    #features_json = json.dumps(data.get('features'))
    #languages_json = json.dumps(languages)
    #tools_json = json.dumps(tools)
    print(type(features))
    print(languages)
    print(tools)
    
    features_json = str(features)
    languages_json = str(languages)
    tools_json = str(tools)
    
    print(type(features_json))
    print(languages_json)
    print(tools_json)
    
    startdate = datetime.now()
        
    # データベースに接続してプロジェクト情報を挿入
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    cur.execute('INSERT INTO projects (user_id, startdate, systemName, makeDay, features, languages, tools) VALUES (%s, %s, %s, %s, %s, %s, %s)', (user_id, startdate, systemName, makeDay, features_json, languages_json, tools_json)) 
    conn.commit()
    cur.close()
    conn.close()
        
    # 各機能を「」で区切って結合
    functions_str = ' \n・'.join(features)
    languages_str = '、'.join(languages)
    tools_str = '、'.join(tools)
    
    if (language == "English"):
        response = client.chat.completions.create(
            model="GPT4", # model = "deployment_name".
            max_tokens=4096,
            messages=[
                {"role": "system", "content": "You provide support in planning based on the user's goals."},
                {"role": "user", "content": f"・制作したいもの： I want to create a project named {systemName}. It will have specific functionalities: {functions_str}. The development will take {makeDay} days, considering a week as 7 days. I will be using programming languages: {languages_str}, and tools: {tools_str}. I am working on this as an individual developer and need help to efficiently achieve my goals. Please create a learning plan in {language} to help me reach these goals effectively. The plan should outline daily activities. Make sure to include detailed information about the specific programming languages and tools (like APIs) that will be used. Do not include learning of languages that I have already used. As this is a personal project, I would like a plan with some flexibility. Utilize the specified development time to its fullest, breaking down tasks in detail and describing them as thoroughly as possible in {language}."},
            ]
        ) 
        res = response.choices[0].message.content
    else:
        # Azure Open AIでタスク生成
        response = client.chat.completions.create(
            model="GPT4", # model = "deployment_name".
            max_tokens=4096,
            messages=[
                {"role": "system", "content": "You provide support in planning based on the user's goals."},
                {"role": "user", "content": f"・制作したいもの：{systemName}\n・具体的な機能: {functions_str}\n・制作日数：{makeDay}日（1週間を7日とする）\n・使用する言語：{languages_str} \n・使用ツール：{tools_str} \n 個人開発をしているのですが、目標を効率的に達成するためのタスクとその計画を考えて欲しいです。目標を効率よく達成するための学習計画を{text_lang}作成してください。また計画は、日単位の活動を作成してください。計画では、使用する具体的なプログラム言語やツール（APIなど）を詳細に記載してください。また、使用したことのある言語の学習は計画に入れないでください。また、個人開発であるため余裕を持った計画を立てて欲しいです。また、指定された制作日数を最大限に使用し細かくタスクを分け、できるだけ詳細に記述してください。\n具体例は次のような感じです: 1日目-3日目：Pythonの基礎学習 - Pythonの文法、データ型、制御構造などの基本的な概念を学習します。 - Pythonの開発環境のセットアップを行います。"},
            ]
        )
        res = response.choices[0].message.content

    make_task_data = make_task(res)

    if not make_task_data:
            res = formatting(res, text_lang)
            make_task_data = make_task(res)
            if not make_task_data:
                make_task_data = make_task2(res)
                if not make_task_data:
                    make_task_data = make_task3(res)
                
        
    # 日数、タスク、その詳細に分ける
    print(make_task_data)
    
    # セッションからユーザーIDを取得（ユーザーがログインしていることが前提）
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

    # POSTデータを取得（JSON形式のデータが送信されることを前提）
    data = make_task_data
    # データベースに接続
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()

    try:
        # データベースに学習プランを挿入
        cur.execute('INSERT INTO learning_plans (user_id) VALUES (%s)', (user_id,))
        plan_id = cur.lastrowid  # 新しく挿入された学習プランのIDを取得

        # 各タスクとその詳細をデータベースに挿入
        for days_range, tasks in data.items():
            for task_name, details in tasks.items():
                cur.execute('INSERT INTO tasks (plan_id, days_range, task_name) VALUES (%s, %s, %s)',
                            (plan_id, days_range, task_name))
                task_id = cur.lastrowid  # 新しく挿入されたタスクのIDを取得

                for detail in details:
                    cur.execute('INSERT INTO task_details (task_id, detail) VALUES (%s, %s)',
                                (task_id, detail))

        # 変更をコミット
        conn.commit()
    except mysql.connector.Error as err:
        # エラーが発生した場合はロールバック
        conn.rollback()
        print(f"An error occurred: {err}")
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    finally:
        # カーソルとコネクションを閉じる
        cur.close()
        conn.close()


                
    #タスク生成回数カウンター
    count = 0
    """
    while(count <=  5):
        #生成された文章からタスクに分割する
        if make_task(res):
            make_task_data = make_task(res)
            count = 5
        else:
            res = formatting(res)
            count += 1
    """
    if not make_task_data:
        # タスクを生成できなかった場合のレスポンス
        return jsonify({'status': 'error', 'message': 'タスクを生成できませんでした', 'redirect': False})
    else:
        # タスク生成が成功した場合のレスポンス
        return jsonify({'status': 'success', 'data': make_task_data, 'redirect': True, 'redirect_url': '/home'})
    
    
    
    

#生成AIが生成したタスクを登録
@app.route('/create_plan', methods=['POST'])
def create_plan():
    # セッションからユーザーIDを取得（ユーザーがログインしていることが前提）
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

    # POSTデータを取得（JSON形式のデータが送信されることを前提）
    data = request.get_json()
    
    # データベースに接続
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    
    try:
        # データベースに学習プランを挿入
        cur.execute('INSERT INTO learning_plans (user_id) VALUES (%s)', (user_id,))
        plan_id = cur.lastrowid  # 新しく挿入された学習プランのIDを取得

        # 各タスクとその詳細をデータベースに挿入
        for task in data:
            days_range = task['日数']
            task_name = task['タスク']
            cur.execute('INSERT INTO tasks (plan_id, days_range, task_name) VALUES (%s, %s, %s)',
                        (plan_id, days_range, task_name))
            task_id = cur.lastrowid  # 新しく挿入されたタスクのIDを取得
            
            for detail in task['詳細']:
                cur.execute('INSERT INTO task_details (task_id, detail) VALUES (%s, %s)',
                            (task_id, detail))

        # 変更をコミット
        conn.commit()

        return jsonify({'status': 'success', 'plan_id': plan_id})
    except Exception as e:
        # エラーが発生した場合はロールバック
        conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        # データベースの接続を閉じる
        cur.close()
        conn.close()


    if not make_task_data:
        return jsonify({'message': 'タスクを生成できませんでした'})
    

    return jsonify(make_task_data)

    
# 目標のリスト生成
def list_projects():
    try:
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
        cur.execute('SELECT id, systemName FROM projects WHERE user_id = %s', (session.get('user_id'),))
        project_list = cur.fetchall()
        cur.close()
        conn.close()
        return project_list
    except:
        return []

@app.route('/send_card_detail', methods=['POST'])
def send_card_detail():
    data = request.json
    card_detail = data.get('text')
    advice_txet = advice(card_detail)
    # card_detail を処理
    return jsonify({'status': 'success', 'text': advice_txet})

@app.route('/get_ai_response', methods=['POST'])
def get_ai_response():
    data = request.json
    user_input = data.get('text')
    # ここでAI応答を生成
    response = client.chat.completions.create(
        model="GPT35TURBO", # model = "deployment_name".
        messages=[
            {"role": "system", "content": "ユーザーの手助けをする"},
            {"role": "user", "content": f"{user_input}"},
        ]
    )
    ai_response = response.choices[0].message.content
    return jsonify({'response': ai_response})

@app.route('/get_ai_response_eng', methods=['POST'])
def get_ai_response_eng():
    data = request.json
    user_input = data.get('text')
    # ここでAI応答を生成
    response = client.chat.completions.create(
        model="GPT35TURBO", # model = "deployment_name".
        messages=[
            {"role": "system", "content": "help the user"},
            {"role": "user", "content": f"{user_input}"},
        ]
    )
    ai_response = response.choices[0].message.content
    return jsonify({'response': ai_response})

#プロジェクトごとに色を割り当てる
def id_to_color(project_id):
    # プロジェクトのIDを基に一貫した色を生成するロジック
    # 例として、IDをハッシュ化し、ハッシュ値を色コードに変換します
    hash_value = hash(str(project_id))
    # ハッシュ値を0から0xFFFFFF（16進数でFFFFFF）の範囲に収まるようにします
    color_code = '#{:06x}'.format(hash_value % 0xFFFFFF)
    return color_code

#プロジェクト名をカレンダーに反映させる
@app.route('/get_projects')
def get_projects():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, startDate, systemName, makeDay FROM projects where user_id = %s", (session.get('user_id'),) )
        projects_data = cursor.fetchall()
        projects_list = []
        for projectId, startDate, systemName, makeDay in projects_data:
            color = id_to_color(projectId)  # IDに基づいて色を生成
            end_date = startDate + timedelta(days=makeDay)
            projects_list.append({
                "id": projectId,
                "title": systemName,
                "start": startDate.strftime('%Y-%m-%d'),
                "end": end_date.strftime('%Y-%m-%d'),
                "allDay": True,
                "color": color,
            })
        return jsonify(projects_list)
    except Exception as e:
        print(e)
        return str(e)
    finally:
        cursor.close()
        conn.close()
        
@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'ログインが必要です。'}), 403

    # データベースに接続
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    
    try:
        # ユーザーIDとタスクIDを確認してタスクが存在するかを検証
        cur.execute('''
            SELECT t.id FROM tasks t
            JOIN learning_plans lp ON t.plan_id = lp.id
            WHERE t.id = %s AND lp.user_id = %s
        ''', (task_id, user_id))
        task = cur.fetchone()

        if not task:
            return jsonify({'status': 'error', 'message': 'タスクが見つかりません。'}), 404

        # タスクを削除
        cur.execute('DELETE FROM tasks WHERE id = %s', (task_id,))
        conn.commit()

        return jsonify({'status': 'success', 'message': 'タスクが削除されました。'})
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error: {err}")
        return jsonify({'status': 'error', 'message': '内部エラーが発生しました。'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/auto_select_language', methods=['POST'])
def auto_select_language():
    # リクエストからJSONデータを取得
    data = request.get_json()

    # データが正しく受け取れたかどうかをチェック
    if not data or 'functions' not in data:
        return jsonify({'status': 'error', 'message': '無効なデータ'}), 400

    # 機能のリストを変数に格納
    functions = data['functions']

    print(functions)

    response = client.chat.completions.create(
        model="GPT35TURBO", # model = "deployment_name".
        messages=[
            {"role": "system", "content": "適切なプログラム言語を考案する"},
            {"role": "user", "content": f"{functions}\n上記の機能を実装するために最適なプログラム言語を、Python, Java, C/C++, C#, Swift, PHP, Ruby, HTML/CSS, Javascript, Kotlin, GO, R, SQLの中から選んでください。複数の言語が必要な場合は組み合わせを提案してください。同じ役割である言語はどちらか1つだけ選択するようにしてください"},
        ]
    )
    ai_response = response.choices[0].message.content

    # AIの応答から使用言語を抽出
    use_lang = extract_languages_from_ai_response(ai_response)

    # 応答から言語が見つからない場合は、全ての言語を抽出
    if not use_lang:
        use_lang = extract_all_languages(ai_response)
        if not use_lang:
            return jsonify({'message': '使用言語を生成できませんでした'})
    
    # 使用言語のリストをJSONで返す
    return jsonify({'languages': use_lang})

#タスクの取得
    @app.route('/get_tasks')
    def get_tasks():
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT id, days_range, task_name FROM tasks")
            tasks_data = cursor.fetchall()
            tasks_list = []
            for taskId, daysRange, taskName in tasks_data:
                start_date, end_date = daysRange.split(' to ')
                tasks_list.append({
                    "id": taskId,
                    "title": taskName,
                    "start": start_date,
                    "end": end_date,
                    "allDay": True
                })
            print(tasks_list)
            print(type(tasks_list))
            return jsonify(tasks_list)
        except Exception as e:
            print(e)
            return str(e)
        finally:
            cursor.close()
            conn.close()


@app.route('/test')
def test():
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
    return res


@app.route('/get_pass_score', methods=['POST'])
def get_pass_score():
    data = request.get_json()

    qualification_name = data.get('qualificationName')
    
    response = client.chat.completions.create(
        model="GPT4", # model = "deployment_name".
        messages=[
            {"role": "system", "content": "適切なプログラム言語を考案する"},
            {"role": "user", "content": f"{qualification_name}\の合格点数を教えてください。\n 以下の形式で答えてください\n 合格点:〇〇点 \n 具体例→合格点:700点"},
        ]
    )
    pass_score  = response.choices[0].message.content

    return jsonify(passScore=pass_score)

@app.route('/submit_qualification_data', methods=['POST'])
def submit_qualification_data():
    # セッションからユーザーIDを取得（この部分は省略しています）
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
    qualificationName = data.get('qualificationName', '')
    selectedColor = data.get('selectedColor', '')
    testDate = data.get('testDate', '')
    currentSkill = data.get('currentSkill', '')
    currentScore = data.get('currentScore', '')
    targetSkill = data.get('targetSkill', '')
    targetScore = data.get('targetScore', '')

    if(currentSkill=="試験を受けたことがある"):
        currentSkill = f"現状：{currentScore}点"
    else:
        currentSkill = f"現状：{currentSkill}"

    if(targetSkill=="自己目標を立てる"):
        targetSkill = f"目標：{targetScore}点"
    else:
        targetSkill = f"目標：{targetSkill}"
        
    # 試験日をdatetimeオブジェクトに変換
    test_date_obj = datetime.strptime(testDate, '%Y-%m-%d')  # '2023-12-31'のような形式を想定

    # 現在の日付を取得
    current_date = datetime.now()

    # 差分を計算
    days_until_test = (test_date_obj - current_date).days

    # ここでデータを処理します（データベースへの保存など）
    print(qualificationName)
    
    # Azure Open AIでタスク生成
    embedding = client.embeddings.create(
        model="ADA", # model = "deployment_name".
        input=f"・取得したい資格：{qualificationName} \n ・試験日：{testDate} \n ・{currentSkill} \n  ・{targetSkill}\n 目標を達成するための計画を立ててください。"
    )
    print(embedding)
    

      # Azure Open AIでタスク生成
    response = client.chat.completions.create(
        model="GPT4", # model = "deployment_name".
        max_tokens=4096,
        messages=[
            {"role": "system", "content": "You provide support in planning based on the user's goals."},
            {"role": "user", "content": f"・取得したい資格：{qualificationName} \n ・試験日：{testDate} \n ・{currentSkill} \n  ・{targetSkill}\n 目標を達成するための計画を立ててください。"},
        ]
       
    )
    res = response.choices[0].message.content

    print(res)

    # 応答を返す
    return jsonify({"message": f"{qualificationName}"})


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)