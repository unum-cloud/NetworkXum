# Columns are: "from_id", "to_id", "weight"
# Allowed databases:
# - PostgreSQL
# - SQLite
# - MySQL
from shared import *


class GraphSQL(GraphBase):

    def __init__(self, url, table_name: str):
        super().__init__()
        self.table_name = table_name
        pass

    def create_index(self):
        f'''
        CREATE INDEX index_from
        ON {self.table_name}(from); 
        CREATE INDEX index_to
        ON {self.table_name}(to); 
        '''
        pass

    def insert(self, e: object) -> bool:
        pass

    def delete(self, e: object) -> bool:
        pass

    def edge_directed(self, v_from, v_to) -> Optional[object]:
        pass

    def edge_undirected(self, v1, v2) -> Optional[object]:
        pass

    # Relatives

    def edges_from(self, v: int) -> List[object]:
        f'''
        SELECT * FROM {self.table_name}
        WHERE from='{v}';
        '''
        pass

    def edges_to(self, v: int) -> List[object]:
        f'''
        SELECT * FROM {self.table_name}
        WHERE to='{v}';
        '''
        pass

    def edges_friends(self, v: int) -> List[object]:
        f'''
        SELECT * FROM {self.table_name}
        WHERE from={v} OR to='{v}';
        '''
        pass

    def vertexes_friends(self, v: int) -> Set[int]:
        pass

    # Wider range of neighbours

    def vertexes_friends_of_friends(self, v: int) -> Set[int]:
        pass

    def vertexes_friends_of_group(self, vs) -> Set[int]:
        pass

    # Metadata

    def count_degree(self, v: int) -> (int, float):
        pass

    def count_followers(self, v: int) -> (int, float):
        pass

    def count_following(self, v: int) -> (int, float):
        pass
