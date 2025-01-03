from typing import TypeVar, Generic, Iterable, Iterator

T_co = TypeVar('T_co', covariant=True)


class ImmutableList(Generic[T_co]):
    def __init__(self, items: Iterable[T_co]) -> None: ...

    def __iter__(self) -> Iterator[T_co]: ...


class Employee: ...


class Manager(Employee): ...


def dump_employees(emps: ImmutableList[Employee]) -> None:
    for emp in emps:
        ...


mgrs = ImmutableList([Manager()])  # type: ImmutableList[Manager]
dump_employees(mgrs)  # OK
