

class Stats(object):

    def __init__(self, filename='benchmarks.json'):
        self.filename = filename
        self.device_name = platform.node()
        self.results = []
        self.reset_from_file(self.filename)

    def __del__(self):
        self.dump_from_file(self.filename)

    @staticmethod
    def bench_matches(
        bench: obj,
        adapter_class: str,
        operation: str,
    ) -> bool:
        if bench['device'] != self.device_name:
            return False
        if bench['adapter_class'] != adapter_class:
            return False
        if bench['operation'] != operation:
            return False
        return True

    def update_stats(
        adapter_class: str,
        operation: str,
        stats: StatsCounter,
    ):
        def predicate(b):
            return bench_matches(b, adapter_class, operation)
        bench = next(filter(predicate, benchmarks), None)
        stats_serialized = {
            'time_elapsed': stats.time_elapsed,
            'count_operations': stats.count_operations,
        }
        if bench is None:
            self.results.append(stats_serialized)
        else:
            bench = stats_serialized

    def reset_from_file(self, filename):
        print('- Restoring previous benchmarks')
        self.results = json.load(open(filename, 'r'))

    def dump_from_file(self, filename):
        json.dump(self.results, open(filename, 'w'))
