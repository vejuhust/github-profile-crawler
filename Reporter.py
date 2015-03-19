#!/usr/bin/env python3
"""Assign parsing page jobs in queue_page for github profile crawler"""

from BaseLogger import BaseLogger
from DatabaseAccessor import DatabaseAccessor
from bs4 import BeautifulSoup
from config import config_report_interval
from contextlib import closing
from datetime import datetime
from json import loads, dumps
from os.path import isfile
from platform import node
from time import sleep, strftime


class Reporter(BaseLogger):
    def __init__(self, log_level=None):
        BaseLogger.__init__(self, self.__class__.__name__, log_level)
        self._db_conn = DatabaseAccessor()
        self._log_info("reporter start @%s", node())


    def process(self):
        self.update_data()
        return


    def update_data(self):
        data = self._load_data()
        self._log_info("load existing data, count: %d", len(data))
        status = {
            "crawl_all": self._db_conn.queue_crawl_count(),
            "crawl_new": self._db_conn.queue_crawl_count("new"),
            "crawl_fail": self._db_conn.queue_crawl_count("fail"),
            "page_all": self._db_conn.queue_page_count(),
            "page_new": self._db_conn.queue_page_count("new"),
            "page_profile": self._db_conn.queue_page_count("profile"),
            "page_follow": self._db_conn.queue_page_count("follow"),
            "page_unknown": self._db_conn.queue_page_count("unknown"),
            "profile": self._db_conn.profile_count(),
            "profile_email": self._db_conn.profile_count("email"),
            "date": strftime("%Y-%m-%d %H:%M:%S"),
        }
        data.append(status)
        self._save_data(data)
        self._log_info("save existing data, count: %d", len(data))
        self._log_info(dumps(status, sort_keys=True, indent=4))


    def _load_data(self, filename="status.json"):
        data = {}
        if isfile(filename):
            try:
                data_file = open(filename, 'r')
                content = data_file.read()
                data_file.close()
                data = loads(content)
            except Exception as e:
                self._log_exception("fail to load json file: %s", filename)
        else:
            self._log_warning("fail to find json file: %s", filename)
        return data


    def _save_data(self, data, filename="status.json"):
        output_file = open(filename, 'w')
        output_file.write(dumps(data, sort_keys = True, indent = 4))
        output_file.close()


    def _extract_list(self, data, field):
        return [ item[field] for item in data ]


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
