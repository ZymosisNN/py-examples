class SimpleObj:
    def __init__(self):
        self.n = 'VALUE'


class StrObj(SimpleObj):
    def __str__(self):
        return f'StrObj.__str__ {self.n}'


class ReprObj(StrObj):
    def __repr__(self):
        return f'ReprObj.__repr__ {self.n}'


print(SimpleObj())
print(str(SimpleObj()))
print(repr(SimpleObj()))

print(StrObj())
print(str(StrObj()))
print(repr(StrObj()))

print(ReprObj())
print(str(ReprObj()))
print(repr(ReprObj()))

print('Format s  :{}'.format(StrObj()))
print('Format !r :{!r}'.format(StrObj()))

print('Format s  :{}'.format(ReprObj()))
print('Format !r :{!r}'.format(ReprObj()))

print('-' * 50)


p = 'PASSED'
strings = {
    'Check current DC': p,
    'Check domains deployment': p,
    'Check delays': p,
    'Check domains distribution over freedom farms': p,
    'Check domains <-> DHs': p,
    'Check number of domains': p,
    'Check MGR Status': p,
    'Check domains distribution over DHs': p,
}

size = max([len(name) for name in strings.keys()]) + 1
print(size)

for name, result in strings.items():
    print('|{: >{size}s} - {}'.format(name, result, size=size))
