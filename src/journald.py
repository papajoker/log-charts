#!/usr/bin/env python

import sys
import os
from datetime import datetime
import subprocess
from pathlib import Path

LOGFILENAME = "/var/log/pacman.log"

"""
--output-fields=LIST    Select fields to print in verbose/export/json
-o --output=STRING
                               short, short-precise,
                               short-iso, short-iso-precise, short-full,
                               short-monotonic, short-unix, verbose, export,
                               json, json-pretty, json-sse, json-seq, cat,
                               with-unit
"""

TTY = os.getenv('TTY', "0") == "1"
to_priority = 3
to_days = 120

if len(sys.argv) > 1:
    to_priority = sys.argv[1]
if len(sys.argv) > 2:
    to_days = sys.argv[2]

def get_journald(priority: int = 2, maxdays: int = 4):
    returns = {}
    cmd = f'journalctl -p{priority} --since="-{maxdays}d" --output-fields="__REALTIME_TIMESTAMP,PRIORITY" -o export --no-pager'

    process = subprocess.Popen('SYSTEMD_COLORS=xterm '+cmd, stdout=subprocess.PIPE, shell=True, text=True)
    while True:
        line = process.stdout.readline()
        if line.startswith("__REALTIME_TIMESTAMP"):
            line = line.split("=")[1]
            date_time = datetime.fromtimestamp(int(line[0:10]))
            date = date_time.strftime("%Y-%m-%d")
            try:
                returns[date] = returns[date] +1
            except KeyError:
                returns[date] = 1
        if line == "":
            break
    return returns


def array_to_js(datas: dict):
    ret = ""
    for k,v in datas.items():
        ret = ret + " "
        ret += "{"+f"day: \"{k}\", count: {v}"+"},\n"
    return f"var data = [{ret}];"

def render(datas, title, template):
    # replace line <!--DATAS-->
    # title <h3><!-- --></h3>
    svalues = array_to_js(values)
    contents = Path(template).read_text()
    contents = contents.replace("<!--DATAS-->", svalues, 1)
    return contents.replace("<h3><!-- --></h3>", f"<h4>{title}</h4>", 1)


values = get_journald(to_priority, to_days)
if TTY:
    print(f"journald- niveaux de 0 à {to_priority}\n")
    for k in values.items():
        print(f"{k[0]} {k[1]:>4}")
    print(
        "\nNiveaux:\n\t"
        "0:emergency "
        "1:alert "
        "2:critique "
        "3:error "
        "4:warning "
        "5:notice "
        "6:info "
        "7:debug "
    )
    sys.exit(0)
print(render(values, f"journald- niveaux de 0 à {to_priority}", "tpl/calendar.html"))

"""
journald.py 3 >/tmp/test.html && firefox /tmp/test.html
TTY=1 journald.py 4 12
"""
