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
        print("crawl all: %d" % self._db_conn.queue_crawl_count())
        print("crawl new: %d" % self._db_conn.queue_crawl_count("new"))
        print("crawl fail: %d" % self._db_conn.queue_crawl_count("fail"))

        print("page all: %d" % self._db_conn.queue_page_count())
        print("page new: %d" % self._db_conn.queue_page_count("new"))
        print("page profile: %d" % self._db_conn.queue_page_count("profile"))
        print("page follow: %d" % self._db_conn.queue_page_count("follow"))
        print("page unknown: %d" % self._db_conn.queue_page_count("unknown"))

        print("profile: %d" % self._db_conn.profile_count())
        print("profile w/ loc: %d" % self._db_conn.profile_count("location"))
        print("profile w/ name: %d" % self._db_conn.profile_count("name"))
        print("profile w/ email: %d" % self._db_conn.profile_count("email"))
        print("profile w/ name & email: %d" % self._db_conn.profile_count("name", "email"))


    def close(self):
        self._db_conn.close()
        self._log_info("reporter exit")
        self._close_logger()


def main():
    with closing(Reporter()) as reporter:
        reporter.process()


if __name__ == '__main__':
    main()
