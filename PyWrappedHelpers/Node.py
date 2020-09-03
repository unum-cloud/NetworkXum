from dataclasses import dataclass, field


@dataclass(order=True)
class Node:
    _id: int = -1
    weight: float = 1
    label: int = -1
    payload: dict = field(default_factory=dict)

    def __bool__(self):
        return self._id >= 0
