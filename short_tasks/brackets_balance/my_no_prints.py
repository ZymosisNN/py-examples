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

        elif s in pairs.values():
            try:
                last_open = opened.pop()
            except IndexError:
                return False

            if pairs[last_open] != s:
                return False

    return not opened


if __name__ == '__main__':
    from samples import SAMPLES

    for sample in SAMPLES:
        print(sample)
        print(my(sample))
        print()
