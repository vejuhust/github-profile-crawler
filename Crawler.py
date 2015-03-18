#!/usr/bin/env python3
"""Web crawler for github profile crawler"""

from BaseLogger import BaseLogger
from DatabaseAccessor import DatabaseAccessor
from config import config_crawl_retry, config_crawl_timeout
from requests import get, codes


class Crawler(BaseLogger):
    def __init__(self):
        BaseLogger.__init__(self, self.__class__.__name__)
        self._db_conn = DatabaseAccessor()


    def process(self):
        status = False
        job = self._db_conn.queue_crawl_take()
        if job != None:
            url = job['url']
            retry_times = config_crawl_retry
            while retry_times > 0:
                text = self._crawl_page(url)
                if text == None:
                    retry_times -= 1
                else:
                    retry_times = 0
            if text == None:
                self._db_conn.queue_crawl_fail(url)
            else:
                self._db_conn.queue_page_create(url, text)
                self._db_conn.queue_crawl_done(url)
                status = True
        return status


    def _crawl_page(self, url):
        try:
            resp = get(url, timeout=config_crawl_timeout)
            if resp.status_code == codes.ok:
                return resp.text
        except Exception as e:
            pass


    def close(self):
        self._db_conn.close()
        self._close_logger()


def main():
    pass


if __name__ == '__main__':
    main()
