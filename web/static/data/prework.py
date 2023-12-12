import json
import os

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


for folder_name in folder_names:
    if folder_name == '.idea':
        continue
    if folder_name == 'inspectionProfiles':
        continue

    ro = folder_name + "/team.json"

    print(folder_name)

    # 读取JSON文件
    with open(ro, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 遍历数据中的每个元素
    for key, item in data.items():
        # 检查'members'键是否存在，并且其值是一个列表
        if 'members' in item and isinstance(item['members'], list) and len(item['members']) > 0:
            if '、' in item['members'][0]:
                # 如果有顿号，按顿号拆分
                members = item['members'][0].split('、')
                item['members'] = members
        if 'organization' in item:
            organization = item['organization'].replace('(', '（').replace(')', '）')
            item['organization'] = organization
            

    with open(ro, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


