import random

print(f'random(): {random.random()}')
print(f'randint(1, 100): {random.randint(1, 100)}')
print(f'uniform(1, 100): {random.uniform(1, 100)}')


print(bool(random.getrandbits(1)))
