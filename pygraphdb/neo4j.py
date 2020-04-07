from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence

from neo4j import GraphDatabase
from neo4j import BoltStatementResult

from pygraphdb.edge import Edge
from pygraphdb.graph_base import GraphBase


class Neo4j(GraphBase):
    """
        Uses Cypher DSL and Bolt API to access Neo4j graph database.

        CAUTION:
        This is a suboptimal implementation in terms of space, 
        as we can't overwrite the native node IDs with ours and have 
        to index verticies by that artificial `_id` property.
        Furthermore, indexing edge properties is only available in 
        enterprise edition, so quering edges by their ID can be even 
        less then performant than searching them by connected node IDS.
    """

    def __init__(self, url='bolt://0.0.0.0:7687', enterprise_edition=False):
        super().__init__()
        self.driver = GraphDatabase.driver(url, encrypted=False)
        self.session = self.driver.session()
        # Create constraints if needed.
        cs = self.get_constraints()
        if len(cs) == 0:
            self.create_index_nodes()
            if enterprise_edition:
                self.create_index_edges()

    def get_constraints(self):
        return list(self.session.run('CALL db.constraints').records())

    def create_index_nodes(self):
        # Existing uniqness constraint means,
        # that we don't have to create a separate index.
        # Docs: https://neo4j.com/docs/cypher-manual/current/administration/constraints/
        task = '''
        CREATE CONSTRAINT unique_nodes
        ON (v:Vertex)
        ASSERT (v._id) IS UNIQUE
        '''
        return self.session.run(task)

    def create_index_edges(self):
        # Edge uniqness constrains are only availiable to Enterprise Edition customers.
        # https://neo4j.com/docs/cypher-manual/current/administration/constraints/#administration-constraints-syntax
        task = '''
        CREATE CONSTRAINT unique_edges
        ON ()-[e:]-()
        ASSERT (e._id) IS UNIQUE
        '''
        # Indexes on relationships are not implemented yet.
        # https://stackoverflow.com/a/22444108
        # task = '''
        # CREATE INDEX ids_edges
        # FOR [e:Edge]
        # ON (e._id)
        # '''
        return self.session.run(task)

    # Relatives

    def find_edge(self, v_from: int, v_to: int) -> Optional[object]:
        pattern = '''
        MATCH (v_from:Vertex {_id: %d})-[e:Edge]->(v_to:Vertex {_id: %d})
        RETURN v_from._id, v_to._id, e.weight
        '''
        task = pattern % (v_from, v_to)
        return self._records_to_edges(self.session.run(task))

    def find_edge_or_inv(self, v1: int, v2: int) -> Optional[object]:
        pattern = '''
        MATCH (v_from:Vertex {_id: %d})-[e:Edge]-(v_to:Vertex {_id: %d})
        RETURN v_from._id, v_to._id, e.weight
        '''
        task = pattern % (v1, v2)
        return self._records_to_edges(self.session.run(task))

    def edges_from(self, v: int) -> List[object]:
        pattern = '''
        MATCH (v_from:Vertex {_id: %d})-[e:Edge]->(v_to:Vertex)
        RETURN v_from._id, v_to._id, e.weight
        '''
        task = pattern % (v)
        return self._records_to_edges(self.session.run(task))

    def edges_to(self, v: int) -> List[object]:
        pattern = '''
        MATCH (v_from:Vertex)-[e:Edge]->(v_to:Vertex {_id: %d})
        RETURN v_from._id, v_to._id, e.weight
        '''
        task = pattern % (v)
        return self._records_to_edges(self.session.run(task))

    def edges_related(self, v: int) -> List[object]:
        pattern = '''
        MATCH (v_from:Vertex {_id: %d})-[e:Edge]-(v_to:Vertex)
        RETURN v_from._id, v_to._id, e.weight
        '''
        task = pattern % (v)
        return self._records_to_edges(self.session.run(task))

    # Wider range of neighbors

    def edges_related_to_group(self, vs: Sequence[int]) -> List[Edge]:
        pattern = '''
        MATCH (v_from:Vertex)-[e:Edge]-(v_to:Vertex)
        WHERE (v_from._id IN [%s]) AND NOT (v_to._id IN [%s])
        RETURN v_from._id, v_to._id, e.weight
        '''
        group_members = ','.join([str(v) for v in vs])
        task = pattern % (group_members, group_members)
        return self._records_to_edges(self.session.run(task))

    def nodes_related_to_group(self, vs: Sequence[int]) -> Set[int]:
        pattern = '''
        MATCH (v_from:Vertex)-[:Edge]-(v_to:Vertex)
        WHERE (v_from._id IN [%s]) AND NOT (v_to._id IN [%s])
        RETURN v_to._id as _id
        '''
        group_members = ','.join([str(v) for v in vs])
        task = pattern % (group_members, group_members)
        return {int(r['_id']) for r in self.session.run(task).records()}

    def nodes_related(self, v: int) -> Set[int]:
        pattern = '''
        MATCH (:Vertex {_id: %d})-[:Edge]-(v_related:Vertex)
        RETURN v_related._id as _id
        '''
        task = pattern % (v)
        return {int(r['_id']) for r in self.session.run(task).records()}

    def nodes_related_to_related(self, v: int, include_related=False) -> Set[int]:
        if include_related:
            pattern = '''
            MATCH (v:Vertex {_id: %d})-[:Edge]-(:Vertex)-[:Edge]-(v_unrelated:Vertex)
            WHERE NOT (v._id = v_unrelated._id)
            RETURN v_unrelated._id as _id
            '''
            task = pattern % v
        else:
            pattern = '''
            MATCH (v:Vertex {_id: %d})-[:Edge]-(:Vertex)-[:Edge]-(v_unrelated:Vertex)
            WHERE NOT EXISTS {
                MATCH (v)-[:Edge]-(v_unrelated)
            } AND NOT (v._id = v_unrelated._id)
            RETURN v_unrelated._id as _id
            '''
            task = pattern % v
        return {int(r['_id']) for r in self.session.run(task).records()}

    def shortest_path(self, v_from, v_to) -> (List[int], float):
        pattern = '''
        MATCH (v_from:Vertex {_id: %d}), (v_to:Vertex {_id: %d})
        CALL algo.shortestPath.stream(v_from, v_to, "weight")
        YIELD nodeId, weight
        MATCH (v_on_path:Loc) WHERE id(v_on_path) = nodeId
        RETURN v_on_path._id AS _id, weight
        '''
        rs = list(self.session.run(task).records())
        path = [int(r['_id']) for r in rs]
        weight = sum([float(r['weight']) for r in rs])
        return path, weight

    # Metadata

    def count_nodes(self) -> int:
        task = '''
        MATCH (v:Vertex)
        WITH count(v) as result
        RETURN result
        '''
        return int(self._first_record(self.session.run(task), 'result'))

    def count_edges(self) -> int:
        task = '''
        MATCH ()-[e:Edge]->()
        WITH count(e) as result
        RETURN result
        '''
        return int(self._first_record(self.session.run(task), 'result'))

    def count_related(self, v: int) -> (int, float):
        pattern = '''
        MATCH (v:Vertex {_id: %d})-[e:Edge]-()
        WITH count(e) as c, sum(e.weight) as s
        RETURN c, s
        '''
        task = pattern % v
        rs = list(self.session.run(task).records())
        c = int(self._first_record(rs, 'c'))
        s = float(self._first_record(rs, 's'))
        return c, s

    def count_followers(self, v: int) -> (int, float):
        pattern = '''
        MATCH ()-[e:Edge]->(v:Vertex {_id: %d})
        WITH count(e) as c, sum(e.weight) as s
        RETURN c, s
        '''
        task = pattern % v
        rs = list(self.session.run(task).records())
        c = int(self._first_record(rs, 'c'))
        s = float(self._first_record(rs, 's'))
        return c, s

    def count_following(self, v: int) -> (int, float):
        pattern = '''
        MATCH (v:Vertex {_id: %d})-[e:Edge]->()
        WITH count(e) as c, sum(e.weight) as s
        RETURN c, s
        '''
        task = pattern % v
        rs = list(self.session.run(task).records())
        c = int(self._first_record(rs, 'c'))
        s = float(self._first_record(rs, 's'))
        return c, s

    # Modifications

    def insert_edge(self, e: Edge) -> bool:
        pattern = '''
        MERGE (v1:Vertex {_id: %d})
        MERGE (v2:Vertex {_id: %d})
        MERGE (v1)-[:Edge {_id: %d, weight: %d}]->(v2)
        '''
        task = pattern % (e['v_from'], e['v_to'], e['_id'], e['weight'])
        return self.session.run(task)

    def insert_many(self, es: List[Edge]) -> int:
        vs = set()
        for e in es:
            vs.add(e['v_from'])
            vs.add(e['v_to'])
        task = str()
        # First upsert all the nodes.
        for v in vs:
            pattern = 'MERGE (v%d:Vertex {_id: %d})'
            part = (pattern % (v, v))
            task += part
            task += '\n'
        # Then add the edges connecting matched nodes.
        for e in es:
            pattern = 'MERGE (v%d)-[:Edge {_id: %d, weight: %d}]->(v%d)'
            part = (pattern % (e['v_from'], e['_id'], e['weight'], e['v_to']))
            task += part
            task += '\n'
        return self.session.run(task)

    def remove_node(self, v: int):
        pattern = '''
        MATCH (v:Vertex {_id: %d})
        DETACH DELETE v
        '''
        task = pattern % v
        return self.session.run(task)

    def remove_edge(self, e: object) -> bool:
        task = str()
        if '_id' in e:
            # We provide excessive information on node IDs
            # to use property indexes.
            pattern = '''
            MATCH (v1:Vertex {_id: %d})
            MATCH (v2:Vertex {_id: %d})
            MATCH (v1)-[e:Edge {_id: %d}]->(v2)
            DELETE e
            '''
            task = pattern % (e['v_from'], e['v_to'], e['_id'])
        else:
            pattern = '''
            MATCH (v1:Vertex {_id: %d})
            MATCH (v2:Vertex {_id: %d})
            MERGE (v1)-[e:Edge]->(v2)
            DELETE e
            '''
            task = pattern % (e['v_from'], e['v_to'])
        return self.session.run(task)

    def remove_all(self):
        try:
            self.session.run('DROP CONSTRAINT unique_nodes;')
        except:
            pass
        self.session.run('MATCH (v) DETACH DELETE v;')

    # def insert_dump(self, filepath: str):
    #     """
    #         The file path must be within the standard import directory:
    #         https://neo4j.com/docs/operations-manual/4.0/configuration/file-locations/
    #         This method works better with remote URLs.
    #     """
    #     pattern = '''
    #     LOAD CSV FROM '%s' AS row
    #     WITH
    #         toInteger(row[0]) AS id_from,
    #         toInteger(row[1]) AS id_to,
    #         toFloat(row[2]) AS w
    #     MERGE (v1:Vertex {_id: id_from})
    #     MERGE (v2:Vertex {_id: id_to})
    #     MERGE (v1)-[:Edge {_id: (floor((id_from + id_to) * (id_from + id_to + 1) / 2.0)+id_to), weight: w}]->(v2)
    #     '''
    #     task = pattern % filepath
    #     self.session.run(task)

    # ---
    # Helper methods.
    # ---

    def _records_to_edges(self, records) -> List[Edge]:
        if isinstance(records, BoltStatementResult):
            records = list(records.records())
        return [Edge(r['v_from._id'], r['v_to._id'], r['e.weight']) for r in records]

    def _first_record(self, records, key):
        if isinstance(records, BoltStatementResult):
            records = list(records.records())
        if len(records) == 0:
            return None
        return records[0][key]
