from prettytable import from_json, PrettyTable
import json

data = [
    {'Account ID': 1461, 'Result': 'Sync resource changed'},
    {'Account ID': 1466, 'Result': 'vccContactSync=False, skipped'},
    {'Account ID': 1467, 'Result': 'Sync resource changed'},
    {'Account ID': 1473, 'Result': 'Sync resource changed'},
    {'Account ID': 1474, 'Result': 'Sync resource changed'}
]

data = data[:1] + data
j = json.dumps(data)
table = from_json(j, title='Preved medved')
print(table)
