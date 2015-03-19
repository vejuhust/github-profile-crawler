#!/usr/bin/env python3
"""Web portal of watchdog for github profile crawler"""

from BaseLogger import BaseLogger
from config import config_report_interval
from flask import Flask, render_template, send_from_directory


app = Flask(__name__)


@app.route('/static/<path>')
def serve_static_files(path):
    return send_from_directory('charts', path)


@app.route('/')
def status():
    filelist = [
        "static/chart_summary.svg",
        "static/chart_crawl.svg",
        "static/chart_profile.svg",
        "static/chart_page.svg",
    ]
    return render_template('status.html', charts=filelist)


if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port=8090)
