
class Edge(object):
    """
        Shared Edge class with ID hashing for simpler collision avoidance.
        Advanced DBs can preserve object uniqness by comparing multiple keys/columns.
        Others only support 1 primary key, so we implement hashing and type
        checking in this class to simplify queries in pygraphdb.
    """

    def __init__(self, v1: int, v2: int, weight=1, _id=None, **kwargs):
        super().__init__()
        assert isinstance(v1, int) and isinstance(v1, int), \
            'Non integer IDs arent supported, use hashes'
        self._id = _id
        self.v1 = v1
        self.v2 = v2
        self.directed = True
        self.weight = weight
        self.attributes = kwargs

    def __repr__(self) -> str:
        d = '->' if self.directed else '-'
        return f'<EdgeSQL({self.v1}{d}{self.v2}, _id={self._id}, weight={self.weight})>'

    def __contains__(self, key) -> bool:
        if key == '_id':
            return self._id is not None
        return key in ['weight', 'v1', 'v2', 'directed']

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, val):
        return setattr(self, key, val)

    @staticmethod
    def combine_ids(v1: int, v2: int) -> int:
        # Source: https://stackoverflow.com/a/919661
        _id = (v1 + v2) * (v1 + v2 + 1) // 2 + v2
        # Some databases may have smaller default integer sizes,
        # but it's bette to switch to `BigInteger`.
        # https://docs.sqlalchemy.org/en/13/core/type_basics.html#sqlalchemy.types.BigInteger
        _id = _id % (2 ** 31)
        return _id


assert (Edge.combine_ids(10, 20) != Edge.combine_ids(20, 10)), \
    'The node IDs transformation must be order-dependant.'
