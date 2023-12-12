import xlrd
import json
import pandas as pd


def find_key_in_json(data, target_string, parent_key=None):
    found_keys = []

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and target_string in value:
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


js = open('2021 年中国大学生程序设计竞赛桂林站 正式赛/team.json', 'r', encoding = 'utf=8')
co = js.read()
ct = json.loads(co)
js.close

df = pd.read_excel('2021 年中国大学生程序设计竞赛桂林站 正式赛/2021 年中国大学生程序设计竞赛桂林站 正式赛.xlsx', sheet_name = '正式队伍')
medalCol = len(df.columns.values)

with open('output.txt', 'w') as file:
    for i in range(1, len(df.index.values)):
        teamName = df.iloc[i, 3]
        medal = df.iloc[i, medalCol - 1]
        if medal == 'Honorable':
            break
        res = find_key_in_json(ct, teamName)
        output_line = f"{ct[res[0]]['organization']} {teamName} {ct[res[0]]['members'][0]} {ct[res[0]]['members'][1]} {ct[res[0]]['members'][2]} {medal}\n"
        file.write(output_line)
