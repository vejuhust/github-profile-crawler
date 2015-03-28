#!/usr/bin/env python3
"""Exporter of profiles for github profile crawler"""

from BaseLogger import BaseLogger
from DatabaseAccessor import DatabaseAccessor
from contextlib import closing
from platform import node
from json import dumps
from csv import DictWriter
from time import strftime
from zipfile import ZipFile, ZIP_DEFLATED


class Exporter(BaseLogger):
    def __init__(self, log_level=None):
        BaseLogger.__init__(self, self.__class__.__name__, log_level)
        self._db_conn = DatabaseAccessor()
        self._log_info("exporter start @%s", node())


    def process(self):
        filenames = []
        data = self._db_conn.profile_read()
        self._log_info("load all profiles data from database")
        filenames.append(self._save_as_json(data))
        filenames.append(self._save_as_csv(data))
        data = self._db_conn.profile_read('email')
        self._log_info("load profiles data with email from database")
        filenames.append(self._save_as_json(data, "profile_email.json"))
        filenames.append(self._save_as_csv(data, "profile_email.csv"))
        self._archive_into_zipfile(filenames)


    def _save_as_json(self, data, filename="profile.json"):
        with open(filename, 'w') as jsonfile:
            jsonfile.write(dumps(data, sort_keys=True, indent=4))
        self._log_info("save as json file: %s", filename)
        return filename


    def _save_as_csv(self, data, filename="profile.csv"):
        fields = set()
        for item in data:
            fields = fields.union(set(item.keys()))
        with open(filename, 'w') as csvfile:
            writer = DictWriter(csvfile, extrasaction='ignore', dialect='excel', fieldnames=sorted(fields, reverse=True))
            writer.writeheader()
            for item in data:
                writer.writerow(item)
        self._log_info("save as csv file: %s", filename)
        return filename


    def _archive_into_zipfile(self, filelist):
        zipname = "profile_{}.zip".format(strftime("%Y-%m-%d_%H-%M-%S"))
        with ZipFile(zipname, 'w', ZIP_DEFLATED) as zip:
            for filename in filelist:
                zip.write(filename)
        self._log_info("archive exported files into %s", zipname)


    def close(self):
        self._db_conn.close()
        self._log_info("exporter exit")
        self._close_logger()


def main():
    with closing(Exporter()) as exporter:
        exporter.process()


if __name__ == '__main__':
    main()
