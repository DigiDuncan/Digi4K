from itertools import groupby


def all_equal(iterable):
    g = groupby(iterable)
    return next(g, True) and not next(g, False)


class BigClass:
    def __init__(self, a: int) -> None:
        self.a = a

    @property
    def _sort_tuple(self) -> tuple:
        return tuple([(k, v) for k, v in self.__dict__.items()])

    def __lt__(self, other):
        if not isinstance(other, BigClass):
            return NotImplemented

        return (self.a,) + self._sort_tuple < (other.a,) + other._sort_tuple

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}({self.a})>"


class SmallClass(BigClass):
    def __init__(self, a: int, b: str, c: str) -> None:
        super().__init__(a)
        self.b = b
        self.c = c


li = [
    BigClass(10),
    SmallClass(2, "a", "z"),
    SmallClass(1, "x", "q"),
    BigClass(45)
]

sli = []

for i in range(100):
    s = sorted(li)
    print(", ".join([str(it) for it in s]))
    sli.append(s)

print(all_equal(sli))
