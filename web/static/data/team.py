import os
import json
import pandas as pd

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

team_list = []
team_set = set()

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
            if "members" not in ct[res[j]]:
                continue
            members_count = len(ct[res[j]].get('members', []))
            if members_count == 0:
                break

            members_real = {}
            members_count_real = 0
            for member in ct[res[j]]['members']:
                if member.strip():  # Check if the member string is not empty after stripping whitespace
                    members_real[member.strip().replace(' ', '')] = member.strip().replace(' ', '')  # Use the member string as the key and the value
                    members_count_real += 1

            members_sorted = sorted(members_real)

            if "coach" in ct[res[j]]:
                coach_info = ct[res[j]]['coach']
            else:
                coach_info = 'NULL'
            team_info = (
                teamName.strip().replace(' ', ''),
                universityName,
                members_count_real,
                tuple(members_sorted),
                coach_info.strip().replace(' ', '')
            )
            if team_info in team_set:
                continue
            team_set.add(team_info)
            team_list.append({
                'teamName': teamName.strip().replace(' ', ''),
                'universityName': universityName,
                'membersNumber': members_count_real,
                'members': members_sorted,
                'coach': coach_info.strip().replace(' ', '')
            })

team_dict_with_id = {}
for i, team in enumerate(team_list, start=1):
    team_dict_with_id[str(i)] = team

output_file = 'teamOrigin.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(team_dict_with_id, f, ensure_ascii=False, indent=4)

with open('teamOrigin.json', 'r', encoding='utf-8') as to:
    to_data = json.load(to)
    
times = {}
vis = {}

te_list = []
t_list = []

with open('team.txt', 'w', encoding='utf-8', errors='ignore') as file:
    for team in team_list:
        team_name = team['teamName']
        res = find_key_in_json(to_data, team_name)
        for i in range(0, len(res)):
            index = res[i]
            universityName = to_data[index]['universityName']
            if universityName != team['universityName']:
                continue
            if universityName not in vis:
                vis[universityName] = {}
            if team_name not in vis[universityName]:
                vis[universityName][team_name] = {}
            if i not in vis[universityName][team_name]:
                vis[universityName][team_name][i] = 0
            if vis[universityName][team_name][i] == 1:
                continue
            vis[universityName][team_name][i] = 1
            if universityName not in times:
                times[universityName] = {}
            if team_name not in times[universityName]:
                times[universityName][team_name] = 0
            times[universityName][team_name] += 1
            t = times[universityName][team_name]
            output_line = f"{team_name} {t} {universityName} {to_data[index]['coach']}\n"
            file.write(output_line)
            members_sorted = to_data[index]['members']
            members_count = len(members_sorted)
            te_list.append({
                'teamName': team_name,
                'universityName': universityName,
                'edition': t,
                'membersNumber': members_count,
                'members': members_sorted,
                'coach': to_data[index]['coach'].strip().replace(' ', '')
            })
            t_list.append({
                'TeamName': team_name,
                'Edition': t,
                'UniversityName': universityName,
                'CoachName': to_data[index]['coach'].strip().replace(' ', '')
            })
            break

te_dict_with_id = {}
for i, team in enumerate(te_list, start=1):
    te_dict_with_id[str(i)] = team

output_file = 'teamComplete.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(te_dict_with_id, f, ensure_ascii=False, indent=4)

t_dict_with_id = {}
for i, team in enumerate(t_list, start=1):
    t_dict_with_id[str(i)] = team

output_file = 'team.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(t_dict_with_id, f, ensure_ascii=False, indent=4)