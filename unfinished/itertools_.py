from itertools import count, product


for i in product('AB', [1, 2]):
    print(i)

print('-' * 80)

for i in [(a, b) for a in 'AB' for b in [1, 2]]:
    print(i)
