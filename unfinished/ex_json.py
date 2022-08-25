import json

# String --> JSON
s = '[{"field1": "value1", "field2": ["list_value1", "list_value1"], "field3": {"inner1": "in_value1", "inner2": "in_value2"}}, {"second": "something"}]'

print('String --> JSON')
print(s)
total = json.loads(s)

for j in total:
    for k, v in j.items():
        print(f'{k}: {v}')
    print('---')

print('-' * 100)

# Dict --> JSON
print('Dict --> JSON')
src_dict = {'a1': 111, 'a2': [1, 2], 'a3': {'b1': 222, 'b2': 'BBB'}}
d = json.dumps(src_dict)
print(d)
