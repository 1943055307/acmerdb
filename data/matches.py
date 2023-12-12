import os
import json
from datetime import datetime

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

match_data = []

for folder_name in folder_names:
    if folder_name == '.idea':
        continue
    if folder_name == 'inspectionProfiles':
        continue
    
    ma = {"matchname": folder_name}

    match_data.append(ma)

    print(folder_name)



with open('match.json', 'w', encoding='utf-8') as file:
    json.dump(match_data, file, indent=4, ensure_ascii=False)

# 读取 TXT 文件并提取日期信息
def read_dates_from_txt(txt_file_path):
    dates_dict = {}
    with open(txt_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) == 2:
                match_name, date = parts
                dates_dict[match_name] = date
    return dates_dict

# 读取并更新 JSON 文件
def update_json_with_dates(json_file_path, dates_dict):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 更新数据
    for value in data:
        match_name = value.get('matchname')
        if match_name in dates_dict:
            value['date'] = dates_dict[match_name]
        value['matchname'] = match_name.strip().replace(' ', '')

    # 根据日期排序
    sorted_data = sorted(data, key=lambda item: datetime.strptime(item['date'], '%Y-%m-%d'), reverse=True)

    # 创建带有 ID 的字典
    match_dict_with_id = {str(i): item for i, item in enumerate(sorted_data, start=1)}

    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(match_dict_with_id, file, indent=4, ensure_ascii=False)

# 指定文件路径
txt_file_path = r"E:\Tencent Files\1356620905\FileRecv\data\match.txt"
json_file_path = 'match.json'

# 读取 TXT 文件
dates_dict = read_dates_from_txt(txt_file_path)

# 更新 JSON 文件
update_json_with_dates(json_file_path, dates_dict)