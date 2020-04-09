from table_sql import PlainSQL


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

    def insert_dump(self, path: str) -> int:
        cnt = self.count_edges()
        with open(path, 'r') as f:
            conn = self.engine.raw_connection()
            cursor = conn.cursor()
            cmd = f'COPY {EdgeNew.__tablename__} (v_from, v_to, weight) FROM STDIN WITH (FORMAT CSV, HEADER TRUE)'
            cursor.copy_expert(cmd, f)
            conn.commit()
        self.insert_table(EdgeNew.__tablename__)
        return self.count_edges() - cnt

    def insert_table(self, source_name: str):
        # https://stackoverflow.com/a/17267423/2766161
        migration = text(f'''
            INSERT INTO {EdgeSQL.__tablename__}
            SELECT * FROM {source_name}
            ON CONFLICT (_id) DO UPDATE SET
            (v_from, v_to, weight, attributes_json) = (EXCLUDED.v_from, EXCLUDED.v_to, EXCLUDED.weight, EXCLUDED.attributes_json);
        ''')
        self.session.execute(migration)
        self.session.commit()
