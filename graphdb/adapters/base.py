from abc import ABC, abstractmethod


class GraphBase(object):

    def __init__(self):
        super().__init__()
        pass

    def __iter__(self):
        pass

    def __len__(self):
        pass

    @abstractmethod
    def create_index(self):
        pass

    @abstractmethod
    def insert(self, e: object) -> bool:
        pass

    @abstractmethod
    def delete(self, e: object) -> bool:
        pass

    @abstractmethod
    def find_directed(self, v_from, v_to) -> Optional[object]:
        pass

    @abstractmethod
    def find_undirected(self, v1, v2) -> Optional[object]:
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
        pass

    @abstractmethod
    def vertexes_related_to_group(self, vs) -> Set[int]:
        pass

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
