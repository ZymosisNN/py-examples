from itertools import product


for i in product('ABC', [1, 2]):
    print(i)

print('-' * 80)

for i in [(a, b) for a in 'ABC' for b in [1, 2]]:
    print(i)
