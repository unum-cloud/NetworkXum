from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence
import concurrent.futures


from PyWrappedGraph.Algorithms import *


class BaseAPI(object):
    """
        Abstract base class for Documents Datastore.
        It's designed with JSON files in mind.
    """
    __max_batch_size__ = 100
    __is_concurrent__ = True
    __in_memory__ = False

    # --------------------------------
    # region: Adding and removing documents.
    # https://networkx.github.io/documentation/stable/reference/classes/graph.html#adding-and-removing-nodes-and-edges
    # --------------------------------

    def __init__(
        self,
        indexed_fields: Sequence[str],
        **kwargs,
    ):
        object.__init__(self)
        self.indexed_fields = indexed_fields

    @abstractmethod
    def upsert_doc(self, e: object) -> bool:
        pass

    @abstractmethod
    def remove_doc(self, e: object) -> bool:
        return False

    @abstractmethod
    def upsert_docs(self, es: Sequence[object]) -> int:
        es = map_compact(self.validate_edge, es)
        successes = map(self.upsert_edge, es)
        return int(sum(successes))

    @abstractmethod
    def remove_docs(self, es: Sequence[object]) -> int:
        successes = map(self.remove_edge, es)
        return int(sum(successes))

    @abstractmethod
    def upsert_docs_from_directory(self, filepath: str) -> int:
        """
            Imports data from adjacency list CSV file. Row shape: `(v1, v2, weight)`.
            Generates the edge IDs by hashing the members.
            So it guarantess edge uniqness, but is much slower than `insert_adjacency_list`.
        """
        return export_edges_into_graph(filepath, self)

    @abstractmethod
    def remove_all(self):
        """Remove all nodes and edges from the graph."""
        pass

    @abstractmethod
    def cound_docs(self) -> int:
        """Nummber of documents indexes by DB."""
        pass

    # endregion

    # --------------------------------
    # region: Search Queries.
    # https://networkx.github.io/documentation/stable/reference/classes/graph.html#reporting-nodes-edges-and-neighbors
    # --------------------------------

    @abstractmethod
    def find_substring(self, field: str, query: str) -> Sequence[object]:
        pass

    @abstractmethod
    def find_regex(self, field: str, query: str) -> Sequence[object]:
        pass

    # endregion
