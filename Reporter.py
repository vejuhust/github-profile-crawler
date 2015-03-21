#!/usr/bin/env python3
"""Web portal of watchdog for github profile crawler"""

from BaseLogger import BaseLogger
from config import config_report_folder, config_report_port
from flask import Flask, render_template, send_from_directory


app = Flask(__name__)


@app.route('/static/<path>')
def serve_static_files(path):
    return send_from_directory(config_report_folder, path)


@app.route('/static/favicon.ico')
def favicon():
    return send_from_directory("", "favicon.ico", mimetype='image/vnd.microsoft.icon')


@app.route('/')
def status():
    filelist = [
        "static/size_summary.svg",
        "static/size_crawl.svg",
        "static/size_profile.svg",
        "static/size_page.svg",
    ]
    return render_template("dashboard.html", title="gitcrawl dashboard - size", charts=filelist)


if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port=config_report_port)
