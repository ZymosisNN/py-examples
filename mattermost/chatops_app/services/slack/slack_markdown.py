"""
Slack format:
    Hyperlink: <https://some.url|"How it's shown in message">
    Bold: *bold text*
    Italic: _italic text_
    Strike: ~strike text~
    Mono: `mono text`
    Code block: ```code block text```
    Quote: >quoted text
"""
from typing import Any


class MD:
    def __init__(self, msg: Any = ''):
        self._msg = [str(msg)] if msg else []

    def __str__(self):
        return ''.join(self._msg)

    def __call__(self, msg: Any):
        self._msg.append(str(msg))
        return self

    @property
    def msg_list(self):
        return self._msg

    def __add__(self, other: Any):
        if isinstance(other, MD):
            self._msg.extend(other.msg_list)
        else:
            print(f'before: {self}')
            self(other)
            print(f'after : {self}')
        return self

    def key_value(self, key, value):
        self(key)(': ').b(value)
        return self

    def br(self):
        self._msg.append('\n')
        return self

    def ok(self):
        self._msg.append(':white_check_mark: ')
        return self

    def nok(self):
        self._msg.append(':x: ')
        return self

    def b(self, msg: Any):
        self._msg.append(f'*{msg}*')
        return self

    def i(self, msg: Any):
        self._msg.append(f'_{msg}_')
        return self

    def strike(self, msg: Any):
        self._msg.append(f'~{msg}~')
        return self

    def mono(self, msg: Any):
        self._msg.append(f'`{msg}`')
        return self

    def code(self, msg: Any):
        self._msg.append(f'```{msg}```')
        return self

    def quote(self, msg: Any):
        self._msg.append(f'>{msg}')
        return self

    def link(self, url: str, label: str):
        self._msg.append(f'<{url}|{label}>')
        return self


def ok(msg: Any) -> MD:
    return MD().ok()(msg)


def nok(msg: Any) -> MD:
    return MD().nok()(msg)


def b(msg: Any) -> MD:
    return MD().b(msg)


def i(msg: Any) -> MD:
    return MD().i(msg)


def strike(msg: Any) -> MD:
    return MD().strike(msg)


def mono(msg: Any) -> MD:
    return MD().mono(msg)


def code(msg: Any) -> MD:
    return MD().code(msg)


def quote(msg: Any) -> MD:
    return MD().quote(msg)


def link(url: str, label: str) -> MD:
    return MD().link(url, label)


if __name__ == '__main__':
    print(ok('OK')('preved').ok()('medved').br().b('jopa'))
    print(nok('NOK')('preved').ok()('medved').br().b('jopa'))
    print(ok('preved') + nok('medved'), '\n')

    test_msg = MD()
    for k, v in {'one': 111, 'two': 222, 'three': 333}.items():
        test_msg.key_value(k, v)
    print(test_msg)
