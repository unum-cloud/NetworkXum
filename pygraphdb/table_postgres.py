from pygraphdb.table_sql import PlainSQL, EdgeNew, EdgeSQL


class PostgreSQL(PlainSQL):
    """
        Extends PlainSQL functionality with optimized operations:
        *   Bulk imports and exports via:
            https://github.com/jmcarp/sqlalchemy-postgres-copy
        *   Async operations through less mature ORM: Gino (only PostgreSQL).
            https://github.com/python-gino/gino
        *   Allows natively quering JSON subproperties via:
            https://sqlalchemy-utils.readthedocs.io/en/latest/data_types.html#module-sqlalchemy_utils.types.json        
    """

    def __init__(self, url, **kwargs):
        PlainSQL.__init__(self, url, **kwargs)
        self.set_pragmas_on_first_launch()

    def set_pragmas_on_first_launch(self):
        if self.count_edges() > 0:
            return
        # https://www.percona.com/blog/2018/08/31/tuning-postgresql-database-parameters-to-optimize-performance/
        # https://www.revsys.com/writings/postgresql-performance.html
        pragmas = [
            # Performance over reliability.
            "SET synchronous_commit=0;",
            # Unlike other databases, PostgreSQL does not provide direct IO.
            # That means data is stored in memory twice, first in PostgreSQL buffer and then kernel buffer.
            # But this can't be changed without restarting the DB.
            # "SET shared_buffers='512MB';",
            # "SET wal_buffers='32MB';",
        ]
        with self.get_session() as s:
            for p in pragmas:
                s.execute(p)
                s.commit()

    # TODO: Change the IDs of imported entries.
    # def upsert_adjacency_list(self, path: str) -> int:
    #     cnt = self.count_edges()
    #     with open(path, 'r') as f:
    #         conn = self.engine.raw_connection()
    #         cursor = conn.cursor()
    #         cmd = f'COPY {EdgeNew.__tablename__} (v_from, v_to, weight) FROM STDIN WITH (FORMAT CSV, HEADER TRUE)'
    #         cursor.copy_expert(cmd, f)
    #         conn.commit()
    #     self.upsert_table(EdgeNew.__tablename__)
    #     return self.count_edges() - cnt

    def upsert_table(self, source_name: str):
        # https://stackoverflow.com/a/17267423/2766161
        migration = f'''
            INSERT INTO {EdgeSQL.__tablename__}
            SELECT * FROM {source_name}
            ON CONFLICT (_id) DO UPDATE SET
            (v_from, v_to, weight, attributes_json) = (EXCLUDED.v_from, EXCLUDED.v_to, EXCLUDED.weight, EXCLUDED.attributes_json);
        '''
        with self.get_session() as s:
            s.execute(migration)
            s.commit()
