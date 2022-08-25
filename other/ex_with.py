class WithObj(object):
    def __init__(self, name):
        self.name = name
        print(f'{name}: init')

    def __enter__(self):
        print(f'{self.name}: enter')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f'{self.name}: exit, exc_type={exc_type}, exc_val={exc_val}, exc_tb={exc_tb}')
        return False  # True means exceptions are handled inside this method


with WithObj('A') as a, WithObj('B') as b:
    print(f'    INSIDE WITH {a.name}')
    print(f'    INSIDE WITH {b.name}')
    raise Exception('some exc')
