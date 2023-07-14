import os
import json
from datetime import datetime


def open_file(fn, f_type="txt"):
    with open(fn, mode='r', encoding='utf-8') as fp:
        if f_type == "json":
            obj = json.load(fp)
        else:
            obj = [
                line.replace("\n", "").strip() for
                line in
                fp.readlines()
                ]
        return obj


def get_timestamp():
    now = datetime.now()
    now_str = datetime.strftime(now, "%Y%m%d-%H%M%S")
    return now_str


def check_folder(p):
    cwd = os.getcwd()
    fp = os.path.join(cwd, p)
    if not os.path.exists(fp):
        os.makedirs(fp)
    return p
