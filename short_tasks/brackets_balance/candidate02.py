from collections import deque


def parentheses_check(str_to_check: str):
    parentheses = {'[': ']', '(': ')', '{': '}'}
    open_brackets = deque()
    for bracket in str_to_check:
        if bracket in parentheses:
            open_brackets.append(bracket)
        elif bracket in parentheses.values():
            try:
                if bracket != parentheses.get(open_brackets.pop()):
                    return False
            except IndexError:
                return False
    return not open_brackets


if __name__ == '__main__':
    from samples import SAMPLES
    # while True:
    #     try:
    #         print(parentheses_check(input()))
    #     except EOFError:  # Press Ctrl+D/Cmd+D or Ctrl+Z to finish input
    #         break

    for sample in SAMPLES:
        print(sample)
        print(parentheses_check(sample))
        print()
