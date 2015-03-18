#!/usr/bin/env python3
"""Profile page parser for github profile crawler"""

from BaseLogger import BaseLogger
from DatabaseAccessor import DatabaseAccessor
from bs4 import BeautifulSoup
from config import config_queue_page, config_parse_domain
from contextlib import closing
from platform import node


class ParserProfile(BaseLogger):
    def __init__(self, log_level=None):
        BaseLogger.__init__(self, self.__class__.__name__, log_level)
        self._db_conn = DatabaseAccessor()
        self._log_info("profile parser start @%s", node())


    def process(self):
        status_profile, status_like = False, False
        job = self._db_conn.queue_page_take_profile()
        if job != None:
            url = job['url']
            text = job.get('text', "")
            profile, like = self._parse_profile_and_like(url, text)
            self._log_info("parse profile page: %s, items count: { profile: %d, like: %d }", url, len(profile), len(like))
            if profile:
                if not self._db_conn.profile_create(profile):
                    self._log_warning("fail to add profile of %s in database", url)
                if not self._db_conn.queue_page_done_profile(url):
                    self._log_warning("fail to mark %s as 'done_profile' in queue_page", url)
                status_profile = True
            if like:
                for key in like:
                    if not self._db_conn.queue_crawl_create(like[key]):
                        self._log_warning("fail to add %s as 'new' job in queue_crawl", like[key])
                status_like = True
        else:
            self._log_warning("grab no profile pages to parse")
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
        self._db_conn.close()
        self._close_logger()


def main():
    pass


if __name__ == '__main__':
    main()
