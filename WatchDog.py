#!/usr/bin/env python3
"""Tracking database status for github profile crawler"""

from BaseLogger import BaseLogger
from DatabaseAccessor import DatabaseAccessor
from bson import json_util
from config import config_report_interval, config_report_item, config_report_status, config_report_folder, config_report_step
from contextlib import closing
from datetime import datetime, timezone
from json import loads, dumps
from os import makedirs
from os.path import isfile, isdir, join
from platform import node
from pygal import StackedLine, Line
from pygal.style import RotateStyle
from time import sleep, strftime, time


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

        time_start = time()
        status = {
            "crawl_all": self._db_conn.queue_crawl_count(),
            "crawl_new": self._db_conn.queue_crawl_count("new"),
            "crawl_fail": self._db_conn.queue_crawl_count("fail"),
            "crawl_done": self._db_conn.queue_crawl_count("done"),
            "page_all": self._db_conn.queue_page_count(),
            "page_new": self._db_conn.queue_page_count("new"),
            "page_profile": self._db_conn.queue_page_count("profile"),
            "page_profile_done": self._db_conn.queue_page_count("done_profile"),
            "page_follow": self._db_conn.queue_page_count("follow"),
            "page_follow_done": self._db_conn.queue_page_count("done_follow"),
            "page_unknown": self._db_conn.queue_page_count("unknown"),
            "profile": self._db_conn.profile_count(),
            "profile_email": self._db_conn.profile_count("email"),
        }
        time_end = time()
        status["duration"] = time_end - time_start
        status["date"] = datetime.utcnow()

        data.append(status)
        self._save_data(data)
        self._log_info("save existing data, count: %d", len(data))
        self._log_info(dumps(status, sort_keys=True, indent=4, default=json_util.default))
        return data


    def _load_data(self, filename=config_report_status):
        data = []
        if isfile(filename):
            try:
                data_file = open(filename, 'r')
                content = data_file.read()
                data_file.close()
                data = loads(content, object_hook=json_util.object_hook)
            except Exception as e:
                self._log_exception("fail to load json file: %s", filename)
        else:
            self._log_warning("fail to find json file: %s", filename)
        return data


    def _save_data(self, data, filename=config_report_status):
        output_file = open(filename, 'w')
        output_file.write(dumps(data, sort_keys=True, indent=4, default=json_util.default))
        output_file.close()


    def _draw_charts_with_data(self, data):
        chart_size_methods = [ self._draw_size_chart_summary, self._draw_size_chart_crawl, self._draw_size_chart_page, self._draw_size_chart_profile ]
        chart_delta_methods = [ self._draw_delta_chart_summary, self._draw_delta_chart_page ]
        pos_start = config_report_item * config_report_step - config_report_step + 1
        if len(data) > pos_start:
            data_render = data[-pos_start::config_report_step]
        else:
            data_render = data[-config_report_item:]
        for method in chart_size_methods:
            result = method(data_render)
            self._log_info("save chart as %s", result)
        for method in chart_delta_methods:
            result = method(data[-config_report_item-1:])
            self._log_info("save chart as %s", result)


    def _get_stackedline_with_style(self):
        dark_rotate_style = RotateStyle('#9e6ffe')
        return StackedLine(fill=True, disable_xml_declaration=True, include_x_axis=False, human_readable=True, interpolate='hermite', style=dark_rotate_style)


    def _get_line_with_style(self):
        dark_rotate_style = RotateStyle('#9e6ffe')
        return Line(fill=False, disable_xml_declaration=True, include_x_axis=False, human_readable=True, interpolate='hermite', style=dark_rotate_style)


    def _extract_list(self, data, field):
        return [ item[field] for item in data ]


    def _extract_date_list(self, data_list):
        return [ data["date"].replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%H:%M") for data in data_list ]


    def _draw_size_chart_summary(self, data, filename="size_summary.svg"):
        filename = join(config_report_folder, filename)
        list_crawl = self._extract_list(data, "crawl_all")
        list_page = self._extract_list(data, "page_all")
        list_profile = self._extract_list(data, "profile")
        chart = self._get_line_with_style()
        chart.title = 'Queue Size Summary'
        chart.x_labels = self._extract_date_list(data)
        chart.add('Profile', list_profile)
        chart.add('Page', list_page)
        chart.add('Crawl', list_crawl)
        chart.render_to_file(filename)
        return filename


    def _draw_size_chart_crawl(self, data, filename="size_crawl.svg"):
        filename = join(config_report_folder, filename)
        list_all = self._extract_list(data, "crawl_all")
        list_new = self._extract_list(data, "crawl_new")
        list_fail = self._extract_list(data, "crawl_fail")
        list_done = [ list_all[i] - list_new[i] - list_fail[i] for i in range(len(list_all))]
        chart = self._get_stackedline_with_style()
        chart.title = 'Size of Queue Crawl'
        chart.x_labels = self._extract_date_list(data)
        chart.add('Done', list_done)
        chart.add('Todo', list_new)
        chart.render_to_file(filename)
        return filename


    def _draw_size_chart_page(self, data, filename="size_page.svg"):
        filename = join(config_report_folder, filename)
        list_all = self._extract_list(data, "page_all")
        list_new = self._extract_list(data, "page_new")
        list_profile = self._extract_list(data, "page_profile")
        list_follow = self._extract_list(data, "page_follow")
        list_unknown = self._extract_list(data, "page_unknown")
        list_done = [ list_all[i] - list_new[i] - list_profile[i] - list_follow[i] - list_unknown[i] for i in range(len(list_all))]
        chart = self._get_stackedline_with_style()
        chart.title = 'Size of Queue Page'
        chart.x_labels = self._extract_date_list(data)
        chart.add('Done', list_done)
        chart.add('Profile', list_profile)
        chart.add('Follow', list_follow)
        chart.add('Todo', list_new)
        chart.render_to_file(filename)
        return filename


    def _draw_size_chart_profile(self, data, filename="size_profile.svg"):
        filename = join(config_report_folder, filename)
        list_all = self._extract_list(data, "profile")
        list_email = self._extract_list(data, "profile_email")
        list_other = [ list_all[i] - list_email[i] for i in range(len(list_all))]
        chart = self._get_stackedline_with_style()
        chart.title = 'Size of Queue Profile'
        chart.x_labels = self._extract_date_list(data)
        chart.add('Other', list_other)
        chart.add('Email', list_email)
        chart.render_to_file(filename)
        return filename


    def _get_delta_list(self, data, field):
        value_list = self._extract_list(data, field)
        for i in range(len(value_list)-1, 0, -1):
            value_list[i] -= value_list[i-1]
        return value_list[1:]


    def _draw_delta_chart_summary(self, data, filename="delta_summary.svg"):
        filename = join(config_report_folder, filename)
        list_crawl = self._get_delta_list(data, "crawl_all")
        list_page = self._get_delta_list(data, "page_all")
        list_profile = self._get_delta_list(data, "profile")
        chart = self._get_line_with_style()
        chart.title = 'Queue Size Increase Summary'
        chart.x_labels = self._extract_date_list(data[1:])
        chart.add('Profile', list_profile)
        chart.add('Page', list_page)
        chart.add('Crawl', list_crawl)
        chart.render_to_file(filename)
        return filename


    def _draw_delta_chart_page(self, data, filename="delta_page.svg"):
        filename = join(config_report_folder, filename)
        list_all = self._get_delta_list(data, "page_all")
        list_fail = self._get_delta_list(data, "crawl_fail")
        list_follow = self._get_delta_list(data, "page_follow_done")
        list_profile = self._get_delta_list(data, "page_profile_done")
        chart = self._get_line_with_style()
        chart.title = 'Queue Page Size Increase'
        chart.x_labels = self._extract_date_list(data[1:])
        chart.add('Profile', list_profile)
        chart.add('Follow', list_follow)
        chart.add('Failed Crawl', list_fail)
        chart.add('New Crawl', list_all)
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
