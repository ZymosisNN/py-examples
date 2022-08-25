from typing import Any
from dataclasses import dataclass


@dataclass
class Some:
    weird_shit: Any
    last_hope: int


my_list = [Some(2, 2),
           Some(1, 0),
           Some(None, 3),
           Some('a', 5),
           Some('string', 4),
           Some(True, 7),
           Some(False, 6),
           Some([20, 10], 1)]


def sorting_tuple(x):
    return (bool(x.weird_shit),
            int(x.weird_shit) if isinstance(x.weird_shit, int) else 100,
            x.last_hope
            )


sorted_list = sorted(my_list, key=sorting_tuple)

for i in sorted_list:
    print(bool(i.weird_shit), i)
    # print(i)



