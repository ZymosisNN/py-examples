"""
root_module description
"""
from some_funcs import func1, func2


class SomeClass:
    """Docstring for SomeClass"""

    def __init__(self, param1: str, param2: int) -> None:
        """
        :param param1:
        :param param2:
        :rtype: object
        """
        self.param1 = param1
        self.param2 = param2

    def get_param_str(self) -> str:
        result = f'param1: "{self.param1}", param2: {self.param2}'
        return result


def print_values() -> None:
    """Docstring for print_values"""
    obj = SomeClass(param1='string value', param2=123)
    print(obj.get_param_str())
    print(func1(123))
    print(func2('medved'))


if __name__ == '__main__':
    print_values()
