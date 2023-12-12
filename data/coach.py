import os
import json
import pandas as pd
import pinyin

def traverse_folder(folder_path):
    folder_names = []
    for root, dirs, files in os.walk(folder_path):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            folder_name = os.path.basename(dir_path)
            folder_names.append(folder_name)

    return folder_names

folder_path = r'E:\Tencent Files\1356620905\FileRecv\data'
folder_names = traverse_folder(folder_path)

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

# 打开并读取teamComplete.json
with open('teamComplete.json', 'r', encoding='utf-8') as file:
    team_data = json.load(file)

coach_data = []

for team_id, team_info in team_data.items():
    # 检查是否为合法的团队信息
    if not isinstance(team_info, dict):
        continue

    coach = team_info.get('coach').strip().replace(' ', '')

    if coach == 'NULL':
        continue

    university = team_info.get('universityName')
    pair = {"coach": coach, "university": university, "gold": 0, "silver": 0, "bronze": 0}

    if pair not in coach_data:
        coach_data.append(pair)

# 根据coach的拼音排序coach_data
coach_data_sorted = sorted(coach_data, key=lambda x: pinyin.get(x['coach'], format="strip"))

coach_dict_with_id = {}
for i, team in enumerate(coach_data_sorted, start=1):
    coach_dict_with_id[str(i)] = team

coach_data = coach_dict_with_id

for folder_name in folder_names:
    if folder_name == '.idea':
        continue
    if folder_name == 'inspectionProfiles':
        continue

    ro = folder_name + "/team.json"
    js = open(ro, 'r', encoding='utf-8')
    co = js.read()
    ct = json.loads(co)
    js.close()

    ex = folder_name + '/' + folder_name + '.xlsx'
    xf = pd.ExcelFile(ex)
    sheet_names = xf.sheet_names
    if "正式队伍" in sheet_names:
        df = pd.read_excel(ex, sheet_name='正式队伍')
    else:
        df = pd.read_excel(ex, sheet_name='所有队伍')
    if "正式队伍" in sheet_names:
        header = pd.read_excel(ex, sheet_name='正式队伍', header=1, nrows=0)
    else:
        header = pd.read_excel(ex, sheet_name='所有队伍', header=1, nrows=0)
    # header = pd.read_excel(ex, header=1, nrows=0)
    # print(header)
    # for x in header:
        # print(x)
    pos = -1
    for i, x in enumerate(header):
        if x == 'Medal':
            pos = i
    # print(df.columns)
    df['Unnamed: 2'] = df['Unnamed: 2'].str.replace('(', '（').str.replace(')', '）')
    print(folder_name)

    medalCol = len(df.columns.values)

    for i in range(1, len(df.index.values)):
        teamName = df.iloc[i, 3]
        universityName = df.iloc[i, 2].strip().replace(' ', '')
        medal = df.iloc[i, pos]
        if medal == 'Honorable':
            break
        res = find_key_in_json(ct, teamName)
        for j in range(0, len(res)):
            if ct[res[j]]['organization'].strip().replace(' ', '') != universityName:
                continue

            if "coach" in ct[res[j]]:
                coach_info = ct[res[j]]['coach'].strip().replace(' ', '')
                re = find_key_in_json(coach_data, coach_info)
                flag = 0
                for k in range(0, len(re)):
                    if coach_data[re[k]]['university'].strip().replace(' ', '') != universityName:
                        continue
                    if medal == 'Gold':
                        flag = 1
                        coach_data[re[k]]['gold'] += 1
                    elif medal == 'Silver':
                        flag = 1
                        coach_data[re[k]]['silver'] += 1
                    elif medal == 'Bronze':
                        flag = 1
                        coach_data[re[k]]['bronze'] += 1
                if flag == 0:
                    print(coach_info)
            else:
                continue


# 创建并写入coach.json文件
with open('coach.json', 'w', encoding='utf-8') as file:
    json.dump(coach_data, file, indent=4, ensure_ascii=False)