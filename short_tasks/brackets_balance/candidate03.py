from typing import List

OPEN_PARENS = {"(", "[", "{"}
MATCH_PARENS = {")": "(", "]": "[", "}": "{"}


def check_parentheses(string: str) -> bool:
    stack: List[str] = []
    for char in string:
        if char in OPEN_PARENS:
            stack.append(char)
        elif char in MATCH_PARENS:
            if not stack:
                return False
            match = MATCH_PARENS[char]
            if match != stack.pop():
                return False
    if stack:
        return False
    return True


if __name__ == '__main__':
    from samples import SAMPLES

    for sample in SAMPLES:
        print(sample)
        print(check_parentheses(sample))
        print()
