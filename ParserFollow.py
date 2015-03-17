#!/usr/bin/env python3
"""Follower/Following page parser for github profile crawler"""

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
        self._db_conn._job_update(config_queue_page, None, "follow", job['url'])
        if job != None:
            url = job['url']
            text = job.get('text', "")
            links = self._parse_user_links(url, text)
            pprint(links)
            pprint(len(links))
            self._log_info(url)
            # if links:
            #     for link in links:
            #         self._db_conn.queue_crawl_create(link)
            #     self._db_conn.queue_page_done_follow(url)
            #     status = True
        return status


    def _parse_user_links(self, url, text):
        links = []
        soup = BeautifulSoup(text)

        tags = soup.find_all(class_="follow-list-item")
        for tag in tags:
            if tag.find_all("a"):
                links.append(tag.find("a").get('href'))

        pagination = soup.find(class_="pagination")
        if pagination:
            tags = pagination.find_all("a")
            for tag in tags:
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


    def _parse_tag_text_by_itemprop(self, soup, item_name):
        tags = soup.find_all(itemprop=item_name)
        if len(tags) > 0:
            return tags[0].text


    def _parse_tag_string_by_class(self, soup, class_name):
        tags = soup.find_all(class_=class_name)
        if len(tags) > 0:
            return tags[0].string


    def _parse_tag_datetime_by_class(self, soup, class_name):
        tags = soup.find_all(class_=class_name)
        if len(tags) > 0:
            return tags[0].get('datetime')


    def _parse_tag_count_and_link(self, soup, text):
        tags = soup.find_all(class_="pagination")
        count = None
        link = None
        for tag in tags:
            if "Next" in tag.find(rel="nofollow").text:
                count = tag.find(class_="vcard-stat-count").text
                link = tag.get('href')
                break
        return count, link


    def close(self):
        self._close_logger()


def main():
    with closing(ParserFollow()) as parser:
        for _ in range(1):
            print("No. {} --".format(_ + 1))
            pprint(parser.process())


if __name__ == '__main__':
    main()
