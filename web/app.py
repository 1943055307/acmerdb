from flask import Flask, g, render_template, request, redirect, url_for, jsonify
# from flask_sqlalchemy import SQLAlchemy
import json
import psycopg2
from datetime import datetime

app = Flask(__name__)
app.template_folder = 'templates'
app.static_folder = 'static'

def get_db_connection():
    if 'db' not in g:
        g.db = psycopg2.connect(dbname="acmerdb", user="luo", password="Luotangwen19?", host="124.70.26.24", port=26000)
    return g.db

@app.before_request
def before_request():
    g.db = get_db_connection()

@app.after_request
def after_request(response):
    db = g.pop('db', None)
    if db is not None:
        db.close()
    return response

@app.route('/')
def index():
    return render_template('hello.html', css_file=url_for('static', filename='/css/styles.css'))

@app.route('/players')
def players():
    return render_template('hello.html', css_file=url_for('static', filename='/css/styles.css'))

@app.route('/matches')
def matches():
    return render_template('matches.html', css_file=url_for('static', filename='/css/styles.css'))

@app.route('/schools')
def schools():
    return render_template('schools.html', css_file=url_for('static', filename='/css/styles.css'))

@app.route('/teams')
def teams():
    return render_template('teams.html', css_file=url_for('static', filename='/css/styles.css'))

@app.route('/coaches')
def coaches():
    return render_template('coaches.html', css_file=url_for('static', filename='/css/styles.css'))

@app.route('/', methods=['POST'])
def process_input():
    if request.method == 'POST':
        input_text = request.form['input_text']
        client_ip = request.remote_addr
        # 将用户输入的文本和客户端IP写入文件
        with open('input.txt', 'a') as file:
            file.write(f"Input Text: {input_text}\n")
            file.write(f"Client IP: {client_ip}\n")
            file.write("\n")

        # 数据库查询（模糊匹配）
        output_text = []
        try:
            cursor = g.db.cursor()
            # 使用LIKE进行模糊匹配
            cursor.execute("SELECT * FROM student WHERE studentname LIKE %s", ("%" + input_text + "%",))
            rows = cursor.fetchall()
            for row in rows:
                output_text.append({'StudentName': row[1], 'UniversityName': row[0]})
            flag = 1 if rows else 2
        except Exception as e:
            print(f"An error occurred: {e}")
            flag = 2

        return render_template('hello.html', success=flag, input_text=output_text, css_file=url_for('static', filename='css/styles.css'))

    return render_template('hello.html')

# @app.route('/teams', methods=['POST'])
# def process_input_teams():
#     if request.method == 'POST':
#         input_text = request.form['input_text']
#         client_ip = request.remote_addr
#         # 将用户输入的文本和客户端IP写入文件
#         with open('input.txt', 'a') as file:
#             file.write(f"Input Text: {input_text}\n")
#             file.write(f"Client IP: {client_ip}\n")
#             file.write("\n")

#         # 数据库查询（模糊匹配）
#         output_text = []
#         try:
#             cursor = g.db.cursor()
#             # 使用LIKE进行模糊匹配
#             cursor.execute("SELECT distinct teamname, universityname FROM team WHERE universityname = %s", (input_text,))
#             rows = cursor.fetchall()
#             for row in rows:
#                 output_text.append({'StudentName': row[1], 'UniversityName': row[0]})
#             flag = 1 if rows else 2
#         except Exception as e:
#             print(f"An error occurred: {e}")
#             flag = 2

#         return render_template('teams_intermediate.html', result_text=input_text, success=flag, input_text=output_text, UniversityName=input_text, css_file=url_for('static', filename='css/styles.css'))

#     return render_template('teams_intermediate.html')

@app.route('/teams_intermediate', methods=['GET', 'POST'])
def process_input_teams():
    if request.method == 'POST':
    # print("hi")
    #     if request.method == 'POST':
        input_text = request.form['input_text']
        school_name = request.form['school_name']
        client_ip = request.remote_addr
        # 将用户输入的文本和客户端IP写入文件
        with open('input.txt', 'a') as file:
            file.write(f"Input Text: {input_text}\n")
            file.write(f"Client IP: {client_ip}\n")
            file.write("\n")

        # 数据库查询（模糊匹配）
        output_text = []
        try:
            cursor = g.db.cursor()
            # 使用LIKE进行模糊匹配
            cursor.execute("SELECT distinct teamname, universityname FROM team WHERE teamname LIKE %s and universityname=%s", ("%" + input_text + "%",school_name))
            rows = cursor.fetchall()
            for row in rows: 
                d = {"Gold": 0, "Silver": 0, "Bronze": 0}
                cursor.execute("select medal from universityaward where teamname = %s and universityname = %s", (row[0], row[1]))
                # print(row[1], row[0])
                tmp_rows = cursor.fetchall()
                for tmp_row in tmp_rows:
                    d[tmp_row[0]] += 1
                output_text.append({'StudentName': row[1], 'UniversityName': row[0], 'Gold': d['Gold'], 'Silver': d['Silver'], 'Bronze': d['Bronze']})
            output_text.sort(key=lambda k: (k['Gold'], k['Silver'], k['Bronze']), reverse=True)
            # output_text.sort(key=lambda k: k['Silver'], reverse=True)
            # output_text.sort(key=lambda k: k['Bronze'], reverse=True)
            flag = 1 if rows else 2
        except Exception as e:
            print(f"An error occurred: {e}")
            flag = 2

        return render_template('teams_intermediate.html', result_text=school_name, success=flag, UniversityName=school_name, input_text=output_text, css_file=url_for('static', filename='css/styles.css'))
    else:
        with open('static/data/resultofteam.txt', 'r') as file:
            text = file.read()
        parts = text.split(" from ", 1)  # 使用"from"进行分割，最多分割成两部分
        if len(parts) >= 2:
            before_from = parts[1]  # "from"前面的部分
        else:
            before_from = text  # 如果没有找到"from"，则整个文本都是前面的部分
        input_text = before_from.strip().replace(' ', '')
        # print(input_text)
        # 数据库查询（模糊匹配）
        output_text = []
        try:
            cursor = g.db.cursor()
            # 使用LIKE进行模糊匹配
            cursor.execute("SELECT distinct teamname, universityname FROM team WHERE universityname = %s", (input_text,))
            rows = cursor.fetchall()
            for row in rows: 
                d = {"Gold": 0, "Silver": 0, "Bronze": 0}
                cursor.execute("select medal from universityaward where teamname = %s and universityname = %s", (row[0], row[1]))
                # print(row[1], row[0])
                tmp_rows = cursor.fetchall()
                # print(tmp_rows[0][0])
                for tmp_row in tmp_rows:
                    d[tmp_row[0]] += 1
                output_text.append({'StudentName': row[1], 'UniversityName': row[0], 'Gold': d['Gold'], 'Silver': d['Silver'], 'Bronze': d['Bronze']})
            # print(len(output_text))
            output_text.sort(key=lambda k: (k['Gold'], k['Silver'], k['Bronze']), reverse=True)
            # output_text.sort(key=lambda k: k['Silver'], reverse=True)
            # output_text.sort(key=lambda k: k['Bronze'], reverse=True)
                # print(output_text)
            flag = 1 if rows else 2
        except Exception as e:
            print(f"An error occurred: {e}")
            flag = 2

        return render_template('teams_intermediate.html', result_text=input_text, success=flag, input_text=output_text, UniversityName=input_text, css_file=url_for('static', filename='css/styles.css'))

    # return render_template('teams_intermediate.html')


@app.route('/find', methods=['POST'])
def find():
    data = request.get_json()
    text = data['text']
    with open('static/data/result.txt', 'w') as file:
        file.write(text)
    return json.dumps({'success': True})


@app.route('/checkmatch', methods=['POST'])
def checkmatch():
    data = request.get_json()
    text = data['text']
    with open('static/data/resultofmatch.txt', 'w') as file:
        file.write(text)
    return json.dumps({'success': True})

@app.route('/checkschool', methods=['POST'])
def checkschool():
    data = request.get_json()
    text = data['text']
    with open('static/data/resultofschool.txt', 'w') as file:
        file.write(text)
    return json.dumps({'success': True})

@app.route('/write-name', methods=['POST'])
def write_team():
    data = request.json
    teammate_name = data['teammateName']
    # print(teammate_name)
    with open('static/data/result.txt', 'w') as file:
        file.write(teammate_name)
    return '', 200

@app.route('/write-team', methods=['POST'])
def write_name():
    data = request.json
    teammate_name = data['teamName']
    # print(teammate_name)
    with open('static/data/resultofteam.txt', 'w') as file:
        file.write(teammate_name)
    return '', 200

@app.route('/result')
def result():
    # print("hi")
    with open('static/data/result.txt', 'r') as file:
        text = file.read()
    parts = text.split(" from ", 1)  # 使用"from"进行分割，最多分割成两部分
    if len(parts) >= 2:
        before_from = parts[0]  # "from"前面的部分
        after_from = parts[1]  # "from"后面的部分
    else:
        before_from = text  # 如果没有找到"from"，则整个文本都是前面的部分
        after_from = ""  # 后面的部分为空字符串
    before_from = before_from.strip()
    after_from = after_from.strip()
    # print(before_from)
    # print(after_from)
    res = []
    team_participation = []
    try:
        cursor = g.db.cursor()
        cursor.execute("SELECT * FROM teamparticipation WHERE studentname = %s AND universityname = %s;", (before_from, after_from))
        rows = cursor.fetchall()
        for row in rows:
            team_participation.append({'TeamName': row[1], 'Edition': row[2], 'UniversityName': row[3]})
    except Exception as e:
        print(f"An error occurred: {e}")
    s_list = []
    try:
        cursor = g.db.cursor()
        cursor.execute("SELECT * FROM senior WHERE student = %s;", (before_from, ))
        rows = cursor.fetchall()
        for row in rows:
            s_list.append({'contest': row[0], 'award': row[1], 'student': row[2], 'grade': row[3], 'schoolname': row[4], 'score': row[5], 'province': row[6]})
    except Exception as e:
        print(f"An error occurred: {e}")
    s_number = len(s_list)
    inf = []
    ye = {}
    for participation in team_participation:
        teamname = participation['TeamName']
        edition = participation['Edition']
        universityname = participation['UniversityName']
        teammateNumber = 0
        awardsNumber = 0
        coach = 'NULL'
        teammate = []
        try:
            cursor = g.db.cursor()
            cursor.execute("SELECT studentname FROM teamparticipation WHERE teamname = %s AND edition = %s AND universityname = %s;", (teamname, edition, universityname))
            rows = cursor.fetchall()
            for row in rows:
                teammate.append({'TeammateName': row[0]})
            teammateNumber = len(teammate)
        except Exception as e:
            print(f"An error occurred: {e}")
        a_list = []
        try:
            cursor = g.db.cursor()
            cursor.execute("SELECT medal, acmname FROM universityaward WHERE teamname = %s AND edition = %s AND universityname = %s;", (teamname, edition, universityname))
            rows = cursor.fetchall()
            for row in rows:
                a_list.append({'ACMname': row[1], 'Medal': row[0]})
                inf.append({'Medal': row[0], 'ACMNAME': row[1]})
            awardsNumber = len(a_list)
        except Exception as e:
            print(f"An error occurred: {e}")
        try:
            cursor = g.db.cursor()
            cursor.execute("SELECT coachname FROM team WHERE teamname = %s AND edition = %s AND universityname = %s;", (teamname, edition, universityname))
            rows = cursor.fetchall()
            coach = rows[0][0]
        except Exception as e:
            print(f"An error occurred: {e}")
        res.append(
            {
                'TeamName': teamname,
                'Edition': edition,
                'TeammateNumber': teammateNumber,
                'Teammate': teammate,
                'coach': coach,
                'AwardsNumber': awardsNumber,
                'Awards': a_list
            }
        )
    with open('static/data/match.json', 'r', encoding='utf-8') as file:
        match_data = json.load(file)
    for inf_instance in inf:
        acmname = inf_instance['ACMNAME']
        medal = inf_instance['Medal']
        re = find_key_in_json(match_data, acmname)
        year = match_data[re[0]]['date'].split("-")[0]
        if year not in ye:
            ye[year] = {}
        if medal not in ye[year]:
            ye[year][medal] = 0
        ye[year][medal] += 1
    
    pres = []

    for year in ye:
        # print(f"Year: {year}")
        # for medal in ye[year]:
        #    print(f"  {medal}, Count: {ye[year][medal]}")
        if 'Gold' not in ye[year]:
            ye[year]['Gold'] = 0
        if 'Silver' not in ye[year]:
            ye[year]['Silver'] = 0
        if 'Bronze' not in ye[year]:
            ye[year]['Bronze'] = 0
        pres.append({'Year': year, 'Gold': ye[year]['Gold'], 'Silver': ye[year]['Silver'], 'Bronze': ye[year]['Bronze']})
    pres.sort(key=lambda x: x['Year'])
    return render_template('result.html', result_text = text, StudentName = before_from, UniversityName = after_from, Res = res, senior_res = s_list, s_number = s_number, pres = pres, css_file = url_for('static', filename='/css/styles.css'))

def find_key_in_json(data, target_string, parent_key=None):
    found_keys = []

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and value == target_string:
                if parent_key is not None:
                    found_keys.append(parent_key)
                else:
                    found_keys.append(key)
            elif isinstance(value, (dict, list)):
                result = find_key_in_json(value, target_string, parent_key=key)
                found_keys.extend(result)
    elif isinstance(data, list):
        for item in data:
            result = find_key_in_json(item, target_string, parent_key=parent_key)
            found_keys.extend(result)
    return found_keys

def medal_sort_priority(medal):
    if medal == 'Gold':
        return 1
    elif medal == 'Silver':
        return 2
    elif medal == 'Bronze':
        return 3
    return 4

@app.route('/write-match', methods=['POST'])
def write_match():
    data = request.json
    matchname = data['Name']
    # print(matchname)
    with open('static/data/resultofmatch.txt', 'w') as file:
        file.write(matchname)
    return '', 200

@app.route('/resultofmatch', methods=['GET', 'POST'])
def resultofmatch():
    if request.method == 'POST':
        input_text = request.form['input_text']
        # print(input_text)
        school_name = request.form['match_name']
        with open('static/data/match.json', 'r', encoding='utf-8') as file:
            match_data = json.load(file)
        text = school_name
        re = find_key_in_json(match_data, text)
        date = match_data[re[0]]['date']
        team = []
        res = []
        try:
            cursor = g.db.cursor()
            cursor.execute("SELECT medal, teamname, edition, universityname,rank  FROM universityaward WHERE acmname = %s and universityname LIKE %s;", (text,'%' + input_text+ '%'))
            rows = cursor.fetchall()
            for row in rows:
                team.append({'Medal': row[0], 'TeamName': row[1], 'Edition': row[2], 'UniversityName': row[3], 'rank': row[4]})
        except Exception as e:
            print(f"An error occurred: {e}")
        team.sort(key=lambda x: x['rank'])
        for team_instance in team:
            medal = team_instance['Medal']
            teamname = team_instance['TeamName']
            edition = team_instance['Edition']
            universityname = team_instance['UniversityName']
            rank = team_instance['rank']
            teammateNumber = 0
            coach = 'NULL'
            teammate = []
            try:
                cursor = g.db.cursor()
                cursor.execute("SELECT studentname FROM teamparticipation WHERE teamname = %s AND edition = %s AND universityname = %s;", (teamname, edition, universityname))
                rows = cursor.fetchall()
                for row in rows:
                    teammate.append({'TeammateName': row[0]})
                teammateNumber = len(teammate)
            except Exception as e:
                print(f"An error occurred: {e}")
            try:
                cursor = g.db.cursor()
                cursor.execute("SELECT coachname FROM team WHERE teamname = %s AND edition = %s AND universityname = %s;", (teamname, edition, universityname))
                rows = cursor.fetchall()
                coach = rows[0][0]
            except Exception as e:
                print(f"An error occurred: {e}")
            res.append(
                {
                    'Medal': medal,
                    'University': universityname,
                    'TeamName': teamname,
                    'Edition': edition,
                    'TeammateNumber': teammateNumber,
                    'Teammate': teammate,
                    'coach': coach,
                    'rank': rank
                }
            )
        
        # output_file = 'res.json'
        # with open(output_file, 'w', encoding='utf-8') as f:
        #     json.dump(res, f, ensure_ascii=False, indent=4)
        # print("1")
        return render_template('resultofmatch.html', date = date, result_text = text, Res = res, css_file = url_for('static', filename='/css/styles.css'))
    else:
        with open('static/data/resultofmatch.txt', 'r') as file:
            text = file.read().strip().replace(' ', '')
        # print(text)
        with open('static/data/match.json', 'r', encoding='utf-8') as file:
            match_data = json.load(file)
        re = find_key_in_json(match_data, text)
        date = match_data[re[0]]['date']
        team = []
        res = []
        try:
            cursor = g.db.cursor()
            cursor.execute("SELECT medal, teamname, edition, universityname, rank FROM universityaward WHERE acmname = %s;", (text,))
            rows = cursor.fetchall()
            for row in rows:
                team.append({'Medal': row[0], 'TeamName': row[1], 'Edition': row[2], 'UniversityName': row[3], 'rank': row[4]})
        except Exception as e:
            print(f"An error occurred: {e}")
        team.sort(key=lambda x: x['rank'])
        for team_instance in team:
            medal = team_instance['Medal']
            teamname = team_instance['TeamName']
            edition = team_instance['Edition']
            universityname = team_instance['UniversityName']
            rank = team_instance['rank']
            teammateNumber = 0
            coach = 'NULL'
            teammate = []
            try:
                cursor = g.db.cursor()
                cursor.execute("SELECT studentname FROM teamparticipation WHERE teamname = %s AND edition = %s AND universityname = %s;", (teamname, edition, universityname))
                rows = cursor.fetchall()
                for row in rows:
                    teammate.append({'TeammateName': row[0]})
                teammateNumber = len(teammate)
            except Exception as e:
                print(f"An error occurred: {e}")
            try:
                cursor = g.db.cursor()
                cursor.execute("SELECT coachname FROM team WHERE teamname = %s AND edition = %s AND universityname = %s;", (teamname, edition, universityname))
                rows = cursor.fetchall()
                coach = rows[0][0]
            except Exception as e:
                print(f"An error occurred: {e}")
            res.append(
                {
                    'Medal': medal,
                    'University': universityname,
                    'TeamName': teamname,
                    'Edition': edition,
                    'TeammateNumber': teammateNumber,
                    'Teammate': teammate,
                    'coach': coach,
                    'rank': rank
                    }
            )
        
        # output_file = 'res.json'
        # with open(output_file, 'w', encoding='utf-8') as f:
        #     json.dump(res, f, ensure_ascii=False, indent=4)
        # print("1")
        return render_template('resultofmatch.html', date = date, result_text = text, Res = res, css_file = url_for('static', filename='/css/styles.css'))

@app.route('/write-school', methods=['POST'])
def write_school():
    data = request.json
    schoolname = data['Name']
    # print(schoolname)
    with open('static/data/resultofschool.txt', 'w') as file:
        file.write(schoolname)
    return '', 200

@app.route('/resultofschool')
def resultofschool():
    with open('static/data/resultofschool.txt', 'r') as file:
        text = file.read().strip().replace(' ', '')
    # print(text)
    with open('static/data/match.json', 'r', encoding='utf-8') as file:
        match_data = json.load(file)
    with open('static/data/school.json', 'r', encoding='utf-8') as file:
        school_data = json.load(file)

    re = find_key_in_json(school_data, text)
    gold = school_data[re[0]]['gold']
    silver = school_data[re[0]]['silver']
    bronze = school_data[re[0]]['bronze']

    inf = []
    ye = {}
    mat = {}
    try:
        cursor = g.db.cursor()
        cursor.execute("SELECT medal, acmname FROM universityaward WHERE universityname = %s;", (text,))
        rows = cursor.fetchall()
        for row in rows:
            inf.append({'Medal': row[0], 'ACMNAME': row[1]})
    except Exception as e:
        print(f"An error occurred: {e}")
    
    for inf_instance in inf:
        acmname = inf_instance['ACMNAME']
        medal = inf_instance['Medal']
        if acmname not in mat:
            mat[acmname] = {}
        if medal not in mat[acmname]:
            mat[acmname][medal] = 0
        mat[acmname][medal] += 1    
        re = find_key_in_json(match_data, acmname)
        year = match_data[re[0]]['date'].split("-")[0]
        if year not in ye:
            ye[year] = {}
        if medal not in ye[year]:
            ye[year][medal] = 0
        ye[year][medal] += 1
    
    res = []
    matres = []

    for acmname in mat:
        if 'Gold' not in mat[acmname]:
            mat[acmname]['Gold'] = 0
        if 'Silver' not in mat[acmname]:
            mat[acmname]['Silver'] = 0
        if 'Bronze' not in mat[acmname]:
            mat[acmname]['Bronze'] = 0
        re = find_key_in_json(match_data, acmname)
        date = match_data[re[0]]['date']
        matres.append({'Date': date, 'ACMNAME': acmname, 'Gold':  mat[acmname]['Gold'], 'Silver': mat[acmname]['Silver'], 'Bronze': mat[acmname]['Bronze']})
    
    matnumber = len(matres)
    matres.sort( key=lambda item: datetime.strptime(item['Date'], '%Y-%m-%d'), reverse=True)
    # print(matres)
    for year in ye:
        # print(f"Year: {year}")
        # for medal in ye[year]:
        #    print(f"  {medal}, Count: {ye[year][medal]}")
        if 'Gold' not in ye[year]:
            ye[year]['Gold'] = 0
        if 'Silver' not in ye[year]:
            ye[year]['Silver'] = 0
        if 'Bronze' not in ye[year]:
            ye[year]['Bronze'] = 0
        res.append({'Year': year, 'Gold': ye[year]['Gold'], 'Silver': ye[year]['Silver'], 'Bronze': ye[year]['Bronze']})

    res.sort(key=lambda x: x['Year'])

    # print(res)
    return render_template('resultofschool.html', result_text = text, Res = res, matnumber = matnumber, Matres = matres, gold = gold, silver = silver, bronze = bronze, css_file = url_for('static', filename='/css/styles.css'))

@app.route('/api/coaches')
def get_coaches():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search_query', '', type=str)  # 获取搜索查询

    with open('static/data/coach.json', 'r', encoding='utf-8') as file:
        coach_data = json.load(file)

    # 只在存在非空搜索查询时过滤数据
    if search_query:
        coach_data = {k: v for k, v in coach_data.items() if search_query.lower() in v['coach'].lower()}

    total = len(coach_data)  # 更新总记录数

    # 实现分页逻辑
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = list(coach_data.values())[start:end]

    # 构建返回的JSON对象
    data_with_pagination = {
        "items": paginated_data,  # 当前页的数据
        "page": page,             # 当前页码
        "per_page": per_page,     # 每页显示的记录数
        "total": total,           # 总记录数
        "total_pages": total // per_page + (1 if total % per_page > 0 else 0)  # 总页数
    }

    return jsonify(data_with_pagination)


@app.route('/api/schools')
def get_schools():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search_query', '', type=str)  # 获取搜索查询
    
    with open('static/data/school.json', 'r', encoding='utf-8') as file:
        school_data = json.load(file)
    
    # 只在存在非空搜索查询时过滤数据
    if search_query:
        school_data = {k: v for k, v in school_data.items() if search_query.lower() in v['university'].lower()}

    total = len(school_data)  # 总记录数

    # 实现分页逻辑
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = list(school_data.values())[start:end]

    # 构建返回的JSON对象
    data_with_pagination = {
        "items": paginated_data,  # 当前页的数据
        "page": page,             # 当前页码
        "per_page": per_page,     # 每页显示的记录数
        "total": total,           # 总记录数
        "total_pages": total // per_page + (1 if total % per_page > 0 else 0)  # 总页数
    }

    return jsonify(data_with_pagination)

@app.route('/api/matches')
def get_matches():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search_query', '', type=str)  # 获取搜索查询

    with open('static/data/match.json', 'r', encoding='utf-8') as file:
        match_data = json.load(file)
    
    # 只在存在非空搜索查询时过滤数据
    if search_query:
        match_data = {k: v for k, v in match_data.items() if search_query.lower() in v['matchname'].lower()}
    total = len(match_data)  # 总记录数
    # print(match_data)
    # 实现分页逻辑
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = list(match_data.values())[start:end]

    # 构建返回的JSON对象
    data_with_pagination = {
        "items": paginated_data,  # 当前页的数据
        "page": page,             # 当前页码
        "per_page": per_page,     # 每页显示的记录数
        "total": total,           # 总记录数
        "total_pages": total // per_page + (1 if total % per_page > 0 else 0)  # 总页数
    }

    return jsonify(data_with_pagination)

@app.route('/findteams', methods=['POST'])
def findteams():
    data = request.get_json()
    text = data['text']
    with open('static/data/resultofteam.txt', 'w') as file:
        file.write(text)
    return json.dumps({'success': True})

@app.route('/resultofteams')
def resultofteams():
    # print("hi")
    with open('static/data/resultofteam.txt', 'r') as file:
        text = file.read()
    # print(text)
    parts = text.split(" from ", 1)  # 使用"from"进行分割，最多分割成两部分
    if len(parts) >= 2:
        before_from = parts[0]  # "from"前面的部分
        after_from = parts[1]  # "from"后面的部分
    else:
        before_from = text  # 如果没有找到"from"，则整个文本都是前面的部分
        after_from = ""  # 后面的部分为空字符串
    before_from = before_from.strip()
    after_from = after_from.strip()
    # print(before_from)
    # print(after_from)
    res = []
    team_participation = []
    try:
        cursor = g.db.cursor()
        cursor.execute("SELECT * FROM team WHERE teamname = %s AND universityname=%s;", (before_from, after_from))
        rows = cursor.fetchall()
        for row in rows:
            team_participation.append({'TeamName': row[0], 'Edition': row[1], 'UniversityName': row[2]})
    except Exception as e:
        print(f"An error occurred: {e}")
    # s_list = []
    # try:
    #     cursor = g.db.cursor()
    #     cursor.execute("SELECT * FROM senior WHERE student = %s;", (before_from, ))
    #     rows = cursor.fetchall()
    #     for row in rows:
    #         s_list.append({'contest': row[0], 'award': row[1], 'student': row[2], 'grade': row[3], 'schoolname': row[4], 'score': row[5], 'province': row[6]})
    # except Exception as e:
    #     print(f"An error occurred: {e}")
    # s_number = len(s_list)
    inf = []
    ye = {}
    for participation in team_participation:
        teamname = participation['TeamName']
        edition = participation['Edition']
        universityname = participation['UniversityName']
        teammateNumber = 0
        awardsNumber = 0
        coach = 'NULL'
        teammate = []
        try:
            cursor = g.db.cursor()
            cursor.execute("SELECT studentname FROM teamparticipation WHERE teamname = %s AND edition = %s AND universityname = %s;", (teamname, edition, universityname))
            rows = cursor.fetchall()
            for row in rows:
                teammate.append({'TeammateName': row[0], 'UniversityName': universityname})
            teammateNumber = len(teammate)
        except Exception as e:
            print(f"An error occurred: {e}")
        a_list = []
        try:
            cursor = g.db.cursor()
            cursor.execute("SELECT medal, acmname FROM universityaward WHERE teamname = %s AND edition = %s AND universityname = %s;", (teamname, edition, universityname))
            rows = cursor.fetchall()
            for row in rows:
                a_list.append({'ACMname': row[1], 'Medal': row[0]})
                inf.append({'Medal': row[0], 'ACMNAME': row[1]})
            awardsNumber = len(a_list)
        except Exception as e:
            print(f"An error occurred: {e}")
        try:
            cursor = g.db.cursor()
            cursor.execute("SELECT coachname FROM team WHERE teamname = %s AND edition = %s AND universityname = %s;", (teamname, edition, universityname))
            rows = cursor.fetchall()
            coach = rows[0][0]
        except Exception as e:
            print(f"An error occurred: {e}")
        res.append(
            {
                'TeamName': teamname,
                'Edition': edition,
                'TeammateNumber': teammateNumber,
                'Teammate': teammate,
                'coach': coach,
                'AwardsNumber': awardsNumber,
                'Awards': a_list
            }
        )
    with open('static/data/match.json', 'r', encoding='utf-8') as file:
        match_data = json.load(file)
    for inf_instance in inf:
        acmname = inf_instance['ACMNAME']
        medal = inf_instance['Medal']
        re = find_key_in_json(match_data, acmname)
        year = match_data[re[0]]['date'].split("-")[0]
        if year not in ye:
            ye[year] = {}
        if medal not in ye[year]:
            ye[year][medal] = 0
        ye[year][medal] += 1
    
    pres = []

    for year in ye:
        # print(f"Year: {year}")
        # for medal in ye[year]:
        #    print(f"  {medal}, Count: {ye[year][medal]}")
        if 'Gold' not in ye[year]:
            ye[year]['Gold'] = 0
        if 'Silver' not in ye[year]:
            ye[year]['Silver'] = 0
        if 'Bronze' not in ye[year]:
            ye[year]['Bronze'] = 0
        pres.append({'Year': year, 'Gold': ye[year]['Gold'], 'Silver': ye[year]['Silver'], 'Bronze': ye[year]['Bronze']})
    pres.sort(key=lambda x: x['Year'])
    return render_template('resultofteams.html', result_text = text, UniversityName = after_from, teamname = before_from, edition = after_from, Res = res, pres = pres, css_file = url_for('static', filename='/css/styles.css'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
