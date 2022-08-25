from typing import Protocol


class Fartable(Protocol):
    def fart(self): ...


class A:
    def vomit(self):
        print('vomit')


class B:
    def fart(self):
        print('fart')


def func(obj: Fartable):
    obj.fart()


a = A()
func(a)

b = B()
func(b)
