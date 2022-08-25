from typing import TypedDict


class My(TypedDict):
    var_int: int
    var_str: str


obj = My(var_int=1, var_str='aaa')
print(obj)
