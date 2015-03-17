#!/usr/bin/env python3
"""Profile page parser for github profile crawler"""

from BaseLogger import BaseLogger
from DatabaseAccessor import DatabaseAccessor
from bs4 import BeautifulSoup
from config import config_queue_page, config_parse_domain
from contextlib import closing
from pprint import pprint


class ParserProfile(BaseLogger):
    def __init__(self):
        BaseLogger.__init__(self, self.__class__.__name__)
        self._db_conn = DatabaseAccessor()


    def process(self):
        status_profile, status_like = False, False
        job = self._db_conn.queue_page_take_profile()
        if job != None:
            url = job['url']
            text = job.get('text', "")
            profile, like = self._parse_profile_and_like(url, text)
            if profile:
                self._db_conn.profile_create(profile)
                self._db_conn.queue_page_done_profile(url)
                status_profile = True
            if like:
                for key in like:
                    self._db_conn.queue_crawl_create(like[key])
                status_like = True
        return status_profile, status_like


    def _parse_profile_and_like(self, url, text):
        profile = {}
        like = {}
        soup = BeautifulSoup(text)
        profile["url"] = url
        profile["login"] = self._parse_tag_text_by_itemprop(soup, "additionalName")
        profile["name"] = self._parse_tag_text_by_itemprop(soup, "name")
        profile["company"] = self._parse_tag_text_by_itemprop(soup, "worksFor")
        profile["location"] = self._parse_tag_text_by_itemprop(soup, "homeLocation")
        profile["blog"] = self._parse_tag_text_by_itemprop(soup, "url")
        profile["email"] = self._parse_tag_string_by_class(soup, "email")
        profile["join_at"] = self._parse_tag_datetime_by_class(soup, "join-date")
        profile["follower"], like["follower"] = self._parse_tag_count_and_link(soup, "Follower")
        profile["following"], like["following"] = self._parse_tag_count_and_link(soup, "Following")
        profile["starred"], _ = self._parse_tag_count_and_link(soup, "Starred")
        return self._purge_data_dict(profile), self._purge_data_dict(like, config_parse_domain)


    def _purge_data_dict(self, data, prefix = None):
        purged = {}
        for key in data:
            if data[key] != None and len(data[key].strip()) > 0:
                if prefix == None:
                    purged[key] = data[key].strip()
                else:
                    purged[key] = prefix + data[key].strip()
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
        tags = soup.find_all(class_="vcard-stat")
        count = None
        link = None
        for tag in tags:
            if text in tag.find(class_="text-muted").text:
                count = tag.find(class_="vcard-stat-count").text
                link = tag.get('href')
                break
        return count, link


    def close(self):
        self._close_logger()


def main():
    pass


if __name__ == '__main__':
    main()
