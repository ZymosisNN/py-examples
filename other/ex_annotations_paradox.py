# Comment this import to see errors
from __future__ import annotations


class UpperClass:
    def f(self) -> UpperClass:
        pass

    def f2(self, d: BottomClass):
        pass


class BottomClass:
    pass
