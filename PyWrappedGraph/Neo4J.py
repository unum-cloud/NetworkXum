import os
import shutil
from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence
from urllib.parse import urlparse

from neo4j import GraphDatabase
from neo4j import BoltStatementResult

from PyWrappedHelpers.Edge import Edge
from PyWrappedGraph.BaseAPI import BaseAPI
from PyWrappedHelpers.Algorithms import *


class Neo4J(BaseAPI):
    """
        Uses Cypher DSL and Bolt API to access Neo4J graph database.

        CAUTION 1:
        This is a suboptimal implementation in terms of space,
        as we can't overwrite the native node IDs with ours and have
        to index verticies by that artificial `_id` property.
        Furthermore, indexing edge properties is only available in
        enterprise edition, so quering edges by their ID can be even
        less then performant than searching them by connected node IDS.

        CAUTION 2:
        Neo4J doesn't have easy switching mechanism between different
        databases on the same server. That's why we have to use "labels"
        to distringuish nodes and edges belonging to disjoint datasets,
        but mixed into the same pot.

        CAUTION 3:
        Neo4J is written in Java (unlike most other DBs) and is very
        rude to other processes running on the same machine :)
        The CPU utilization is often 10-20x higher than in other DBs.
        To import 30 MB CSV file it allocated 1.4 GB of RAM!!!

        CAUTION 4:
        It constantly crashes with different codes and included query 
        profiler outputs incosistent results. Examples:
        *   `neobolt.exceptions.TransientError:`
            There is not enough stack size to perform the current task. 
            This is generally considered to be a database error, 
            so please contact Neo4J support.
        *   `neobolt.exceptions.DatabaseError`
            Java heap space...
    """
    # Depending on the machine this can be higher.
    # But on a laptop we would get "Java heap space" error.
    __max_batch_size__ = 1000
    __is_concurrent__ = True
    __edge_type__ = Edge

    def __init__(
        self,
        url='bolt://localhost:7687/graph',
        enterprise_edition=False,
        import_directory='/Users/av/Library/Application Support/Neo4J Desktop/Application/neo4jDatabases/database-b5d1180d-a778-47d2-84e6-4169343543ea/installation-4.0.3/import',
        use_full_name_for_label=False,
        use_indexes_over_constraints=True,
        **kwargs,
    ):
        BaseAPI.__init__(self, **kwargs)
        self.import_directory = import_directory

        # Neo4J can't resolve DB name, username or password on its own.
        url_obj = urlparse(url)
        url_clean = '{x.scheme}://{x.hostname}:{x.port}/'.format(x=url_obj)
        self.driver = GraphDatabase.driver(
            url_clean,
            encrypted=False,
            user=url_obj.username,
            password=url_obj.password,
        )
        self.session = self.driver.session()

        # Resolve the name (for CAUTION 2):
        name = str()
        for c in extract_database_name(url):
            if (c in "qwertyuiopasdfghjklzxcvbnm") or\
                (c in "QWERTYUIOPAFGHJKLZXCVBNM") or\
                    (c in "1234567890"):
                name += c
        self._v = 'v' + name
        self._e = 'e' + name
        # Create constraints if needed.
        self.use_indexes_over_constraints = use_indexes_over_constraints
        if use_indexes_over_constraints:
            idxs = self.get_indexes()
            if f'index{self._v}' not in idxs:
                self.create_index_nodes()
        else:
            cs = self.get_constraints()
            if f'constraint{self._v}' not in cs:
                self.create_constraint_nodes()
            if f'constraint{self._e}' not in cs:
                if enterprise_edition:
                    self.create_constraint_edges()

    def get_constraints(self) -> List[str]:
        cs = list(self.session.run('CALL db.constraints').records())
        names = [c.get('name', '') for c in cs]
        return names

    def get_indexes(self) -> List[str]:
        cs = list(self.session.run('CALL db.indexes').records())
        names = [c.get('name', '') for c in cs]
        return names

    def create_index_nodes(self):
        # Docs for CYPHER direct syntax:
        # https://neo4j.com/docs/cypher-manual/current/administration/indexes-for-search-performance/index.html#administration-indexes-syntax
        task = 'CREATE INDEX indexVERTEX FOR (v:VERTEX) ON (v._id)'
        # Older version didn't have index names.
        # Docs for `db.` operations.
        # https://neo4j.com/docs/operations-manual/current/reference/procedures/#ref-procedure-reference-enterprise-edition
        # task = 'CALL db.createIndex(":VERTEX(_id)", "native-btree-1.0", )'
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        return self.session.run(task)

    def create_constraint_nodes(self):
        # Existing uniqness constraint means,
        # that we don't have to create a separate index.
        # Docs: https://neo4j.com/docs/cypher-manual/current/administration/constraints/
        task = f'''
        CREATE CONSTRAINT constraintVERTEX
        ON (v:VERTEX)
        ASSERT (v._id) IS UNIQUE
        '''
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        return self.session.run(task)

    def create_constraint_edges(self):
        # Edge uniqness constrains are only availiable to Enterprise Edition customers.
        # https://neo4j.com/docs/cypher-manual/current/administration/constraints/#administration-constraints-syntax
        task = f'''
        CREATE CONSTRAINT uniqueEDGE
        ON ()-[e:EDGE]-()
        ASSERT (e._id) IS UNIQUE
        '''
        # Indexes on relationships are not implemented yet.
        # https://stackoverflow.com/a/22444108
        # task = '''
        # CREATE INDEX ids_edges
        # FOR [e:EDGE]
        # ON (e._id)
        # '''
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        return self.session.run(task)

    # Relatives

    def edge_directed(self, v1: int, v2: int) -> Optional[object]:
        pattern = '''
        MATCH (v1:VERTEX {_id: %d})-[e:EDGE]->(v2:VERTEX {_id: %d})
        RETURN v1._id, v2._id, e.weight
        '''
        task = pattern % (v1, v2)
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        return self._records_to_edges(self.session.run(task))

    def edge_undirected(self, v1: int, v2: int) -> Optional[object]:
        pattern = '''
        MATCH (v1:VERTEX {_id: %d})-[e:EDGE]-(v2:VERTEX {_id: %d})
        RETURN v1._id, v2._id, e.weight
        '''
        task = pattern % (v1, v2)
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        return self._records_to_edges(self.session.run(task))

    def edges_from(self, v: int) -> List[object]:
        pattern = '''
        MATCH (v1:VERTEX {_id: %d})-[e:EDGE]->(v2:VERTEX)
        RETURN v1._id, v2._id, e.weight
        '''
        task = pattern % (v)
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        return self._records_to_edges(self.session.run(task))

    def edges_to(self, v: int) -> List[object]:
        pattern = '''
        MATCH (v1:VERTEX)-[e:EDGE]->(v2:VERTEX {_id: %d})
        RETURN v1._id, v2._id, e.weight
        '''
        task = pattern % (v)
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        return self._records_to_edges(self.session.run(task))

    def edges_related(self, v: int) -> List[object]:
        pattern = '''
        MATCH (v1:VERTEX {_id: %d})-[e:EDGE]-(v2:VERTEX)
        RETURN v1._id, v2._id, e.weight
        '''
        task = pattern % (v)
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        return self._records_to_edges(self.session.run(task))

    # Wider range of neighbors

    def edges_related_to_group(self, vs: Sequence[int]) -> List[Edge]:
        pattern = '''
        MATCH (v1:VERTEX)-[e:EDGE]-(v2:VERTEX)
        WHERE (v1._id IN [%s]) AND NOT (v2._id IN [%s])
        RETURN v1._id, v2._id, e.weight
        '''
        group_members = ','.join([str(v) for v in vs])
        task = pattern % (group_members, group_members)
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        return self._records_to_edges(self.session.run(task))

    def nodes_related_to_group(self, vs: Sequence[int]) -> Set[int]:
        pattern = '''
        MATCH (v1:VERTEX)-[:EDGE]-(v2:VERTEX)
        WHERE (v1._id IN [%s]) AND NOT (v2._id IN [%s])
        RETURN v2._id as _id
        '''
        group_members = ','.join([str(v) for v in vs])
        task = pattern % (group_members, group_members)
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        return {int(r['_id']) for r in self.session.run(task).records()}

    def nodes_related(self, v: int) -> Set[int]:
        pattern = '''
        MATCH (:VERTEX {_id: %d})-[:EDGE]-(v_related:VERTEX)
        RETURN v_related._id as _id
        '''
        task = pattern % (v)
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        return {int(r['_id']) for r in self.session.run(task).records()}

    def nodes_related_to_related(self, v: int, include_related=False) -> Set[int]:
        if include_related:
            pattern = '''
            MATCH (v:VERTEX {_id: %d})-[:EDGE]-(:VERTEX)-[:EDGE]-(v_unrelated:VERTEX)
            WHERE NOT (v._id = v_unrelated._id)
            RETURN v_unrelated._id as _id
            '''
            task = pattern % v
        else:
            pattern = '''
            MATCH (v:VERTEX {_id: %d})-[:EDGE]-(:VERTEX)-[:EDGE]-(v_unrelated:VERTEX)
            WHERE NOT EXISTS {
                MATCH (v)-[e_banned:EDGE]-(v_unrelated)
            } AND NOT (v._id = v_unrelated._id)
            RETURN v_unrelated._id as _id
            '''
            task = pattern % v
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        return {int(r['_id']) for r in self.session.run(task).records()}

    def shortest_path(self, v1, v2) -> (List[int], float):
        pattern = '''
        MATCH (v1:VERTEX {_id: %d}), (v2:VERTEX {_id: %d})
        CALL algo.shortestPath.stream(v1, v2, "weight")
        YIELD nodeId, weight
        MATCH (v_on_path:Loc) WHERE id(v_on_path) = nodeId
        RETURN v_on_path._id AS _id, weight
        '''
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        rs = list(self.session.run(task).records())
        path = [int(r['_id']) for r in rs]
        weight = sum([float(r['weight']) for r in rs])
        return path, weight

    # Metadata

    def count_nodes(self) -> int:
        task = f'''
        MATCH (v:{self._v})
        WITH count(v) as result
        RETURN result
        '''
        return int(self._first_record(self.session.run(task), 'result'))

    def count_edges(self) -> int:
        task = f'''
        MATCH ()-[e:{self._e}]->()
        WITH count(e) as result
        RETURN result
        '''
        return int(self._first_record(self.session.run(task), 'result'))

    def count_related(self, v: int) -> (int, float):
        pattern = '''
        MATCH (v:VERTEX {_id: %d})-[e:EDGE]-()
        WITH count(e) as c, sum(e.weight) as s
        RETURN c, s
        '''
        task = pattern % v
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        rs = list(self.session.run(task).records())
        c = int(self._first_record(rs, 'c'))
        s = float(self._first_record(rs, 's'))
        return c, s

    def count_followers(self, v: int) -> (int, float):
        pattern = '''
        MATCH (:VERTEX)-[e:EDGE]->(v:VERTEX {_id: %d})
        WITH count(e) as c, sum(e.weight) as s
        RETURN c, s
        '''
        task = pattern % v
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        rs = list(self.session.run(task).records())
        c = int(self._first_record(rs, 'c'))
        s = float(self._first_record(rs, 's'))
        return c, s

    def count_following(self, v: int) -> (int, float):
        pattern = '''
        MATCH (v:VERTEX {_id: %d})-[e:EDGE]->(:VERTEX)
        WITH count(e) as c, sum(e.weight) as s
        RETURN c, s
        '''
        task = pattern % v
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        rs = list(self.session.run(task).records())
        c = int(self._first_record(rs, 'c'))
        s = float(self._first_record(rs, 's'))
        return c, s

    def biggest_edge_id(self) -> int:
        task = '''
        MATCH (:VERTEX)-[e:EDGE]->(:VERTEX)
        RETURN e._id AS _id
        ORDER BY _id DESC
        LIMIT 1
        '''
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        rs = list(self.session.run(task).records())
        if len(rs) == 0:
            return 0
        return int(self._first_record(rs, '_id'))

    def upsert_edge(self, e: Edge) -> bool:
        """
            CAUTION: True Upserting is too slow, if indexing isn't enabled,
            as we need to perform full scans to match each edge ID!
            So for the non-enterprise version - we strongly recommend 
            using `insert_edge()`
        """
        pattern = '''
        MERGE (v1:VERTEX {_id: %d})
        MERGE (v2:VERTEX {_id: %d})
        MERGE (v1)-[:EDGE {_id: %d, weight: %d}]%s(v2)
        '''
        d = '->' if e['directed'] else '-'
        task = pattern % (e['v1'], e['v2'], e['_id'], e['weight'], d)
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        self.session.run(task)
        return True

    def insert_edge(self, e: Edge) -> bool:
        pattern = '''
        MERGE (v1:VERTEX {_id: %d})
        MERGE (v2:VERTEX {_id: %d})
        CREATE (v1)-[:EDGE {_id: %d, weight: %d}]%s(v2)
        '''
        d = '->' if e['directed'] else '-'
        task = pattern % (e['v1'], e['v2'], e['_id'], e['weight'], d)
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        self.session.run(task)
        return True

    def insert_edges(self, es: List[Edge]) -> int:
        vs = set()
        for e in es:
            vs.add(e['v1'])
            vs.add(e['v2'])
        task = str()
        # First upsert all the nodes.
        for v in vs:
            pattern = 'MERGE (v%d:VERTEX {_id: %d})'
            part = (pattern % (v, v))
            task += part
            task += '\n'
        # Then add the edges connecting matched nodes.
        for e in es:
            pattern = 'CREATE (v%d)-[:EDGE {_id: %d, weight: %d}]%s(v%d)'
            d = '->' if e['directed'] else '-'
            part = (pattern % (e['v1'], e['_id'], e['weight'], d, e['v2']))
            task += part
            task += '\n'
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        self.session.run(task)
        return len(es)

    def remove_node(self, v: int):
        pattern = '''
        MATCH (v:VERTEX {_id: %d})
        DETACH DELETE v
        '''
        task = pattern % v
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        return self.session.run(task)

    def remove_edge(self, e: object) -> bool:
        task = str()
        if '_id' in e:
            # We provide excessive information on node IDs
            # to use property indexes.
            pattern = '''
            MATCH (v1:VERTEX {_id: %d})
            MATCH (v2:VERTEX {_id: %d})
            MATCH (v1)-[e:EDGE {_id: %d}]%s(v2)
            DELETE e
            '''
            d = '->' if e['directed'] else '-'
            task = pattern % (e['v1'], e['v2'], e['_id'], d)
        else:
            pattern = '''
            MATCH (v1:VERTEX {_id: %d})
            MATCH (v2:VERTEX {_id: %d})
            MATCH (v1)-[e:EDGE]%s(v2)
            DELETE e
            '''
            d = '->' if e['directed'] else '-'
            task = pattern % (e['v1'], e['v2'], d)
        task = task.replace('VERTEX', self._v)
        task = task.replace('EDGE', self._e)
        self.session.run(task)
        return True

    def remove_all(self):
        self.session.run(f'MATCH (v:{self._v}) DETACH DELETE v')
        idxs = self.get_indexes()
        if f'index{self._v}' in idxs:
            self.session.run(f'DROP INDEX index{self._v}')
        cs = self.get_constraints()
        if f'constraint{self._v}' in cs:
            self.session.run(f'DROP CONSTRAINT constraint{self._v}')
        if f'constraint{self._e}' in cs:
            self.session.run(f'DROP CONSTRAINT constraint{self._e}')

    def insert_adjacency_list(self, filepath: str) -> int:
        chunk_len = Neo4J.__max_batch_size__
        count_edges_added = 0
        for es in chunks(yield_edges_from_csv(filepath), chunk_len):
            count_edges_added += self.insert_edges(es)
        return count_edges_added

    def insert_adjacency_list_at_once(self, filepath: str, directed=True) -> int:
        """
            This function may be tricky to use!

            CAUTION 1: This operation makes a temporary copy of the entire dump 
            and places it into pre-specified `import_directory`:
            https://neo4j.com/docs/operations-manual/4.0/configuration/file-locations/

            CAUTION 2: This frequently fails with following error:
            `neobolt.exceptions.DatabaseError`: "Java heap space".
        """
        cnt = self.count_edges()
        current_id = self.biggest_edge_id() + 1
        _, filename = os.path.split(filepath)

        # We will need to link the file to import folder.
        file_link = os.path.expanduser(self.import_directory)
        file_link = os.path.join(file_link, filename)
        file_link = os.path.abspath(file_link)

        try:
            shutil.copy(filepath, file_link)
            # https://neo4j.com/docs/cypher-manual/current/clauses/load-csv/#load-csv-importing-large-amounts-of-data
            pattern_full = '''
            LOAD CSV WITH HEADERS FROM '%s' AS row
            WITH
                toInteger(row.v1) AS id_from,
                toInteger(row.v2) AS id_to,
                toFloat(row.weight) AS w,
                toInteger(linenumber()) AS idx
            MERGE (v1:VERTEX {_id: id_from})
            MERGE (v2:VERTEX {_id: id_to})
            CREATE (v1)-[:EDGE {_id: idx + %d, weight: w}]%s(v2)
            '''
            d = '->' if directed else '-'
            task = pattern_full % (
                'file:///' + filename, current_id, d
            )
            task = task.replace('VERTEX', self._v)
            task = task.replace('EDGE', self._e)
            print('task is:', task)
            self.session.run(task)
        finally:
            # Don't forget to copy temporary file!
            os.unlink(file_link)
        return self.count_edges() - cnt

    def insert_adjacency_list_in_parts(self, filepath: str, directed=True) -> int:
        """
            This function may be tricky to use!

            CAUTION 1: This operation makes a temporary copy of the entire dump 
            and places it into pre-specified `import_directory`:
            https://neo4j.com/docs/operations-manual/4.0/configuration/file-locations/

            CAUTION 2: This frequently fails with following error:
            `neobolt.exceptions.DatabaseError`: "Java heap space".
        """
        cnt = self.count_edges()
        current_id = self.biggest_edge_id() + 1
        _, filename = os.path.split(filepath)

        # We will need to link the file to import folder.
        file_link = os.path.expanduser(self.import_directory)
        file_link = os.path.join(file_link, filename)
        file_link = os.path.abspath(file_link)

        try:
            shutil.copy(filepath, file_link)
            # https://neo4j.com/docs/cypher-manual/current/clauses/load-csv/#load-csv-importing-large-amounts-of-data
            pattern_nodes = '''
            USING PERIODIC COMMIT %d
            LOAD CSV WITH HEADERS FROM '%s' AS row
            WITH
                toInteger(row.v1) AS id_from,
                toInteger(row.v2) AS id_to
            MERGE (v1:VERTEX {_id: id_from})
            MERGE (v2:VERTEX {_id: id_to});
            '''
            pattern_edges = '''
            USING PERIODIC COMMIT %d
            LOAD CSV WITH HEADERS FROM '%s' AS row
            WITH
                toInteger(row.v1) AS id_from,
                toInteger(row.v2) AS id_to,
                toFloat(row.weight) AS w,
                toInteger(linenumber()) AS idx
            MATCH (v1:VERTEX {_id: id_from})
            MATCH (v2:VERTEX {_id: id_to})
            CREATE (v1)-[e:EDGE {_id: idx + %d, weight: w}]%s(v2)
            RETURN count(e)
            '''
            d = '->' if directed else '-'
            tasks = [
                pattern_nodes % (
                    Neo4J.__max_batch_size__, 'file:///' + filename
                ),
                pattern_edges % (
                    Neo4J.__max_batch_size__, 'file:///' + filename, current_id, d
                ),
            ]
            for task in tasks:
                task = task.replace('VERTEX', self._v)
                task = task.replace('EDGE', self._e)
                self.session.run(task)
        finally:
            # Don't forget to copy temporary file!
            os.unlink(file_link)
        return self.count_edges() - cnt

    # ---
    # Helper methods.
    # ---

    def _records_to_edges(self, records) -> List[Edge]:
        if isinstance(records, BoltStatementResult):
            records = list(records.records())
        return [Edge(r['v1._id'], r['v2._id'], r['e.weight']) for r in records]

    def _first_record(self, records, key):
        if isinstance(records, BoltStatementResult):
            records = list(records.records())
        if len(records) == 0:
            return None
        return records[0][key]
