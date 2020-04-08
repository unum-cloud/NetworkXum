
class BulkImporter(object):
    """
    Performs multithreaded bulk import into DB.
    Saves stats.
    """

    def __init__(
        self,
        graph: GraphBase,
        stats: StatsFile,
        dataset_path: str,
    ):
        self.graph = graph
        self.stats = stats
        self.dataset_path = dataset_path

    def run(self):
        counter = StatsCounter()
        counter.handle(lambda: self.graph.import_bulk(self.dataset_path))
        self.stats.insert(

        )
