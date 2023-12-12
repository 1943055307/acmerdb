import json
import os

with open('teamComplete.json', 'r', encoding='utf-8') as to:
    to_data = json.load(to)

tp_list = []

with open('teamparticipation.txt', 'w', encoding='utf-8', errors='ignore') as file:
    for unit_id, unit_data in to_data.items():
        for i in range(0, unit_data['membersNumber']):
            output_line = f"{unit_data['members'][i]} {unit_data['teamName']} {unit_data['edition']} {unit_data['universityName']}\n"
            tp_list.append({
                'StudentName': unit_data['members'][i],
                'TeamName': unit_data['teamName'],
                'Edition': unit_data['edition'],
                'UniversityName': unit_data['universityName']
            })
            file.write(output_line)

tp_dict_with_id = {}
for i, team in enumerate(tp_list, start=1):
    tp_dict_with_id[str(i)] = team

output_file = 'teamparticipation.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(tp_dict_with_id, f, ensure_ascii=False, indent=4)