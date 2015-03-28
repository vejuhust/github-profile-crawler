#!/usr/bin/env python3
"""Follower/following page parser for github profile crawler"""

from BaseLogger import BaseLogger
from DatabaseAccessor import DatabaseAccessor
from bs4 import BeautifulSoup
from config import config_queue_page, config_idle_sleep, config_parse_domain, config_parse_process
from contextlib import closing
from multiprocessing import Process
from platform import node
from time import sleep


class ParserFollow(BaseLogger):
    def __init__(self, log_level=None):
        BaseLogger.__init__(self, self.__class__.__name__, log_level)
        self._db_conn = DatabaseAccessor()
        self._log_info("follow parser start @%s", node())


    def process(self):
        status = False
        job = self._db_conn.queue_page_take_follow()
        if job != None:
            url = job['url']
            text = job.get('text', "")
            links = self._parse_user_links(url, text)
            self._log_info("parse follow page: %s, link count: %d", url, len(links))
            if links:
                for link in links:
                    if not self._db_conn.queue_crawl_create(link):
                        self._log_warning("fail to add %s as 'new' job in queue_crawl", link)
                if not self._db_conn.queue_page_done_follow(url):
                    self._log_warning("fail to mark %s as 'done_follow' in queue_page", url)
                status = True
        else:
            self._log_warning("grab no follow pages to parse")
            sleep(config_idle_sleep)
        return status


    def _parse_user_links(self, url, text):
        links = []
        soup = BeautifulSoup(text)

        for tag in soup.find_all(class_="follow-list-item"):
            if tag.find_all("a"):
                links.append(tag.find("a").get('href'))

        pagination = soup.find(class_="pagination")
        if pagination:
            for tag in pagination.find_all("a"):
                if "Next" == tag.text:
                    links.append(tag.get('href'))

        return self._purge_data_list(links, config_parse_domain)


    def _purge_data_list(self, data, prefix = None):
        purged = []
        for item in data:
            if item != None and len(item.strip()) > 0:
                if prefix == None or prefix in item:
                    purged.append(item.strip())
                else:
                    purged.append(prefix + item.strip())
        return purged


    def close(self):
        self._db_conn.close()
        self._log_info("follow parser exit")
        self._close_logger()


def main(times=10):
    with closing(ParserFollow()) as parser:
        if times:
            for _ in range(times):
                parser.process()
        else:
            while True:
                parser.process()


if __name__ == '__main__':
    for _ in range(config_parse_process):
        Process(target=main, args=(0,)).start()
