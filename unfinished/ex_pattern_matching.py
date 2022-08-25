def pm(obj):
    match obj:
        case 'A' | 'B':
            return 'Big A or B'

        case 42:
            return 'This is "42"'

        case []:
            return f'Empty sequence'

        case first, 'OLOLO':
            return f'Sequence with 2 elements, the first is "{first}", the second is exactly "OLOLO"'

        case [a, b, c]:
            return f'List: {[a, b, c]}'

        case (a, b, c):  # never happens because of the list clause right above
            return f'Tuple: {a, b, c}'

        case [x, *_, y]:
            return f'Sequence starting with "{x}", ending with "{y}" and some shit inside'

        case default:
            return f'Default clause: {default}'


def cmd_split(cmd, allowed=()):
    match cmd.split():
        case ['get', x] | ['take', x] | ['pick', x] | ['pick', x, 'up'] | ['pick', 'up', x]:
            return f'Taking {x}'

        case ['go', ('north' | 'south' | 'east' | 'west') as direction]:  # exactly parentheses inside
            return f'New direction is {direction}'

        case ['use', item] if item in allowed:
            return f'Using {item}'

        case _:
            return '- not matched -'


if __name__ == '__main__':
    print('General:')
    test_cases = (
        0,
        42,
        '42',
        'preved',
        (),
        ['A', 'b', 'c', 'd'],
        ['some', 'OLOLO'],
        'A',
        'B',
        (1, 2, 3),
        [4, 5, 6],
    )
    for value in test_cases:
        print(f'{str(value): >30s} : {pm(value)}')

    print('Split sequences:')
    word = 'SHIT'
    test_cases = (
        f'get {word}',
        f'take    {word}',
        f' pick    {word}  ',
        f'pick    {word}   up',
        f'pick  up    {word}',
        'go   south',
    )
    for value in test_cases:
        print(f'{str(value): >30s} : {cmd_split(value)}')

    test_allowed = 'food', 'water'
    value = 'use food'
    print(f'{str(value): >30s} : {cmd_split(value)}')
    print(f'{str(value): >30s} : {cmd_split(value, test_allowed)}')
    value = 'use beer'
    print(f'{str(value): >30s} : {cmd_split(value, test_allowed)}')
