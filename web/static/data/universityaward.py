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

ua_list = []

with open('teamComplete.json', 'r', encoding='utf-8') as to:
    to_data = json.load(to)

with open('universityaward.txt', 'w', encoding='utf-8', errors='ignore') as file:
    for folder_name in folder_names:
        if folder_name == '.idea':
            continue
        if folder_name == 'inspectionProfiles':
            continue

        ro = folder_name + "/team.json"
        js = open(ro, 'r', encoding = 'utf=8')
        co = js.read()
        ct = json.loads(co)
        js.close

        ex = folder_name + '/' + folder_name + '.xlsx'
        xf = pd.ExcelFile(ex)
        sheet_names = xf.sheet_names
        if "正式队伍" in sheet_names:
            df = pd.read_excel(ex, sheet_name = '正式队伍')
        else:
            df = pd.read_excel(ex, sheet_name = '所有队伍')
        # print(df.columns)
        df['Unnamed: 2'] = df['Unnamed: 2'].str.replace('(', '（').str.replace(')', '）')
        print(folder_name)
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

        medalCol = len(df.columns.values)

        for i in range(1, len(df.index.values)):
            teamName = df.iloc[i, 3]
            universityName = df.iloc[i, 2].strip().replace(' ', '')
            medal = df.iloc[i, pos]
            if medal == 'Honorable':
                break
            res = find_key_in_json(ct, teamName)
            resComplete = find_key_in_json(to_data, teamName.strip().replace(' ', ''))
            for j in range(0, len(res)):
                if ct[res[j]]['organization'] != universityName:
                    continue
                if "members" not in ct[res[j]]:
                    continue

                members_count = len(ct[res[j]]['members'])
                if members_count == 0:
                    continue
                awardStr = teamName.strip().replace(' ', '') + universityName

                members_real = {}
                members_count_real = 0
                for member in ct[res[j]]['members']:
                    if member.strip():  # Check if the member string is not empty after stripping whitespace
                        members_real[member.strip().replace(' ', '')] = member.strip().replace(' ', '')  # Use the member string as the key and the value
                        members_count_real += 1

                members_sorted = sorted(set(members_real.values()))
                members_count_real = len(members_sorted)

                if members_count_real == 1:
                    awardStr = awardStr + members_sorted[0]
                elif members_count_real == 2:
                    awardStr = awardStr + members_sorted[0] + members_sorted[1]
                elif members_count_real == 3:
                    awardStr = awardStr + members_sorted[0] + members_sorted[1] + members_sorted[2]
                if "coach" in ct[res[j]]:
                    awardStr = awardStr + ct[res[j]]['coach'].strip().replace(' ', '')
                else:
                    awardStr = awardStr + 'NULL'
                flag = 0
                for k in range(0, len(resComplete)):
                    cStr = teamName.strip().replace(' ', '') + to_data[resComplete[k]]['universityName']
                    for n in range(0, to_data[resComplete[k]]['membersNumber']):
                        cStr = cStr + to_data[resComplete[k]]['members'][n]
                    cStr = cStr + to_data[resComplete[k]]['coach'].strip().replace(' ', '')
                    if awardStr == cStr:
                        flag = 1
                        output_line = f"{medal} {folder_name.strip().replace(' ', '')} {teamName.strip().replace(' ', '')} {to_data[resComplete[k]]['edition']} {universityName}\n"
                        ua_list.append(
                            {
                                'Level': medal,
                                'ACMname': folder_name.strip().replace(' ', ''),
                                'TeamName': teamName.strip().replace(' ', ''),
                                'Edition': to_data[resComplete[k]]['edition'],
                                'UniversityName': universityName
                            }
                        )
                        file.write(output_line)
                        break
                
                if flag == 0:
                    print(awardStr)

ua_dict_with_id = {}
for i, team in enumerate(ua_list, start=1):
    ua_dict_with_id[str(i)] = team

output_file = 'universityaward.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(ua_dict_with_id, f, ensure_ascii=False, indent=4)