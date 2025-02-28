from dataclasses import dataclass


@dataclass
class GraphDegree:
    count: int = 0
    weight: float = 0

    def __int__(self):
        return self.count
