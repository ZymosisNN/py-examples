from pprint import pprint

from jsonpath_ng.ext import parse
from jsonpath_ng import DatumInContext

data = {
    'string': 'preved medved',
    'color': 'red',
    'elements': [
        'element1',
        'element2',
        'element3',
    ],
    'map': {
        'one': 1,
        'two': 2,
        'three': 3,
        'numbers': [11, 22, 33]
    }
}

jp_str = '$..Numbers[1]'

expr = parse(jp_str)

pprint(data)
print('')

res: list[DatumInContext] = expr.find(data)

for i in res:
    print(i.value)
    print(i.context)
    print(i.path)
    print(i.full_path)
    print(i.id_pseudopath)
