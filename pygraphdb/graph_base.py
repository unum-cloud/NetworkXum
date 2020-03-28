from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence

from pygraphdb.edge import Edge


class GraphBase(object):

    def __init__(self):
        super().__init__()
        pass

    def __iter__(self):
        pass

    def __len__(self):
        return self.count_edges()

    # Relatives

    @abstractmethod
    def find_directed(self, v_from: int, v_to: int) -> Optional[object]:
        """
            Given 2 vertexes that are stored in DB as 
            outgoing from `v_from` into `v_to`.
        """
        pass

    @abstractmethod
    def find_undirected(self, v1: int, v2: int) -> Optional[object]:
        """
            Given 2 vertexes search for an edge 
            that goes in any direction.
        """
        pass

    @abstractmethod
    def edges_from(self, v: int) -> List[object]:
        pass

    @abstractmethod
    def edges_to(self, v: int) -> List[object]:
        pass

    @abstractmethod
    def edges_related(self, v: int) -> List[object]:
        """
            Finds all edges that contain `v` as part of it.
        """
        pass

    # Wider range of neighbours

    @abstractmethod
    def vertexes_related(self, v: int) -> Set[int]:
        """
            Returns
            -------
            Set[int] 
                The IDs of all vertexes that have a shared edge with `v`.
        """
        vs_unique = set()
        for e in self.edges_related(v):
            vs_unique.add(e['v_from'])
            vs_unique.add(e['v_to'])
        vs_unique.remove(v)
        return vs_unique

    @abstractmethod
    def vertexes_related_to_group(self, vs: Sequence[int]) -> Set[int]:
        """
            Returns
            -------
            Set[int] 
                The IDs of all vertexes that have at 
                least one shared edge with any member of `vs`.
        """
        results = set()
        for v in vs:
            results = results.union(self.vertexes_related(v))
        return results.difference(set(vs))

    @abstractmethod
    def vertexes_related_to_related(self, v: int) -> Set[int]:
        related = self.vertexes_related(v)
        related_to_related = self.vertexes_related_to_group(related.union({v}))
        return related.union(related_to_related).difference({v})

    @abstractmethod
    def shortest_path(self, v_from, v_to) -> List[int]:
        pass

    # Metadata

    @abstractmethod
    def count_vertexes(self) -> int:
        pass

    @abstractmethod
    def count_edges(self) -> int:
        pass

    @abstractmethod
    def count_related(self, v: int) -> (int, float):
        """
            Returns
            -------
            int 
                The number of edges containing `v`.
            float
                The total `weight` of edges containing `v`
        """
        pass

    @abstractmethod
    def count_followers(self, v: int) -> (int, float):
        """
            Returns
            -------
            int 
                The number of edges incoming into `v`.
            float
                The total `weight` of edges incoming into `v`.
        """
        pass

    @abstractmethod
    def count_following(self, v: int) -> (int, float):
        """
            Returns
            -------
            int 
                The number of edges outgoing from `v`.
            float
                The total `weight` of edges outgoing from `v`.
        """
        pass

    # Modifications

    @abstractmethod
    def insert(self, e: Edge) -> bool:
        """
            Inserts an `Edge` with automatically precomputed ID.
        """
        pass

    @abstractmethod
    def delete(self, e: object) -> bool:
        """
            Can delete edges with known ID and without.
            In the second case we only delete 1 edge, that has 
            matching `v_from` and `v_to` vertexes without 
            searching for reverse edge.
        """
        pass
