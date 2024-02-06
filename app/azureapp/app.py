import os
from openai import AzureOpenAI
from flask import Flask,render_template, request, redirect, url_for, session, jsonify, current_app
import mysql.connector, random
from datetime import timedelta, datetime
import json
from task_generation import make_task, make_task2, make_task3, extract_languages_from_ai_response, extract_all_languages,make_task_eng
from authlib.integrations.flask_client import OAuth #Google認証
import secrets #Google認証
from google_auth_oauthlib.flow import Flow #Google Calendar
from googleapiclient.discovery import build #Google Calendar
from google.oauth2.credentials import Credentials #Google Calendar
from googleapiclient.discovery import build #Google Calendar

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

#Googleログイン認証
###########################################################################################################################
oauth = OAuth(app)

# Google OAuth設定
google = oauth.register(
    name='Azure',
    client_id='1007338565716-n2pd8nuusdc3b7n3lprd0k8anlfe3a80.apps.googleusercontent.com',
    client_secret='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',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile https://www.googleapis.com/auth/calendar.readonly'},
)

@app.route('/')
def welcome():
    return '<a href="/login">Sign in with Google</a>'

@app.route('/login')
def login():
    session['nonce'] = secrets.token_urlsafe()  # nonceを生成してセッションに保存
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri, nonce=session['nonce'])

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('token', None)
    return redirect('/')

@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    nonce = session.pop('nonce', None)
    user_info = google.parse_id_token(token, nonce=nonce)
    session['email'] = user_info.get('email')

    # トークン情報をセッションに保存
    session['credentials'] = {
        'token': token.get('access_token'),
        'refresh_token': token.get('refresh_token'),
        'token_uri': token.get('token_uri'),
        'client_id': token.get('client_id'),
        'client_secret': token.get('client_secret'),
        'scope': token.get('scope')
    }
    return redirect('/check_login')

###########################################################################################################################

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

###########################################################################################################################
#Google認証に合わせたログイン
@app.route("/check_login", methods=['GET','POST'])
def check_login():
    user = session.get('email', None)
    pw = '099878362'
    if 'user' is None:
        return redirect('/admin')
    if try_login(user, pw) == False:
        try_signup(user, pw)
    if try_login(user, pw) == False:
        return redirect('/admin')
    return redirect("/home")

def try_login(username, password):
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    cur.execute('SELECT id, name, password FROM account WHERE name = %s', (username,))
    account = cur.fetchone()
    cur.close()
    conn.close()
    if account and account[2] == password:
        session['user_id'] = account[0]
        print(session['user_id'])
        return True
    return False

# セッションからユーザーIDを取得
def get_user_id_from_session():
    return session.get('user_id')


def try_signup(username, password):
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    # ユーザー名が既に存在するかどうかをチェック
    cur.execute('SELECT name FROM account WHERE name = %s', (username,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return False  # 既に存在するユーザー名
    # 新しいアカウントを作成
    cur.execute('INSERT INTO account (name, password) VALUES (%s, %s)', (username, password))
    conn.commit()
    cur.close()
    conn.close()
    return True

def check_signup():
    user = session.get('email', None)
    pw = '099878362'
    if (user is None):
        return redirect('/admin')
    if user_checker(user) == False:
        return redirect('/home')
    return redirect('/home')

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

###########################################################################################################################

#ホーム画面
@app.route("/home")
def home():
    user = session.get('email', None)
    user_id = session.get('user_id', None)
    if user is None:
        return redirect('/')
    if user_id is None:
        return redirect('/')

    # データベースに接続して、ユーザーに関連するタスクとその詳細を取得
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    
    cur.execute('select count(*) from projects where user_id = %s and status != 1', (user_id,))
    incomplete_projects_count = cur.fetchone()[0]
    
    if incomplete_projects_count > 0:
        project_response = get_projects()
        projects = json.loads(project_response.data)
        projects = list_projects()
    else:
        projects = []
    
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

    # get_projects 関数の呼び出し
    project_response = get_projects()
    projects = json.loads(project_response.data)
    
    #list_projects関数の呼び出し
    projects = list_projects()

    #Googleカレンダーのイベントを取得
    calendar_events = get_events_data()
    
    #JSON形式に変換
    calendar_events_json = json.dumps(calendar_events)
    
    return render_template('home.html', username=user, projects=projects, tasks=tasks.values(), events_json=calendar_events_json)

def get_events_data():
    email = dict(session).get('email', None)
    creds_info = session.get('credentials', {})

    if not (email and creds_info.get('token')):
        return []  # イベントがない場合は空のリストを返す

    # GoogleカレンダーAPIの認証情報を設定
    credentials = Credentials(
        token=creds_info['token'],
        refresh_token=creds_info.get('refresh_token'),
        token_uri=creds_info.get('token_uri'),
        client_id=creds_info.get('client_id'),
        client_secret=creds_info.get('client_secret'),
        scopes=creds_info.get('scope')
    )

    # Googleカレンダーサービスの初期化
    service = build('calendar', 'v3', credentials=credentials)

    # 現在の日時をJSTで取得
    now = datetime.utcnow() + timedelta(hours=9)

    # 過去3ヶ月前の日時をJSTで計算
    three_months_ago = now - timedelta(weeks=12)
    three_months_ago_str = three_months_ago.isoformat() + 'Z'

    # 将来3ヶ月後の日時をJSTで計算
    three_months_later = now + timedelta(weeks=12)
    three_months_later_str = three_months_later.isoformat() + 'Z'

    # カレンダーからイベントを取得
    events_result = service.events().list(
        calendarId='primary', 
        timeMin=three_months_ago_str, 
        timeMax=three_months_later_str,
        maxResults=250, 
        singleEvents=True, 
        orderBy='startTime'
        ).execute()
    events = events_result.get('items', [])

    # イベントデータを整形
    formatted_events = []
    for event in events:
        formatted_events.append({
            'title': event.get('summary', 'No Title'),
            'start': event['start'].get('dateTime', event['start'].get('date')),
            'end': event['end'].get('dateTime', event['end'].get('date'))
        })

    return formatted_events

@app.route('/get-calendar-events')
def get_calendar_events():
    # Googleカレンダーのイベントデータを取得
    calendar_events = get_events_data()

    # JSON形式でイベントデータを返す
    return jsonify(calendar_events)

#Projectページ
@app.route('/tasks')
def tasks_page():
    user = session.get('email', None)
    user_id = session.get('user_id', None)
    if user is None:
        return redirect('/')
    if user_id is None:
        return redirect('/')

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
    return render_template('tasks.html', tasks=tasks.values())

#Projectページ
@app.route('/projects')
def projects_page():
    # get_projects 関数の呼び出し
    project_response = get_projects()
    projects = json.loads(project_response.data)
    #list_projects関数の呼び出し
    projects = list_projects()
    return render_template('projects.html',projects=projects)

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
    if not all([category, systemName, makeDay, features, languages, tools, selectedColor, startDate]):
        current_app.logger.error('Missing data for required fields')
        return jsonify({'status': 'error', 'message': 'Missing data for required fields'}), 400
        
    #リストデータをJSON文字列に変換してデータベースに保存
    features_json = json.dumps(data.get('features'))
    languages_json = json.dumps(languages)
    tools_json = json.dumps(tools)
    
    print(type(features))
    print(languages)
    print(tools)
    
    features_json = str(features)
    languages_json = str(languages)
    tools_json = str(tools)
    
    
    print(type(features_json))
    print(languages_json)
    print(tools_json)
        
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

    if (language == "English"):
        make_task_data = make_task_eng(res)
    else:
        make_task_data = make_task(res)

    if not make_task_data:
            if (language == "English"):
                res = formatting(res, text_lang)
                make_task_data = make_task_eng(res)
                """
                if not make_task_data:
                    make_task_data = make_task2(res)
                    if not make_task_data:
                        make_task_data = make_task3(res)
                """
            else:
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
    
    if not make_task_data:
        # タスクを生成できなかった場合のレスポンス
        return jsonify({'status': 'error', 'message': 'タスクを生成できませんでした', 'redirect': False})
    else: 
    # データベースに接続してプロジェクト情報を挿入
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
        cur.execute('INSERT INTO projects (user_id, startDate, systemName, makeDay, features, languages, tools, color) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (user_id, startDate, systemName, makeDay, features_json, languages_json, tools_json, selectedColor)) 
        conn.commit()
        cur.close()
        conn.close()
        
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

# #プロジェクトごとに色を割り当てる
# def id_to_color(project_id):
#     # プロジェクトのIDを基に一貫した色を生成するロジック
#     # 例として、IDをハッシュ化し、ハッシュ値を色コードに変換します
#     hash_value = hash(str(project_id))
#     # ハッシュ値を0から0xFFFFFF（16進数でFFFFFF）の範囲に収まるようにします
#     color_code = '#{:06x}'.format(hash_value % 0xFFFFFF)
#     return color_code

@app.route('/get_projects')
def get_projects():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    try:
        # プロジェクトの情報とRGB形式の色情報を取得します。
        cursor.execute("""
            SELECT id, startDate, systemName, makeDay, color
            FROM projects
            WHERE user_id = %s
        """, (session.get('user_id'),))
        projects_data = cursor.fetchall()
        projects_list = []
        for projectId, startDate, systemName, makeDay, color in projects_data:
            # 色情報がNULLの場合、デフォルトの色を設定
            color = color if color else "rgb(255, 228, 138)"  # デフォルトの色（RGB形式）
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

        
@app.route('/update_task_status/<int:task_id>', methods=['POST'])
def update_task_status(task_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'ログインが必要です。'}), 403

    # リクエストボディからステータスを取得
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'status': 'error', 'message': '無効なリクエストです。'}), 400

    new_status = data['status']

    # データベースに接続
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()
    
    try:
        # タスクのステータスを更新
        cur.execute('''
            UPDATE tasks
            SET status = %s
            WHERE id = %s
            AND user_id = %s
        ''', (new_status, task_id, user_id))
        conn.commit()

        if cur.rowcount == 0:
            return jsonify({'status': 'error', 'message': 'タスクが見つかりません。'}), 404

        return jsonify({'status': 'success', 'message': 'タスクのステータスが更新されました。'})

    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'status': 'error', 'message': f'内部エラーが発生しました。{err}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/check_status/<int:project_id>', methods=['POST'])
def check_status(project_id):
    conn = mysql.connector.connect(**config)
    cur = conn.cursor()

    try:
        # 関連する全てのタスクのstatusが0かどうかを確認
        cur.execute('''
            SELECT COUNT(*) FROM tasks t 
            JOIN learning_plans lp ON t.plan_id = lp.id
            JOIN projects p ON lp.user_id = p.user_id
            WHERE p.id = %s AND t.status != 0
        ''', (project_id,))
        incomplete_task_count = cur.fetchone()[0]

        if incomplete_task_count == 0:
            # 全てのタスクのstatusが0の場合、projectsのstatusを0に変更
            cur.execute('UPDATE projects SET status = 0 WHERE id = %s', (project_id,))
            conn.commit()

        return jsonify({'status': 'success', 'message': 'プロジェクトのステータスが更新されました。'})

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
    
    """
    # Azure Open AIでタスク生成
    embedding = client.embeddings.create(
        model="ADA", # model = "deployment_name".
        input=f"・取得したい資格：{qualificationName} \n ・試験日：あと{days_until_test}日 \n ・{currentSkill} \n  ・{targetSkill}\n 目標を達成するための計画を詳細に立ててください。"
    )
    print(embedding)
    """

      # Azure Open AIでタスク生成
    response = client.chat.completions.create(
        model="GPT4", # model = "deployment_name".
        max_tokens=4096,
        messages=[
            {"role": "system", "content": "You provide support in planning based on the user's goals."},
            {"role": "user", "content": f"・取得したい資格：{qualificationName} \n ・試験日：あと{days_until_test}日 \n ・{currentSkill} \n  ・{targetSkill}\n 目標を達成するための計画を立ててください。また、指定された制作日数を最大限に使用し細かくタスクを分け、できるだけ詳細に記述し試験の具体的な分野への勉強方法などを記載すること。\n以下の形式で回答してください。 \n 〇日目-〇日目：タスク -詳細1。 -詳細2。・・・  \n"},
        ]
       
    )
    res = response.choices[0].message.content

    print(res)

    make_task_data = make_task(res)

    if not make_task_data:
            res = formatting(res, "Japanese")
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
                cur.execute('INSERT INTO tasks (user_id, plan_id, days_range, task_name) VALUES (%s, %s, %s, %s)',
                            (user_id, plan_id, days_range, task_name))
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

@app.route('/submit_qualification_data_eng', methods=['POST'])
def submit_qualification_data_eng():
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

    if(currentSkill=="Have taken the exam"):
        currentSkill = f"CurrentScore：{currentScore}"
    else:
        currentSkill = f"CurrentSkill：{currentSkill}"

    if(targetSkill=="Set a personal target"):
        targetSkill = f"TargetScore：{targetScore}"
    else:
        targetSkill = f"Target：{targetSkill}"

    # 試験日をdatetimeオブジェクトに変換
    test_date_obj = datetime.strptime(testDate, '%Y-%m-%d')  # '2023-12-31'のような形式を想定

    # 現在の日付を取得
    current_date = datetime.now()

    # 差分を計算
    days_until_test = (test_date_obj - current_date).days

    # ここでデータを処理します（データベースへの保存など）
    print(qualificationName)
    
    """
    # Azure Open AIでタスク生成
    embedding = client.embeddings.create(
        model="ADA", # model = "deployment_name".
        input=f"・取得したい資格：{qualificationName} \n ・試験日：あと{days_until_test}日 \n ・{currentSkill} \n  ・{targetSkill}\n 目標を達成するための計画を詳細に立ててください。"
    )
    print(embedding)
    """

      # Azure Open AIでタスク生成
    response = client.chat.completions.create(
        model="GPT4", # model = "deployment_name".
        max_tokens=4096,
        messages=[
            {"role": "system", "content": "You provide support in planning based on the user's goals."},
            {"role": "user", "content": f"・Desired Qualification: {qualificationName} \n ・Days until Exam: {days_until_test} days left \n ・{currentSkill} \n ・{targetSkill}\n Please create a plan to achieve these goals. Utilize the specified number of production days to the fullest, break down tasks into detail, and include specific study methods for each area of the exam. \nPlease respond in the following format: \n 〇 day-〇 :Task name - Detail 1. - Detail 2. ... \n Day 1-3: Learning Python Basics - Learn the basic concepts of Python syntax, data types, and control structures. - Set up the Python development environment."},
        ]
       
    )
    res = response.choices[0].message.content

    print(res)

    make_task_data = make_task_eng(res)

    if not make_task_data:
            res = formatting(res, "英語でテキスト生成してください")
            make_task_data = make_task_eng(res)
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
                cur.execute('INSERT INTO tasks (user_id, plan_id, days_range, task_name) VALUES (%s, %s, %s, %s)',
                            (user_id, plan_id, days_range, task_name))
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

#試験用のタイマーページ 
@app.route('/timer')
def timer():
    return render_template('timer_test.html')

def time_str_to_seconds(time_str):
    hours, minutes, seconds = map(int, time_str.split(':'))
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds

# タスク実行のデータを受け取る
@app.route('/save_data', methods=['POST'])
def save_data():
    try:
        # POSTリクエストからデータを受け取る
        data = request.get_json()

        # セッションからユーザーIDを取得（ユーザーがログインしていることが前提）
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'User not logged in'}), 401
        
        seconds = time_str_to_seconds(data['formattedTime'])

        current_time = datetime.now()
        new_time = current_time + timedelta(hours=9)

        # データベースに接続
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # タスク実行情報を挿入
        insert_query = """
        INSERT INTO task_executions (task_id, execution_date, execution_time, user_memo)
        VALUES (%s, %s, %s, %s)
        """
        task_id = 1  # タスクIDを適切に設定
        execution_date = new_time
        execution_time = seconds
        #task_progress = float(data['progressValue'])
        user_memo = data['user_memo']

        cursor.execute(insert_query, (task_id, execution_date, execution_time, user_memo))

        # データベースへの変更をコミット
        conn.commit()

        # タスクの進捗値を更新するSQL文
        update_query = """
        UPDATE tasks
        SET task_progress = %s
        WHERE id = %s
        """

        task_id = 1  # タスクIDを適切に設定
        new_task_progress = int(data['progressValue']) 

        cursor.execute(update_query, (new_task_progress, task_id))

        # データベースへの変更をコミット
        conn.commit()


        # レスポンスを返す（任意のレスポンスを設定することができます）
        response_data = {'message': 'データを受け取りました。'}
        return jsonify(response_data), 200

    except Exception as e:
        # エラーが発生した場合の処理
        conn.rollback()
        error_message = {'error': str(e)}
        return jsonify(error_message), 500

    finally:
        # データベース接続をクローズ
        cursor.close()
        conn.close()

###########################################################################################################################
# #旧ログイン機能
# @app.route("/")
# def welcome():
#     return render_template("welcome.html")

# @app.route("/login")
# def login_page():
#     return render_template("login.html")

# @app.route("/check_login", methods=['POST'])
# def check_login():
#     user, pw = (None, None)
#     if 'user' in request.form:
#         user = request.form['user']
#     if 'pw' in request.form:
#         pw = request.form['pw']
#     if (user is None) or (pw is None):
#         return redirect('/')
#     if try_login(user, pw) == False:
#         return """
#         <h1>Wrong username or password</h1>
#         <p><a href="/">→Return</a></p>
#         """
#     return redirect("/home")

# @app.route("/signup")
# def signup_page():
#     return render_template("signup.html")

# @app.route("/check_signup", methods=['POST'])
# def check_signup():
#     user, pw= (None, None)
#     if 'user' in request.form:
#         user = request.form['user']
#     if 'pw' in request.form:
#         pw = request.form['pw']
#     if (user is None) or (pw is None):
#         return redirect('/')
#     if user_checker(user) == False:
#         return """
#         <h1>Same username exists. Please use a different username.</h1>
#         <p><a href="/">→Reruen</a></p>
#         """
#     if try_signup(user, pw) == False:
#         return """
#         <h1>Invalid username, password, or email address</h1>
#         <p><a href="/login">→Return</a></p>
#         """
#     return redirect('/login')

# @app.route('/logout')
# def logout_page():
#     try_logout()
#     return """
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>ログアウト</title>
#         <style>
#             body {
#                 font-family: 'Arial', sans-serif;
#                 background-color: #f0f0f0;
#                 text-align: center;
#                 padding-top: 50px;
#             }

#             h1 {
#                 color: #333;
#                 font-size: 24px;
#             }

#             p {
#                 margin-top: 20px;
#                 font-size: 18px;
#             }

#             a {
#                 text-decoration: none;
#                 color: #007bff;
#                 font-weight: bold;
#             }

#             a:hover {
#                 color: #0056b3;
#                 text-decoration: underline;
#             }
#         </style>
#     </head>
#     <body>
#         <h1>Logged out</h1>
#         <p><a href="/login">→return</a></p>
#     </body>
#     </html>
#     """

# def is_login():
#     if 'user_id'  in session:
#         return True
#     return False

# def try_login(username, password):
#     conn = mysql.connector.connect(**config)
#     cur = conn.cursor()
#     cur.execute('SELECT id, password FROM account WHERE name = %s', (username,))
#     account = cur.fetchone()
#     cur.close()
#     conn.close()
#     if account and account[1] == password:
#         session['user_id'] = account[0]  # ユーザーIDをセッションに保存
#         return True
#     return False

# # セッションからユーザーIDを取得
# def get_user_id_from_session():
#     return session.get('user_id')

# def try_signup(username, password):
#     conn = mysql.connector.connect(**config)
#     cur = conn.cursor()
#     # ユーザー名が既に存在するかどうかをチェック
#     cur.execute('SELECT id FROM account WHERE name = %s', (username,))
#     if cur.fetchone():
#         cur.close()
#         conn.close()
#         return False  # 既に存在するユーザー名
#     # 新しいアカウントを作成
#     cur.execute('INSERT INTO account (name, password) VALUES (%s, %s)', (username, password))
#     user_id = cur.lastrowid  # 新しいユーザーIDを取得
#     conn.commit()
#     cur.close()
#     conn.close()
#     session['user_id'] = user_id  # ユーザーIDをセッションに保存
#     return True

# def try_logout():
#     session.pop('user_id', None)
#     return True

# def get_user():
#     if is_login():
#         return session['user_id']
#     return 'not login'

# def user_checker(user):
#     conn = mysql.connector.connect(**config)
#     cur = conn.cursor()
#     cur.execute('select * from account')
#     results = cur.fetchall()
#     cur.close()
#     conn.close()
#     for result in results:
#         if user in result:
#             return False
#     return True
        
###########################################################################################################################
#APIの接続確認
# @app.route('/test')
# def test():
#     response = client.chat.completions.create(
#     model="GPT35TURBO", # model = "deployment_name".
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
#         {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
#         {"role": "user", "content": "Do other Azure AI services support this too?"}
#     ]
#     )
#     res = response.choices[0].message.content
#     return res
###########################################################################################################################
#アカウント管理(要変更)
# @app.route("/admin")
# def admin():
#     return render_template("admin.html", accounts=get_account())

###########################################################################################################################
#タスク名をカレンダーに反映させる
# @app.route('/get_tasks')
# def get_tasks():
#     conn = mysql.connector.connect(**config)
#     cursor = conn.cursor()

#     try:
#         # ユーザーIDをセッションから取得
#         user_id = session.get('user_id')
#         if user_id is None:
#             return jsonify({"error": "User not logged in"}), 401

#         # learning_plansのIDを取得
#         cursor.execute("SELECT id FROM learning_plans WHERE user_id = %s", (user_id,))
#         plan_ids = cursor.fetchall()
#         if not plan_ids:
#             return jsonify([])  # 該当するlearning_plansがない場合

#         # 複数のplan_idsに対応するtasksを取得
#         plan_ids_tuple = tuple([id[0] for id in plan_ids])  # タプルに変換
#         query = "SELECT id, days_range, task_name FROM tasks WHERE plan_id IN %s"
#         cursor.execute(query, (plan_ids_tuple,))

#         tasks_data = cursor.fetchall()
#         tasks_list = []
#         for taskId, daysRange, taskName in tasks_data:
#             start_date, end_date = daysRange.split(' to ')
#             tasks_list.append({
#                 "id": taskId,
#                 "title": taskName,
#                 "start": start_date,
#                 "end": end_date,
#                 "allDay": True
#             })
#         print(tasks_list)
#         print(type(tasks_list))
#         return jsonify(tasks_list)
#     except Exception as e:
#         print(e)
#         return str(e)
#     finally:
#         cursor.close()
#         conn.close()

###########################################################################################################################

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)