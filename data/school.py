import os
import json

with open('team.json', 'r', encoding='utf-8') as file:
    team_data = json.load(file)

school_data = []

for team_id, team_info in team_data.items():
    # 检查是否为合法的团队信息
    if not isinstance(team_info, dict):
        continue

    university = team_info.get('UniversityName')
    pair = {"university": university, "gold": 0, "silver": 0, "bronze": 0}

    if pair not in school_data:
        school_data.append(pair)

school_dict_with_id = {}
for i, team in enumerate(school_data, start=1):
    school_dict_with_id[str(i)] = team

school_data = school_dict_with_id

with open('universityaward.json', 'r', encoding='utf-8') as file:
    award_data = json.load(file)

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

for award_id, award_info in award_data.items():
    university = award_info.get('UniversityName')
    award_level = award_info.get('Level')
    res = find_key_in_json(school_data, university)
    flag = 0
    if len(res) == 1:
        flag == 1
    if award_level == 'Gold':
        flag = 1
        school_data[res[0]]['gold'] += 1
    elif award_level == 'Silver':
        flag = 1
        school_data[res[0]]['silver'] += 1
    elif award_level == 'Bronze':
        flag = 1
        school_data[res[0]]['bronze'] += 1
    if flag == 0:
        print(university)

sorted_data = sorted(
    school_data.items(), 
    key=lambda x: (x[1]['gold'], x[1]['silver'], x[1]['bronze']), 
    reverse=True
)


school_dict_with_id = {}
for i, (_, team_data) in enumerate(sorted_data, start=1):
    school_dict_with_id[str(i)] = team_data

with open('school.json', 'w', encoding='utf-8') as file:
    json.dump(school_dict_with_id, file, indent=4, ensure_ascii=False)
