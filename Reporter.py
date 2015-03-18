#!/usr/bin/env python3
"""Assign parsing page jobs in queue_page for github profile crawler"""

from BaseLogger import BaseLogger
from DatabaseAccessor import DatabaseAccessor
from bs4 import BeautifulSoup
from config import config_parse_process
from contextlib import closing
from multiprocessing import Process
from platform import node


class Reporter(BaseLogger):
    def __init__(self, log_level=None):
        BaseLogger.__init__(self, self.__class__.__name__, log_level)
        self._db_conn = DatabaseAccessor()
        self._log_info("reporter start @%s", node())


    def process(self):
        pass


    def close(self):
        self._db_conn.close()
        self._log_info("reporter exit")
        self._close_logger()


def main():
    with closing(Reporter()) as reporter:
        reporter.process()


if __name__ == '__main__':
    main()
