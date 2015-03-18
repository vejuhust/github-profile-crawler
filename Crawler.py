#!/usr/bin/env python3
"""Web crawler for github profile crawler"""

from BaseLogger import BaseLogger
from DatabaseAccessor import DatabaseAccessor
from config import config_crawl_retry, config_crawl_sleep, config_crawl_process, config_crawl_timeout
from contextlib import closing
from multiprocessing import Process
from platform import node
from random import randint
from requests import get, codes
from time import sleep


class Crawler(BaseLogger):
    def __init__(self, log_level=None):
        BaseLogger.__init__(self, self.__class__.__name__, log_level)
        self._db_conn = DatabaseAccessor()
        self._log_info("crawler start @%s", node())


    def process(self):
        status = False
        job = self._db_conn.queue_crawl_take()
        if job != None:
            url = job['url']
            self._log_info("start to crawl %s", url)
            retry_times = config_crawl_retry
            while retry_times > 0:
                text = self._crawl_page(url)
                if text == None:
                    retry_times -= 1
                else:
                    retry_times = 0
            if text == None:
                self._log_warning("fail to crawl %s after %d attempts", url, config_crawl_retry)
                if not self._db_conn.queue_crawl_fail(url):
                    self._log_warning("fail to mark %s as 'fail' in queue_crawl", url)
            else:
                self._log_info("finish crawling %s, response length: %d", url, len(text))
                if not self._db_conn.queue_page_create(url, text):
                    self._log_warning("fail to add %s as 'new' job in queue_page", url)
                if not self._db_conn.queue_crawl_done(url):
                    self._log_warning("fail to mark %s as 'done' in queue_crawl", url)
                status = True
        else:
            self._log_warning("grab no jobs to crawl")
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
        self._log_info("crawler exit")
        self._close_logger()


def crawl(crawler):
    crawler.process()
    sleep(randint(1, config_crawl_sleep))


def main(times=10):
    with closing(Crawler()) as crawler:
        if times:
            for _ in range(times):
                crawl(crawler)
        else:
            while True:
                crawl(crawler)


if __name__ == '__main__':
    for _ in range(config_crawl_process):
        Process(target=main, args=(5,)).start()
