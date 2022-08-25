class My:
    def __init__(self, v):
        self.v = v

    def __str__(self):
        return f'My({self.v})'

    def __or__(self, other):
        print(f'__or__ Left: {self}, Right: {other}')
        return False

    def __ror__(self, other):
        print(f'__ror__ Left: {other}, Right: {self}')
        return False

    def __mul__(self, other):
        print(f'__mul__ Left: {self}, Right: {other}')

    def __rmul__(self, other):
        print(f'__rmul__ Left: {other}, Right: {self}')

    def __matmul__(self, other):
        print(f'__matmul__ Left: {self}, Right: {other}')

    def __lshift__(self, other):
        print(f'__lshift__ Left: {self}, Right: {other}')

    def __rlshift__(self, other):
        print(f'__rlshift__ Left: {other}, Right: {self}')

    def __ior__(self, other):
        print(f'__ior__ Left: {self}, Right: {other}')

    def __truediv__(self, other):
        print(f'__truediv__ Left: {self}, Right: {other}')

    def __floordiv__(self, other):
        print(f'__floordiv__ Left: {self}, Right: {other}')


a = My(1)
b = My(2)

# a | b
# 1 | b
# 1 * b
# a @ b
# a << b
a / b
a // b



# a |= b
