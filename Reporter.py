#!/usr/bin/env python3
"""Tracking database status for github profile crawler"""

from BaseLogger import BaseLogger
from DatabaseAccessor import DatabaseAccessor
from bs4 import BeautifulSoup
from config import config_report_interval, config_report_item, config_report_status
from contextlib import closing
from json import loads, dumps
from os.path import isfile
from platform import node
from pygal import StackedLine
from pygal.style import RotateStyle
from time import sleep, strftime


class Reporter(BaseLogger):
    def __init__(self, log_level=None):
        BaseLogger.__init__(self, self.__class__.__name__, log_level)
        self._db_conn = DatabaseAccessor()
        self._log_info("reporter start @%s", node())


    def process(self):
        data = self._update_data()
        self._draw_charts_with_data(data)
        return


    def _update_data(self):
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
        return data


    def _load_data(self, filename=config_report_status):
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


    def _save_data(self, data, filename=config_report_status):
        output_file = open(filename, 'w')
        output_file.write(dumps(data, sort_keys = True, indent = 4))
        output_file.close()


    def _draw_charts_with_data(self, data):
        self._draw_chart_summary(data[-config_report_item:])
        self._draw_chart_crawl(data[-config_report_item:])
        self._draw_chart_page(data[-config_report_item:])
        self._draw_chart_profile(data[-config_report_item:])


    def _get_chart_with_style(self):
        dark_rotate_style = RotateStyle('#9e6ffe')
        return StackedLine(fill=True, disable_xml_declaration=True, include_x_axis=True, human_readable=True, interpolate='cubic', style=dark_rotate_style)


    def _extract_list(self, data, field):
        return [ item[field] for item in data ]


    def _extract_date_list(self, data):
        return [ item["date"].split()[-1][:5] for item in data ]


    def _draw_chart_summary(self, data, filename='static/chart_summary.svg'):
        list_crawl = self._extract_list(data, "crawl_all")
        list_page = self._extract_list(data, "page_all")
        list_profile = self._extract_list(data, "profile")
        line_chart = self._get_chart_with_style()
        line_chart.title = 'Status Summary'
        line_chart.x_labels = self._extract_date_list(data)
        line_chart.add('Profile', list_profile)
        line_chart.add('Page', list_page)
        line_chart.add('Crawl', list_crawl)
        line_chart.render_to_file(filename)
        return filename


    def _draw_chart_crawl(self, data, filename='static/chart_crawl.svg'):
        list_all = self._extract_list(data, "crawl_all")
        list_new = self._extract_list(data, "crawl_new")
        list_fail = self._extract_list(data, "crawl_fail")
        list_done = [ list_all[i] - list_new[i] - list_fail[i] for i in range(len(list_all))]
        line_chart = self._get_chart_with_style()
        line_chart.title = 'Queue Crawl Status'
        line_chart.x_labels = self._extract_date_list(data)
        line_chart.add('Failed', list_fail)
        line_chart.add('Done', list_done)
        line_chart.add('Todo', list_new)
        line_chart.render_to_file(filename)
        return filename


    def _draw_chart_page(self, data, filename='static/chart_page.svg'):
        list_all = self._extract_list(data, "page_all")
        list_new = self._extract_list(data, "page_new")
        list_profile = self._extract_list(data, "page_profile")
        list_follow = self._extract_list(data, "page_follow")
        list_unknown = self._extract_list(data, "page_unknown")
        list_done = [ list_all[i] - list_new[i] - list_profile[i] - list_follow[i] - list_unknown[i] for i in range(len(list_all))]
        line_chart = self._get_chart_with_style()
        line_chart.title = 'Queue Page Status'
        line_chart.x_labels = self._extract_date_list(data)
        line_chart.add('Other', list_unknown)
        line_chart.add('Done', list_done)
        line_chart.add('Profile', list_profile)
        line_chart.add('Follow', list_follow)
        line_chart.add('Todo', list_new)
        line_chart.render_to_file(filename)
        return filename


    def _draw_chart_profile(self, data, filename='static/chart_profile.svg'):
        list_all = self._extract_list(data, "profile")
        list_email = self._extract_list(data, "profile_email")
        list_other = [ list_all[i] - list_email[i] for i in range(len(list_all))]
        line_chart = self._get_chart_with_style()
        line_chart.title = 'Profile Status'
        line_chart.x_labels = self._extract_date_list(data)
        line_chart.add('Other', list_other)
        line_chart.add('Email', list_email)
        line_chart.render_to_file(filename)
        return filename


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
