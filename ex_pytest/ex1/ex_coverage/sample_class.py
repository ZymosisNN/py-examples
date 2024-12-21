class MySUT:
    def __init__(self):
        self.a = 'aaa'
        self.b = 123

    def f1(self) -> list:
        res = [self.a, self.b]
        return res

    def f2(self, suff) -> list:
        res = self.f1() + [suff]
        return res
