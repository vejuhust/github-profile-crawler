#!/usr/bin/env python3
"""Tracking database status for github profile crawler"""

from BaseLogger import BaseLogger
from DatabaseAccessor import DatabaseAccessor
from config import config_report_interval, config_report_item, config_report_status, config_report_folder, config_report_step
from contextlib import closing
from json import loads, dumps
from os import makedirs
from os.path import isfile, isdir, join
from platform import node
from pygal import StackedLine, Line
from pygal.style import RotateStyle
from time import sleep, strftime


class WatchDog(BaseLogger):
    def __init__(self, log_level=None):
        BaseLogger.__init__(self, self.__class__.__name__, log_level)
        self._db_conn = DatabaseAccessor()
        if not isdir(config_report_folder):
            makedirs(config_report_folder)
            self._log_info("create folder of charts: %s", config_report_folder)
        self._log_info("watchdog start @%s", node())


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
        data = []
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
        draw_methods = [ self._draw_chart_summary, self._draw_chart_crawl, self._draw_chart_page, self._draw_chart_profile ]
        for method in draw_methods:
            result = method(data[ -config_report_item * config_report_step + config_report_step - 1 : : config_report_step ])
            self._log_info("save chart as %s", result)


    def _get_stackedline_with_style(self):
        dark_rotate_style = RotateStyle('#9e6ffe')
        return StackedLine(fill=True, disable_xml_declaration=True, include_x_axis=False, human_readable=True, interpolate='cubic', style=dark_rotate_style)


    def _get_line_with_style(self):
        dark_rotate_style = RotateStyle('#9e6ffe')
        return Line(fill=False, disable_xml_declaration=True, include_x_axis=False, human_readable=True, interpolate='cubic', style=dark_rotate_style)


    def _extract_list(self, data, field):
        return [ item[field] for item in data ]


    def _extract_date_list(self, data):
        return [ item["date"].split()[-1][:5] for item in data ]


    def _draw_chart_summary(self, data, filename="chart_summary.svg"):
        filename = join(config_report_folder, filename)
        list_crawl = self._extract_list(data, "crawl_all")
        list_page = self._extract_list(data, "page_all")
        list_profile = self._extract_list(data, "profile")
        chart = self._get_line_with_style()
        chart.title = 'Status Summary'
        chart.x_labels = self._extract_date_list(data)
        chart.add('Profile', list_profile)
        chart.add('Page', list_page)
        chart.add('Crawl', list_crawl)
        chart.render_to_file(filename)
        return filename


    def _draw_chart_crawl(self, data, filename="chart_crawl.svg"):
        filename = join(config_report_folder, filename)
        list_all = self._extract_list(data, "crawl_all")
        list_new = self._extract_list(data, "crawl_new")
        list_fail = self._extract_list(data, "crawl_fail")
        list_done = [ list_all[i] - list_new[i] - list_fail[i] for i in range(len(list_all))]
        chart = self._get_stackedline_with_style()
        chart.title = 'Queue Crawl Status'
        chart.x_labels = self._extract_date_list(data)
        # chart.add('Failed', list_fail)
        chart.add('Done', list_done)
        chart.add('Todo', list_new)
        chart.render_to_file(filename)
        return filename


    def _draw_chart_page(self, data, filename="chart_page.svg"):
        filename = join(config_report_folder, filename)
        list_all = self._extract_list(data, "page_all")
        list_new = self._extract_list(data, "page_new")
        list_profile = self._extract_list(data, "page_profile")
        list_follow = self._extract_list(data, "page_follow")
        list_unknown = self._extract_list(data, "page_unknown")
        list_done = [ list_all[i] - list_new[i] - list_profile[i] - list_follow[i] - list_unknown[i] for i in range(len(list_all))]
        chart = self._get_stackedline_with_style()
        chart.title = 'Queue Page Status'
        chart.x_labels = self._extract_date_list(data)
        # chart.add('Other', list_unknown)
        chart.add('Done', list_done)
        chart.add('Profile', list_profile)
        chart.add('Follow', list_follow)
        chart.add('Todo', list_new)
        chart.render_to_file(filename)
        return filename


    def _draw_chart_profile(self, data, filename="chart_profile.svg"):
        filename = join(config_report_folder, filename)
        list_all = self._extract_list(data, "profile")
        list_email = self._extract_list(data, "profile_email")
        list_other = [ list_all[i] - list_email[i] for i in range(len(list_all))]
        chart = self._get_stackedline_with_style()
        chart.title = 'Profile Status'
        chart.x_labels = self._extract_date_list(data)
        chart.add('Other', list_other)
        chart.add('Email', list_email)
        chart.render_to_file(filename)
        return filename


    def close(self):
        self._db_conn.close()
        self._log_info("watchdog exit")
        self._close_logger()


def main():
    with closing(WatchDog()) as watchdog:
        while True:
            watchdog.process()
            sleep(config_report_interval)


if __name__ == '__main__':
    main()
