#!/usr/bin/env python3
"""Exporter of profiles for github profile crawler"""

from BaseLogger import BaseLogger
from DatabaseAccessor import DatabaseAccessor
from contextlib import closing
from platform import node
from json import dumps
from csv import DictWriter


class Exporter(BaseLogger):
    def __init__(self, log_level=None):
        BaseLogger.__init__(self, self.__class__.__name__, log_level)
        self._db_conn = DatabaseAccessor()
        self._log_info("exporter start @%s", node())


    def process(self):
        data = self._db_conn.profile_read()
        self._log_info("load all profiles data from database")
        self._save_as_json(data)
        self._save_as_csv(data)


    def _save_as_json(self, data, filename="profile.json"):
        with open(filename, 'w') as jsonfile:
            jsonfile.write(dumps(data, sort_keys=True, indent=4))
        self._log_info("saved as json file: %s", filename)


    def _save_as_csv(self, data, filename="profile.csv"):
        fields = set()
        for item in data:
            fields = fields.union(set(item.keys()))
        with open(filename, 'w') as csvfile:
            writer = DictWriter(csvfile, extrasaction='ignore', dialect='excel', fieldnames=sorted(fields, reverse=True))
            writer.writeheader()
            for item in data:
                writer.writerow(item)
        self._log_info("saved as csv file: %s", filename)


    def close(self):
        self._db_conn.close()
        self._log_info("exporter exit")
        self._close_logger()


def main():
    with closing(Exporter()) as exporter:
        exporter.process()


if __name__ == '__main__':
    main()
