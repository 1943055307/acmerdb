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

students_set = set()

st_list = []

with open('student.txt', 'w', encoding='utf-8', errors='ignore') as file:
    for folder_name in folder_names:
        if folder_name == '.idea':
            continue
        if folder_name == 'inspectionProfiles':
            continue

        ro = folder_name + "/team.json"
        js = open(ro, 'r', encoding='utf=8')
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
        # print(df.columns)
        df['Unnamed: 2'] = df['Unnamed: 2'].str.replace('(', '（').str.replace(')', '）')

        print(folder_name)

        medalCol = len(df.columns.values)
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
        # print(pos)
        for i in range(1, len(df.index.values)):
            teamName = df.iloc[i, 3]
            universityName = str(df.iloc[i, 2]).strip().replace(' ', '')
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
                for k in range(0, members_count):
                    student_info = f"{universityName} {ct[res[j]]['members'][k].strip().replace(' ', '')}\n"
                    if ct[res[j]]['members'][k] == '':
                        continue
                    if ct[res[j]]['members'][k] == ' ':
                        continue
                    if student_info in students_set:
                        continue
                    st_list.append({
                        'StudentName': ct[res[j]]['members'][k].strip().replace(' ', ''),
                        'UniversityName': universityName,
                    })
                    students_set.add(student_info)
                    file.write(student_info)

st_dict_with_id = {}
for i, team in enumerate(st_list, start=1):
    st_dict_with_id[str(i)] = team

output_file = 'student.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(st_dict_with_id, f, ensure_ascii=False, indent=4)