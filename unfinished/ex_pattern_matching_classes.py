from enum import Enum
from dataclasses import dataclass


class MouseButton(Enum):
    LEFT = 1
    RIGHT = 2
    MIDDLE = 3


@dataclass
class MouseClickEvent:
    position: tuple[int, int] = 0, 0
    button: MouseButton = MouseButton.LEFT

    @property
    def z(self):
        return 'ZZZ'

    def __str__(self):
        return f'MouseClick<{self.position}, {self.button.name}>'


def pm(event):
    match event:
        case MouseClickEvent(position=(3, 4), button=MouseButton.MIDDLE):
            return f'#1: x=3, y=4, exactly MIDDLE button'

        case MouseClickEvent(position=(3, 4), button=btn):
            return f'#2: x=3, y=4, any button = {btn}'

        case MouseClickEvent(position=pos, button=btn, z=z):
            return f'#3: default {pos} and {btn} (z={z})'

        case str():
            return f'#4: String "{event}"'

        case {'key': v}:
            return f'DICT: = {v}'

        case default:
            return f'Unmatched: {default}'


if __name__ == '__main__':
    test_cases = (
        MouseClickEvent(),
        MouseClickEvent(position=(1, 2)),
        MouseClickEvent(button=MouseButton.MIDDLE),
        MouseClickEvent(position=(3, 4), button=MouseButton.RIGHT),
        MouseClickEvent(position=(3, 4), button=MouseButton.MIDDLE),
        'Just a string',
        123,
        {'key': 'value'},
    )
    for value in test_cases:
        print(f'{str(value): <30s} : {pm(value)}')

    a = []
