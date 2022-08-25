d = {
    'one': 5,
    'two': 0,
    'three': 1,
    'four': 10,
    'five': 5,
    'six': 3,
    'six2': 5
}


for i in [i for v in sorted(list(set(d.values()))) for i in d.items() if i[1] == v]:
    print(i)
print("#"*10)
[print(i) for v in sorted(list(set(d.values()))) for i in d.items() if i[1] == v]
print("#"*10)


def print_func(x):
    print(x)
    return x


print([print_func(i) for v in sorted(list(set(d.values()))) for i in d.items() if i[1] == v])

print(sorted(d, key=lambda item: d[item]))

