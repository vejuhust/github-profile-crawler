#!/usr/bin/env python3
"""Assign parsing page jobs in queue_page for github profile crawler"""

from BaseLogger import BaseLogger
from DatabaseAccessor import DatabaseAccessor
from bs4 import BeautifulSoup
from config import config_report_interval
from contextlib import closing
from json import dumps
from platform import node
from time import sleep


class Reporter(BaseLogger):
    def __init__(self, log_level=None):
        BaseLogger.__init__(self, self.__class__.__name__, log_level)
        self._db_conn = DatabaseAccessor()
        self._log_info("reporter start @%s", node())


    def process(self):
        status = {
            "crawl all": self._db_conn.queue_crawl_count(),
            "crawl new": self._db_conn.queue_crawl_count("new"),
            "crawl fail": self._db_conn.queue_crawl_count("fail"),
            "page all": self._db_conn.queue_page_count(),
            "page new": self._db_conn.queue_page_count("new"),
            "page profile": self._db_conn.queue_page_count("profile"),
            "page follow": self._db_conn.queue_page_count("follow"),
            "page unknown": self._db_conn.queue_page_count("unknown"),
            "profile": self._db_conn.profile_count(),
            "profile w/ loc": self._db_conn.profile_count("location"),
            "profile w/ name": self._db_conn.profile_count("name"),
            "profile w/ email": self._db_conn.profile_count("email"),
            "profile w/ name & email": self._db_conn.profile_count("name", "email"),
        }
        self._log_info(dumps(status, sort_keys=True, indent=4))


    def close(self):
        self._db_conn.close()
        self._log_info("reporter exit")
        self._close_logger()


def main():
    with closing(Reporter()) as reporter:
        while True:
            reporter.process()
            sleep(config_report_interval)


if __name__ == '__main__':
    main()
