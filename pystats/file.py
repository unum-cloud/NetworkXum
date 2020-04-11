import json
from typing import Optional
from os import path
import platform

from pygraphdb.helpers import StatsCounter


class StatsFile(object):

    def __init__(self, filename='artifacts/stats.json'):
        self.filename = filename
        self.device_name = platform.node()
        self.results = []
        self.reset_from_file(self.filename)

    # This is highly unreliable:
    # https://stackoverflow.com/a/29737870/2766161
    # def __del__(self):
    #     self.dump_to_file(self.filename)

    def bench_matches(
        self,
        bench: object,
        wrapper_name: str,
        operation_name: str,
        dataset: str,
    ) -> bool:
        if bench.get('device', None) != self.device_name:
            return False
        if bench.get('database', None) != wrapper_name:
            return False
        if bench.get('operation', None) != operation_name:
            return False
        if bench.get('dataset', None) != dataset:
            return False
        return True

    def find_index(
        self,
        wrapper_class: str,
        operation_name: str,
        dataset: str = '',
    ) -> Optional[int]:
        for i, r in enumerate(self.results):
            if self.bench_matches(r, wrapper_class, operation_name, dataset):
                return i
        return None

    def upsert(
        self,
        wrapper_class: str,
        operation_name: str,
        dataset: str,
        stats: StatsCounter,
    ):
        bench_idx = self.find_index(wrapper_class, operation_name, dataset)
        stats_serialized = {
            'device': self.device_name,
            'time_elapsed': stats.time_elapsed,
            'count_operations': stats.count_operations,
            'msecs_per_operation': stats.msecs_per_op(),
            'operations_per_second': stats.ops_per_sec(),
            'operation': operation_name,
            'database': wrapper_class,
            'dataset': dataset,
        }
        if bench_idx is None:
            bench_idx.results.append(stats_serialized)
        else:
            self.results[bench_idx] = stats_serialized

    def reset_from_file(self, filename=None):
        if filename is None:
            filename = self.filename
        if not path.exists(filename):
            self.results = []
            return
        with open(filename, 'r') as f:
            self.results = json.load(f)

    def dump_to_file(self, filename=None):
        if filename is None:
            filename = self.filename
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=4)
