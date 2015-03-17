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
        status = False
        job = self._db_conn.queue_page_take_profile()
        # self._db_conn._job_update(config_queue_page, None, "profile", job['url'])
        if job != None:
            url = job['url']
            text = job.get('text', "")
            profile, like = self._parse_profile_and_like(url, text)
            self._log_info(profile)
            self._log_info(like)
            if profile:
                status = True
        return status


    def _parse_profile_and_like(self, url, text):
        self._log_info("parse {} now".format(url))
        profile = {}
        like = {}
        soup = BeautifulSoup(text)
        profile["login"] = self._parse_tag_text_by_itemprop(soup, "additionalName")
        profile["name"] = self._parse_tag_text_by_itemprop(soup, "name")
        profile["company"] = self._parse_tag_text_by_itemprop(soup, "worksFor")
        profile["location"] = self._parse_tag_text_by_itemprop(soup, "homeLocation")
        profile["blog"] = self._parse_tag_text_by_itemprop(soup, "url")
        profile["email"] = self._parse_tag_string_by_class(soup, "email")
        profile["join_at"] = self._parse_tag_datetime_by_class(soup, "join-date")
        profile["followers"], like["followers"] = self._parse_tag_count_and_link(soup, "Followers")
        profile["following"], like["following"] = self._parse_tag_count_and_link(soup, "Following")
        profile["starred"], _ = self._parse_tag_count_and_link(soup, "Starred")
        return self._purge_data_dict(profile), self._purge_data_dict(like, config_parse_domain)


    def _purge_data_dict(self, data, prefix = None):
        purged = {}
        for key in data:
            if data[key] != None and len(data[key]) > 0:
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
            if tag.find(class_="text-muted").text == text:
                count = tag.find(class_="vcard-stat-count").text
                link = tag.get('href')
                break
        return count, link


    def close(self):
        self._log_info("bye bye!")
        self._close_logger()


def main():
    with closing(ParserProfile()) as parser:
        for _ in range(10):
            print("No. {} --".format(_ + 1))
            pprint(parser.process())


if __name__ == '__main__':
    main()
