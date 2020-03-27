from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Generator, Set, Tuple

from pygraphdb.edge import Edge


class GraphBase(object):

    def __init__(self):
        super().__init__()
        pass

    def __iter__(self):
        pass

    def __len__(self):
        return self.count_edges()

    @abstractmethod
    def insert(self, e: Edge) -> bool:
        pass

    @abstractmethod
    def delete(self, e: object) -> bool:
        pass

    @abstractmethod
    def find_directed(self, v_from: int, v_to: int) -> Optional[object]:
        pass

    @abstractmethod
    def find_directed(self, v1: int, v2: int) -> Optional[object]:
        pass

    # Relatives

    @abstractmethod
    def edges_from(self, v: int) -> List[object]:
        pass

    @abstractmethod
    def edges_to(self, v: int) -> List[object]:
        pass

    @abstractmethod
    def edges_related(self, v: int) -> List[object]:
        pass

    @abstractmethod
    def vertexes_related(self, v: int) -> Set[int]:
        pass

    # Wider range of neighbours

    @abstractmethod
    def vertexes_related_to_related(self, v: int) -> Set[int]:
        related = self.vertexes_related(v)
        related_to_related = self.vertexes_related_to_group(related.union({v}))
        return related.union(related_to_related).difference({v})

    @abstractmethod
    def vertexes_related_to_group(self, vs) -> Set[int]:
        results = set()
        for v in vs:
            results = results.union(self.vertexes_related(v))
        return results.difference(set(vs))

    # Metadata

    @abstractmethod
    def count_related(self, v: int) -> (int, float):
        pass

    @abstractmethod
    def count_followers(self, v: int) -> (int, float):
        pass

    @abstractmethod
    def count_following(self, v: int) -> (int, float):
        pass

    @abstractmethod
    def count_vertexes(self) -> int:
        pass

    @abstractmethod
    def count_edges(self) -> int:
        pass
