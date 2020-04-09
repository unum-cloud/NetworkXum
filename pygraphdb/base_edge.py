
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
        self._id = Edge.combine_ids(self.v_from, self.v_to)
        self.attributes = {}

    def __repr__(self) -> str:
        return f'<EdgeSQL(_id={self._id}, v_from={self.v_from}, v_to={self.v_to}, weight={self.weight})>'

    def __contains__(self, key) -> bool:
        if key == '_id':
            return self._id is not None
        return key in ['weight', 'v_from', 'v_to']

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, val):
        return setattr(self, key, val)

    @staticmethod
    def combine_ids(v_from: int, v_to: int) -> int:
        # Source: https://stackoverflow.com/a/919661
        _id = (v_from + v_to) * (v_from + v_to + 1) // 2 + v_to
        # Some databases may have smaller default integer sizes,
        # but it's bette to switch to `BigInteger`.
        # https://docs.sqlalchemy.org/en/13/core/type_basics.html#sqlalchemy.types.BigInteger
        _id = _id % (2 ** 31)
        return _id


assert (Edge.combine_ids(10, 20) != Edge.combine_ids(20, 10)), \
    'The node IDs transformation must be order-dependant.'
