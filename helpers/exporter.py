# Exports data from `stats.json` to `stats.md` in human-readable form.
from __future__ import annotations
from typing import List, Optional
from enum import Enum
import os
import json


class AggregationPolicy(Enum):
    UseFirst = 1
    FindMin = 2
    FindMax = 3


class StatsExporter(object):

    def __init__(self):
        self.stats = []
        self.table = []

    def load(self, filename) -> StatsExporter:
        contents = json.load(open(filename, 'r'))
        assert isinstance(contents, list), 'Must be a list!'
        self.stats.extend(contents)
        self.filename = filename
        return self

    def limit_to(self, **kwargs) -> StatsExporter:
        self.stats = StatsExporter.filter(self.stats, **kwargs)
        return self

    def correlate(
        self,
        field_col: str,
        field_row: str,
        field_cell: str,
    ) -> StatsExporter:
        self.table = StatsExporter.to_table(
            stats=self.stats,
            field_col=field_col,
            field_row=field_row,
            field_cell=field_cell,
        )
        return self

    def compare_by(self, column) -> StatsExporter:
        column_idx = column
        if isinstance(column, str):
            column_idx = self.table[0].index(column)
        self.table = StatsExporter.add_emoji_column(self.table, column_idx)
        return self

    def export(
        self,
        title: str,
        filename=None,
        overwrite=False,
    ) -> StatsExporter:
        if filename is None:
            base = os.path.splitext(self.filename)[0]
            filename = base + '.md'
        content = StatsExporter.render_table(self.table)
        text_file = open(filename, 'w' if overwrite else 'a')
        text_file.write(f'## {title}\n\n')
        text_file.write(content)
        text_file.write('\n\n')
        text_file.close()
        self.table = []
        return self

    @staticmethod
    def filter(
        stats: List[dict],
        **kwargs
    ) -> List[dict]:
        """
            Returns objects with matching fields.
        """
        # Define filtering predicate.
        def matches(s) -> bool:
            for k, v in kwargs.items():
                if s.get(k, None) != v:
                    return False
            return True
        # Filter.
        result = list()
        for s in stats:
            if matches(s):
                result.append(s)
        return result

    @staticmethod
    def to_table(
        stats: List[dict],
        field_col: str,
        field_row: str,
        field_cell: str,
        aggregation_policy=AggregationPolicy.UseFirst,
        allowed_rows: List[str] = [],
        allowed_cols: List[str] = [],
        add_headers=True,
    ) -> List[List[str]]:

        # Preprocessing.
        if len(allowed_rows) == 0:
            allowed_rows = {s.get(field_row, '') for s in stats}
            allowed_rows.discard('')
            allowed_rows = list(allowed_rows)
        if len(allowed_cols) == 0:
            allowed_cols = {s.get(field_col, '') for s in stats}
            allowed_cols.discard('')
            allowed_cols = list(allowed_cols)

        # Define variables.
        count_rows = len(allowed_rows)
        count_cols = len(allowed_cols)
        floats = [[None for _ in range(count_cols)] for _ in range(count_rows)]

        # Export the table.
        def index_of(vs: List[str], v: str) -> Optional[int]:
            try:
                return vs.index(v)
            except:
                return None
        for s in stats:
            if not ((field_row in s) and (field_col in s) and (field_cell in s)):
                continue
            idx_row = index_of(allowed_rows, s[field_row])
            idx_col = index_of(allowed_cols, s[field_col])
            if (idx_row is None) or (idx_col is None):
                continue
            old_val = floats[idx_row][idx_col]
            new_val = s[field_cell]
            if old_val == None:
                new_val = float(new_val)
            elif aggregation_policy == AggregationPolicy.UseFirst:
                new_val = old_val
            elif aggregation_policy == AggregationPolicy.FindMin:
                new_val = min(float(old_val), float(new_val))
            elif aggregation_policy == AggregationPolicy.FindMax:
                new_val = max(float(old_val), float(new_val))
            floats[idx_row][idx_col] = new_val

        # Generate readable strings.
        strings = [[str('%.2f' % cell) for cell in row] for row in floats]
        if add_headers:
            strings = StatsExporter.add_headers(
                strings=strings,
                col_names=allowed_cols,
                row_names=allowed_rows
            )
        return strings

    @staticmethod
    def add_headers(
        strings: List[List[str]],
        col_names: List[str],
        row_names: List[str],
    ) -> List[List[str]]:
        assert len(strings) > 0, 'Empty table!'
        assert len(row_names) == len(strings), 'Mismatch in rows number'
        assert len(col_names) == len(strings[0]), 'Mismatch in cols number'
        result = list()
        result.append(list())
        result[0].append('*')
        result[0].extend(col_names)
        for idx_row in range(len(row_names)):
            result.append(list())
            result[idx_row+1].append(row_names[idx_row])
            result[idx_row+1].extend(strings[idx_row])
        return result

    @staticmethod
    def add_emoji_column(
        table: List[List[str]],
        numeric_column: int,
        log_scale=False,
    ) -> List[List[str]]:
        values = [float(row[numeric_column]) for row in table[1:]]
        value_smallest = min(values)
        value_biggest = max(values)
        diff = (value_biggest-value_smallest)
        best_bracket_smalest_val = value_biggest - diff/3
        worst_bracket_biggest_val = value_smallest + diff/3

        table[0][numeric_column] = 'Result'
        for row in table[1:]:
            val = float(row[numeric_column])
            if val >= best_bracket_smalest_val:
                row.append(':thumbsup:')
            elif val < worst_bracket_biggest_val:
                row.append(':thumbsdown:')
            else:
                row.append('')
        return table

    @staticmethod
    def render_table(
        table: List[List[str]],
    ) -> str:
        lines = list()

        def render_line(cells: List[str]) -> str:
            line = ' | '.join(cells)
            line = f'| {line} |'
            return line

        for idx_row in range(len(table)):
            cells = table[idx_row]
            lines.append(render_line(cells))
            if idx_row == 0:
                delimeters = ['---'] * len(cells)
                lines.append(render_line(delimeters))
        return '\n'.join(lines)


StatsExporter().\
    load('bench/stats.json').\
    correlate('wrapper_name', 'operation_name', 'time_elapsed').\
    export('Simple Queries', overwrite=True)
