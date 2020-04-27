from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence
import concurrent.futures

from pygraphdb.base_edge import Edge
from pygraphdb.helpers import *


class GraphBase(object):
    """
        Abstract base class for Graph Datastructures.
        It's designed for directed weighted graphs, but can be easily tweaked.
        By default, it allows multi-edges (multiple edges connecting same nodes).
        Easiest way to preserve edge uniqness is to generate edge IDs
        by hashing IDs of nodes that it's connecting.
    """
    __max_batch_size__ = 100
    __is_concurrent__ = True
    __edge_type__ = Edge
    __in_memory__ = False

    # --------------------------------
    # region: Adding and removing nodes and edges.
    # https://networkx.github.io/documentation/stable/reference/classes/graph.html#adding-and-removing-nodes-and-edges
    # --------------------------------

    def __init__(
        self,
        is_directed=True,
        is_weighted=True,
        edge_id_generator=None,
        **kwargs,
    ):
        object.__init__(self)
        self.count_undirected_in_source_queries = True
        self.is_directed = is_directed
        self.is_weighted = is_weighted
        self.edge_id_generator = edge_id_generator
        if self.edge_id_generator is None:
            self.edge_id_generator = lambda e: self.biggest_edge_id() + 1

    @abstractmethod
    def validate_edge(self, e: object) -> Optional[object]:
        if ('v1' not in e) or ('v2' not in e):
            return None
        if '_id' not in e:
            e['_id'] = self.edge_id_generator(e)
        return e

    @abstractmethod
    def upsert_edge(self, e: object) -> bool:
        """
            Updates an `Edge` with given ID. If it's missing - creates a new one.
            If ID property isn't set - it will be computed as hash of member nodes, 
            so only one such edge can exist in DB.
        """
        pass

    @abstractmethod
    def remove_edge(self, e: object) -> bool:
        """
            Can delete edges with known ID and without.
            In the second case we only delete 1 edge, that has 
            matching `v1` and `v2` nodes without 
            searching for reverse edge.
        """
        return False

    @abstractmethod
    def upsert_edges(self, es: Sequence[object]) -> int:
        es = map_compact(self.validate_edge, es)
        successes = map(self.upsert_edge, es)
        return int(sum(successes))

    @abstractmethod
    def remove_edges(self, es: Sequence[object]) -> int:
        successes = map(self.remove_edge, es)
        return int(sum(successes))

    @abstractmethod
    def upsert_adjacency_list(self, filepath: str) -> int:
        """
            Imports data from adjacency list CSV file. Row shape: `(v1, v2, weight)`.
            Generates the edge IDs by hashing the members.
            So it guarantess edge uniqness, but is much slower than `insert_adjacency_list`.
        """
        return export_edges_into_graph(filepath, self)

    @abstractmethod
    def insert_adjacency_list(self, filepath: str) -> int:
        """
            Imports data from adjacency list CSV file. Row shape: `(v1, v2, weight)`.
            Uses the `biggest_edge_id` to generate incremental IDs for new edges.
            Doesn't guarantee edge uniqness (for 2 given nodes) as `upsert_adjacency_list` does.
        """
        return export_edges_into_graph(filepath, self)

    @abstractmethod
    def remove_all(self):
        """Remove all nodes and edges from the graph."""
        pass

    @abstractmethod
    def remove_node(self, n: int) -> int:
        """Removes all the edges containing that node."""
        return self.remove_edges(self.edges_related(n))

    # endregion

    # --------------------------------
    # region: Simple lookups.
    # https://networkx.github.io/documentation/stable/reference/classes/graph.html#reporting-nodes-edges-and-neighbors
    # --------------------------------

    @abstractmethod
    def count_nodes(self) -> int:
        pass

    @abstractmethod
    def count_edges(self) -> int:
        pass

    @abstractmethod
    def biggest_edge_id(self) -> int:
        return 0

    @abstractmethod
    def contains_node(self, v: int) -> bool:
        # TODO
        pass

    @abstractmethod
    def node_attributes(self, v: int) -> dict:
        # TODO
        pass

    # --------------------------------
    # region: Bulk reads.
    # https://networkx.github.io/documentation/stable/reference/classes/graph.html#reporting-nodes-edges-and-neighbors
    # --------------------------------

    @abstractmethod
    def iterate_nodes(self) -> Generator[object, None, None]:
        # TODO
        pass

    @abstractmethod
    def iterate_edges(self) -> Generator[object, None, None]:
        # TODO
        pass

    @abstractmethod
    def edge_directed(self, v1: int, v2: int) -> Optional[object]:
        """Only finds edges directed from `v1` to `v2`."""
        pass

    @abstractmethod
    def edge_undirected(self, v1: int, v2: int) -> Optional[object]:
        """Checks for edges in both directions."""
        pass

    @abstractmethod
    def edges_from(self, v: int) -> List[object]:
        pass

    @abstractmethod
    def edges_to(self, v: int) -> List[object]:
        pass

    @abstractmethod
    def edges_related(self, v: int) -> List[object]:
        """Finds all edges that contain `v` as part of it."""
        pass

    @abstractmethod
    def count_following(self, v: int) -> (int, float):
        """Returns the number of edges outgoing from `v` and total `weight`."""
        pass

    @abstractmethod
    def count_followers(self, v: int) -> (int, float):
        """Returns the number of edges incoming into `v` and total `weight`."""
        pass

    @abstractmethod
    def count_related(self, v: int) -> (int, float):
        """Returns the number of edges containing `v` and total `weight`."""
        pass

    # endregion

    # --------------------------------
    # region: Wider range of neighbors & analytics.
    # Most of them aren't implemented in DBs and will
    # be called through NetworkX wrapper.
    # --------------------------------

    @abstractmethod
    def nodes_related(self, v: int) -> Set[int]:
        """Returns IDs of nodes that have a shared edge with `v`."""
        vs_unique = set()
        for e in self.edges_related(v):
            vs_unique.add(e['v1'])
            vs_unique.add(e['v2'])
        vs_unique.discard(v)
        return vs_unique

    @abstractmethod
    def nodes_related_to_group(self, vs: List[int]) -> Set[int]:
        """Returns IDs of nodes that have one or more edges with members of `vs`."""
        results = set()
        for v in vs:
            results = results.union(self.nodes_related(v))
        return results.difference(set(vs))

    @abstractmethod
    def nodes_related_to_related(self, v: int, include_related=False) -> Set[int]:
        related = self.nodes_related(v)
        related_to_related = self.nodes_related_to_group(related.union({v}))
        if include_related:
            return related_to_related.union(related).difference({v})
        else:
            return related_to_related.difference(related).difference({v})

    @abstractmethod
    def shortest_path(self, v1, v2) -> List[int]:
        pass

    # endregion
