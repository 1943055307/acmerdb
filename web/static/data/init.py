import psycopg2
import os
import csv

# 数据库连接参数
host = "localhost"
dbname = "acmerdb"
user = "postgres"
password = "Wys_20031028"
port = "your_port"

# 建立数据库连接
conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password)
cursor = conn.cursor()

# 删除所有现有表
# cursor.execute("""
#     SELECT table_schema, table_name
#     FROM information_schema.tables
#     WHERE table_schema = 'public'
# """)
# tables = cursor.fetchall()
# for table in tables:
#     print(f"Deleting {table[1]}")
#     cursor.execute(f"DROP TABLE IF EXISTS {table[1]} CASCADE")
cursor.execute(
    """
    delete from student
    """
)
cursor.execute(
    """
    delete from team
    """
)
cursor.execute(
    """
    delete from teamparticipation
    """
)
cursor.execute(
    """
    delete from universityaward
    """
)

# 创建表格
create_statements = [
    """
    CREATE TABLE student (
        universityname VARCHAR(100),
        studentname VARCHAR(100),
        PRIMARY KEY (universityname, studentname)
    );
    """,
    """
    CREATE TABLE team (
        teamname VARCHAR(400),
        edition INTEGER,
        universityname VARCHAR(100),
        coachname VARCHAR(100),
        PRIMARY KEY (teamname, edition, universityname)
    );
    """,
    """
    CREATE TABLE teamparticipation (
        studentname VARCHAR(100),
        teamname VARCHAR(400),
        edition INTEGER,
        universityname VARCHAR(100),
        PRIMARY KEY (studentname, teamname, edition, universityname)
    );
    """,
    """
    CREATE TABLE universityaward (
        medal VARCHAR(10),
        acmname VARCHAR(100),
        teamname VARCHAR(400),
        edition INTEGER,
        universityname VARCHAR(100),
        PRIMARY KEY (acmname, teamname, edition, universityname)
    );
    """,
    """
    CREATE TABLE senior (
        contest VARCHAR(100),
        award VARCHAR(100),
        student VARCHAR(100),
        grade VARCHAR(100),
        schoolname VARCHAR(100),
        score VARCHAR(100),
        province VARCHAR(100),
        PRIMARY KEY (contest, student, grade, schoolname, score)
    );
    """,
]

# for statement in create_statements:
    # cursor.execute(statement)

# 当前文件的路径
current_path = os.path.dirname(__file__)

# 导入数据的函数
def import_data(file_name, table_name):
    file_path = os.path.join(current_path, 'static', file_name)
    with open(file_path, 'r', encoding='UTF-8', errors='ignore') as file:
        for line in file:
            values = line.strip().split(' ')
            insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['%s'] * len(values))})"
            cursor.execute(insert_query, values)

# 导入每个表的数据
import_data('data/student.txt', 'student')
import_data('data/team.txt', 'team')
import_data('data/teamparticipation.txt', 'teamparticipation')
import_data('data/universityaward.txt', 'universityaward')

# file_path = os.path.join(current_path, 'static', 'data/senior.txt')
# seen_rows = set()  # 用来存储已经见过的行
# with open(file_path, 'r', encoding='utf-8') as file:
#     reader = csv.reader(file)
#     for row in reader:
#         # 创建一个元组，包含行中的所有数据
#         row_tuple = tuple(row)

#         # 检查这一行是否已经处理过
#         if row_tuple in seen_rows:
#             continue  # 如果已经处理过，跳过这一行

#         # 将这一行添加到已见行集合中
#         seen_rows.add(row_tuple)

#         # 插入数据到数据库
#         cursor.execute("INSERT INTO senior (contest, award, student, grade, schoolname, score, province) VALUES (%s, %s, %s, %s, %s, %s, %s)",
#                        (row[0], row[1], row[2], row[3], row[4], row[5], row[6]))


# 提交更改并关闭连接
conn.commit()
cursor.close()
conn.close()
