# Exports data from `stats.json` to `stats.md` in human-readable form.
from __future__ import annotations
from typing import List, Optional
from enum import Enum
import os
import json
import re
import locale

import psutil


class AggregationPolicy(Enum):
    UseFirst = 1
    FindMin = 2
    FindMax = 3


class StatsExporter(object):

    def __init__(self):
        self.filtered_stats = []
        self.current_table = []
        self.full_content = ''

    def reload_stats(self, filename: str) -> StatsExporter:
        self.filtered_stats = []
        return self.import_stats(filename)

    def import_stats(self, filename: str) -> StatsExporter:
        contents = json.load(open(filename, 'r'))
        assert isinstance(contents, list), 'Must be a list!'
        assert len(contents) > 0, 'Shouldnt be empty!'
        self.filtered_stats.extend(contents)
        return self

    def export_to(self, filename: str, overwrite=True) -> StatsExporter:
        text_file = open(filename, 'w' if overwrite else 'a')
        text_file.write(self.full_content)
        text_file.close()
        self.full_content = ''
        return self

    def add_text(self, text: str) -> StatsExporter:
        # Remove whitespaces in front of every row.
        text = '\n'.join([line.strip() for line in text.splitlines()])
        self.full_content += f'{text}\n'
        # Headers must have 2 line spacings.
        if text.startswith('#'):
            self.full_content += '\n'
        return self

    def add_last_table(self) -> StatsExporter:
        content = StatsExporter.render_table(self.current_table)
        self.full_content += content
        self.full_content += '\n\n'
        self.current_table = []
        return self

    def filter_stats(self, **kwargs) -> StatsExporter:
        self.filtered_stats = StatsExporter.filter(
            self.filtered_stats,
            **kwargs
        )
        return self

    def correlate_all_values(
        self,
        field_col: str,
        field_row: str,
        field_cell: str,
    ) -> StatsExporter:
        self.current_table = StatsExporter.to_table(
            stats=self.filtered_stats,
            field_col=field_col,
            field_row=field_row,
            field_cell=field_cell,
        )
        return self

    def correlate(
        self,
        field_col: str,
        field_row: str,
        field_cell: str,
        allowed_cols: List[str],
        allowed_rows: List[str],
    ) -> StatsExporter:
        self.current_table = StatsExporter.to_table(
            stats=self.filtered_stats,
            field_col=field_col,
            field_row=field_row,
            field_cell=field_cell,
            allowed_rows=allowed_rows,
            allowed_cols=allowed_cols,
        )
        return self

    def compare_by(self, column) -> StatsExporter:
        column_idx = column
        if isinstance(column, str):
            column_idx = self.current_table[0].index(column)
        self.current_table = StatsExporter.add_emoji_column(
            self.current_table,
            column_idx
        )
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
                if v is None:
                    pass
                elif isinstance(v, re.Pattern):
                    if not v.search(s.get(k, '')):
                        return False
                elif s.get(k, None) != v:
                    return False
            return True
        # Filter.
        result = list()
        for s in stats:
            if matches(s):
                result.append(s)
        return result

    @staticmethod
    def num2str(num: float) -> str:
        if num is None:
            return ''
        if isinstance(num, str):
            return num
        return '{:,.2f}'.format(num)

    @staticmethod
    def str2num(str_: str) -> float:
        if str_ is None or len(str_) == 0:
            return None
        if isinstance(str_, float):
            return str_
        str_ = str_.replace(',', '')
        return float(str_)

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
        strings = [[StatsExporter.num2str(c) for c in r] for r in floats]
        if add_headers:
            strings = StatsExporter.add_headers(
                strings=strings,
                col_names=allowed_cols,
                row_names=allowed_rows,
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
        result[0].append('')
        result[0].extend(col_names)
        for idx_row in range(len(row_names)):
            result.append(list())
            result[idx_row+1].append(row_names[idx_row])
            result[idx_row+1].extend(strings[idx_row])
        return result

    @staticmethod
    def add_emoji_column(
        table: List[List[str]],
        col_idx: int,
        log_scale=False,
    ) -> List[List[str]]:
        values = [StatsExporter.str2num(r[col_idx]) for r in table[1:]]
        values = [v for v in values if v is not None]
        value_smallest = min(values) if len(values) else 0
        value_biggest = max(values) if len(values) else 1
        diff = (value_biggest-value_smallest)
        best_bracket_smalest_val = value_biggest - diff/3
        worst_bracket_biggest_val = value_smallest + diff/3

        table[0].append('Result')
        for r in table[1:]:
            val = StatsExporter.str2num(r[col_idx])
            if val is None:
                r.append('?')
            elif val >= best_bracket_smalest_val:
                r.append(':thumbsup:')
            elif val < worst_bracket_biggest_val:
                r.append(':thumbsdown:')
            else:
                r.append('')
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
                delimeters = [':---'] + [':---:'] * (len(cells) - 1)
                lines.append(render_line(delimeters))
        return '\n'.join(lines)
