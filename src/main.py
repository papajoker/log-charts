#!/usr/bin/env python

import sys
import re
import os
from pathlib import Path

LOGFILENAME = "/var/log/pacman.log"

DEBUG = os.getenv('DEBUG', "0") == "1"
to_find = "upgraded"
to_find_verb = "ALPM"

if len(sys.argv) > 1:
    to_find = sys.argv[1]
if len(sys.argv) > 2:
    to_find_verb = sys.argv[2]

def parse_log(filename: str, req: str = "", verb :str = "ALPM"):
    returns = {}
    regex = re.compile(r'(\[.*\]) +(\[.*\]) +(.*)')
    #print(regex)
    with open(filename, "r") as log:
        for line in log:
            line = regex.search(line)
            if not line:
                continue
            if verb and f"[{verb}]" != line.group(2):
                continue
            if req and req not in line.group(3):
                continue
            if DEBUG:
                print(line.group(0), " => ", line.group(1), " => ", line.group(2), " => ", line.group(3))
            date = line.group(1)[1:11]
            try:
                returns[date] = returns[date] +1
            except KeyError:
                returns[date] = 1
            #print(date)
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


values = parse_log(LOGFILENAME, to_find, to_find_verb)
if DEBUG:
    sys.exit(0)
print(render(values, f"{to_find} - {to_find_verb}", "tpl/calendar.html"))

"""
script.py "transaction started" "ALPM"
script.py "starting full system upgrade" "PACMAN"
script.py "upgraded python " "ALPM"
"""