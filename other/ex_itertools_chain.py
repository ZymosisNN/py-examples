from itertools import chain

# Flatten list of lists
a = ['a', 'b', 'c']
b = [1, 2, 3, 4]
print(list(chain(a, b)))

c = [a, b]
print(list(chain(*c)))
