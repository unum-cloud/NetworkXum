
class Edge(object):
    """
        Shared Edge class with ID hashing for simpler collision avoidance.
        Advanced DBs can preserve object uniqness by comparing multiple keys/columns. 
        Others only support 1 primary key, so we implement hashing and type 
        checking in this class to simplify queries in pygraphdb.
    """

    def __init__(self, v_from: int, v_to: int, weight=1):
        super().__init__()
        assert isinstance(v_from, int) and isinstance(v_from, int), \
            'Non integer IDs arent supported, use hashes'
        self._id = None
        self.v_from = v_from
        self.v_to = v_to
        self.weight = weight
        self._update_hash()

    def __repr__(self):
        return f'<EdgeSQL(_id={self._id}, v_from={self.v_from}, v_to={self.v_to}, weight={self.weight})>'

    def __contains__(self, key):
        if key == '_id':
            return self._id is not None
        return key in ['weight', 'v_from', 'v_to']

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, val):
        return setattr(self, key, val)

    def _update_hash(self):
        self._id = (self.v_from + self.v_to) * \
            (self.v_from + self.v_to + 1) // 2 + self.v_to
