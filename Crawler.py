#!/usr/bin/env python3
"""Web crawler for github-profile-crawler"""

from pprint import pprint as pp
from requests import get, codes
from contextlib import closing
from time import sleep
from config import config_retry_times, config_sleep_sec
from DatabaseAccessor import DatabaseAccessor


class Crawler():
    def __init__(self):
        self._db_conn = DatabaseAccessor()


    def process(self):
        status = False
        job = self._db_conn.queue_crawl_take()
        if job != None:
            url = job['url']
            retry_times = config_retry_times
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
        resp = get(url)
        if resp.status_code == codes.ok:
            return resp.text


    def close(self):
        self._db_conn.close()


def main():
    with closing(DatabaseAccessor()) as dal:
        pp(dal.queue_crawl_create("https://github.com/wong2"))
        pp(dal.queue_crawl_create("https://github.com/thankcreate"))
        pp(dal.queue_crawl_create("https://github.com/xudifsd"))
        with closing(Crawler()) as crawler:
            i = 5
            while i > 0:
                crawler.process()
                sleep(config_sleep_sec)
                i -= 1
        pp(dal.queue_crawl_reset("https://github.com/wong2"))
        pp(dal.queue_crawl_reset("https://github.com/thankcreate"))
        pp(dal.queue_crawl_reset("https://github.com/xudifsd"))


if __name__ == '__main__':
    main()
