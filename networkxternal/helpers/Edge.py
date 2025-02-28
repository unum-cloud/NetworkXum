from dataclasses import dataclass, field


@dataclass(order=True)
class Edge:
    _id: int = -1
    first: int = -1
    second: int = -1
    weight: float = 1
    label: int = -1
    is_directed: bool = True
    payload: dict = field(default_factory=dict)

    def __repr__(self) -> str:
        d = "->" if self.is_directed else "-"
        return f"<Edge({self.first}{d}{self.second}, _id={self._id}, weight={self.weight})>"

    def __bool__(self):
        return self._id >= 0

    def __getitem__(self, key: int):
        # We want `Edge` to behave as `(int, int)` tuple for NetworkX compatibility.
        if isinstance(key, int):
            if key == 0:
                return self.first
            elif key == 1:
                return self.second
        return None

    def inverted(self):
        return Edge(
            _id=self._id,
            first=self.second,
            second=self.first,
            weight=self.weight,
            label=self.label,
            is_directed=self.is_directed,
            payload=self.payload,
        )

    @staticmethod
    def identify_by_members(first: int, second: int) -> int:
        # Source: https://stackoverflow.com/a/919661
        _id = (first + second) * (first + second + 1) // 2 + second
        # Some databases may have smaller default integer sizes,
        # but it's bette to switch to `BigInteger`.
        # https://docs.sqlalchemy.org/en/13/core/type_basics.html#sqlalchemy.types.BigInteger
        _id = _id % (2**31)
        return _id


assert Edge.identify_by_members(10, 20) != Edge.identify_by_members(
    20, 10
), "The node IDs transformation must be order-dependant."
