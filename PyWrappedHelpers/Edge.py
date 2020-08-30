from dataclasses import dataclass


@dataclass
class Edge:
    _id: int = -1
    first: int = -1
    second: int = -1
    weight: float = 1
    label: int = 0
    is_directed: bool = True

    def __repr__(self) -> str:
        d = '->' if self.is_directed else '-'
        return f'<Edge({self.first}{d}{self.second}, _id={self._id}, weight={self.weight})>'

    @staticmethod
    def identify_by_members(first: int, second: int) -> int:
        # Source: https://stackoverflow.com/a/919661
        _id = (first + second) * (first + second + 1) // 2 + second
        # Some databases may have smaller default integer sizes,
        # but it's bette to switch to `BigInteger`.
        # https://docs.sqlalchemy.org/en/13/core/type_basics.html#sqlalchemy.types.BigInteger
        _id = _id % (2 ** 31)
        return _id


assert (Edge.identify_by_members(10, 20) != Edge.identify_by_members(20, 10)), \
    'The node IDs transformation must be order-dependant.'


@dataclass
class Node:
    _id: int = -1
    weight: float = 1
    label: int = 0
    payload: str = ''
