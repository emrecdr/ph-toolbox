import csv
import sys
from typing import Optional


class CsvStore:
    def __init__(self, filename: str = "store.csv"):
        self.file = filename

    def read_all_by_idx(self, idx: int = 0, filename: Optional[str] = None, include_1st_row: bool = True):
        if filename is None:
            filename = self.file
        with open(filename, mode="r", newline="") as store_file:
            store_reader = csv.reader(store_file, delimiter=",")
            try:
                data = [row[idx] if idx < len(row) else None for row in store_reader]
            except csv.Error as e:
                sys.exit(f"File {filename}, line {store_reader.line_num}: {e}")

        return data if include_1st_row else data[1:]

    def write_row(self, data: list, filename: Optional[str] = None):
        if filename is None:
            filename = self.file
        with open(filename, mode="a", newline="") as store_file:
            store_writer = csv.writer(store_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            store_writer.writerow(data)
