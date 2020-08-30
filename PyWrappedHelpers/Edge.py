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

    # def __contains__(self, key) -> bool:
    #     return key in ['_id', 'first', 'second', 'is_directed', 'label', 'weight']

    # def __getitem__(self, key):
    #     return getattr(self, key)

    # def __setitem__(self, key, val):
    #     return setattr(self, key, val)

    @staticmethod
    def combine_ids(first: int, second: int) -> int:
        # Source: https://stackoverflow.com/a/919661
        _id = (first + second) * (first + second + 1) // 2 + second
        # Some databases may have smaller default integer sizes,
        # but it's bette to switch to `BigInteger`.
        # https://docs.sqlalchemy.org/en/13/core/type_basics.html#sqlalchemy.types.BigInteger
        _id = _id % (2 ** 31)
        return _id


assert (Edge.combine_ids(10, 20) != Edge.combine_ids(20, 10)), \
    'The node IDs transformation must be order-dependant.'


@dataclass
class Node:
    _id: int = -1
    weight: float = 1
    label: int = 0
    payload: str = ''
