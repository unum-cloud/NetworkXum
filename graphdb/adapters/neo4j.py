from neo4j import GraphDatabase

from shared import *


class GraphNeo4j(GraphBase):

    def __init__(self, url='bolt://localhost:7687', collection_name=''):
        super().__init__()
        self.driver = GraphDatabase.driver(url, auth=("neo4j", "password"))

        pass

    def create_index(self):
        pass

    def insert(self, e: object) -> bool:
        pass

    def delete(self, e: object) -> bool:
        pass

    def __iter__(self):
        pass

    def find_directed(self, v_from, v_to) -> Optional[object]:
        pass

    def find_undirected(self, v1, v2) -> Optional[object]:
        pass

    # Relatives

    def edges_from(self, v: int) -> List[object]:
        pass

    def edges_to(self, v: int) -> List[object]:
        pass

    def edges_related(self, v: int) -> List[object]:
        pass

    def vertexes_related(self, v: int) -> Set[int]:
        pass

    # Wider range of neighbours

    def vertexes_related_to_related(self, v: int) -> Set[int]:
        pass

    def vertexes_related_to_group(self, vs) -> Set[int]:
        pass

    # Metadata

    def count_related(self, v: int) -> (int, float):
        pass

    def count_followers(self, v: int) -> (int, float):
        pass

    def count_following(self, v: int) -> (int, float):
        pass
