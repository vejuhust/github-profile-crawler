#!/usr/bin/env python3
"""Exporter of profiles for github profile crawler"""

from BaseLogger import BaseLogger
from DatabaseAccessor import DatabaseAccessor
from contextlib import closing
from platform import node


class Exporter(BaseLogger):
    def __init__(self, log_level=None):
        BaseLogger.__init__(self, self.__class__.__name__, log_level)
        self._db_conn = DatabaseAccessor()
        self._log_info("exporter start @%s", node())


    def process(self):
        pass

    def close(self):
        self._db_conn.close()
        self._log_info("exporter exit")
        self._close_logger()


def main():
    with closing(Exporter()) as exporter:
        pass


if __name__ == '__main__':
    main()
