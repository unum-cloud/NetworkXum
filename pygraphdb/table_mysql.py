from table_sql import PlainSQL


class MySQL(PlainSQL):

    def __init__(self, url):
        PlainSQL.__init__(self, url)
        self.set_pragmas_on_first_launch()

    def set_pragmas_on_first_launch(self):
        if self.count_edges() > 0:
            return
        # https://stackoverflow.com/a/60717467/2766161
        pragmas = [
            'SET GLOBAL local_infile=1;',
        ]
        for p in pragmas:
            self.session.execute(p)
            self.session.commit()

    def insert_dump_native(self, path: str) -> int:
        """
            This method requires the file to be mounted on the same filesystem.
            Unlike Postgres the connection wrapper doesn't allow channeling data to remote DB.            
        """
        cnt = self.count_edges()
        pattern = '''
        LOAD DATA LOCAL INFILE  '%s'
        INTO TABLE %s
        FIELDS TERMINATED BY ',' 
        LINES TERMINATED BY '\n'
        IGNORE 1 ROWS
        (v_from, v_to, weight);
        '''
        task = pattern % (path, EdgeNew.__tablename__)
        self.session.execute(task)
        self.session.commit()
        self.insert_table(EdgeNew.__tablename__)
        return self.count_edges() - cnt
