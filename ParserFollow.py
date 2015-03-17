#!/usr/bin/env python3
"""Follower/following page parser for github profile crawler"""

from BaseLogger import BaseLogger
from DatabaseAccessor import DatabaseAccessor
from bs4 import BeautifulSoup
from config import config_queue_page, config_parse_domain
from contextlib import closing
from pprint import pprint


class ParserFollow(BaseLogger):
    def __init__(self):
        BaseLogger.__init__(self, self.__class__.__name__)
        self._db_conn = DatabaseAccessor()


    def process(self):
        status = False
        job = self._db_conn.queue_page_take_follow()
        if job != None:
            url = job['url']
            text = job.get('text', "")
            links = self._parse_user_links(url, text)
            self._log_info(url)
            if links:
                for link in links:
                    self._db_conn.queue_crawl_create(link)
                self._db_conn.queue_page_done_follow(url)
                status = True
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
        self._close_logger()


def main():
    pass


if __name__ == '__main__':
    main()
