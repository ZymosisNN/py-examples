pairs = {
    '(': ')',
    '[': ']',
    '{': '}',
}


def my(text: str) -> bool:
    opened = []
    for s in text:
        if s in pairs.keys():
            opened.append(s)
            continue

        if s in pairs.values():
            try:
                last_open = opened.pop()
            except IndexError:
                print(f'    No opened brackets, Got: "{s}"')
                return False

            if pairs[last_open] != s:
                print(f'    Last open: "{last_open}", Exp: "{pairs[last_open]}", Got: "{s}"')
                return False

    if opened:
        print(f'    Open brackets remain: {opened}')

    return not opened


if __name__ == '__main__':
    from samples import SAMPLES

    for sample in SAMPLES:
        print(sample)
        print(my(sample))
        print()
