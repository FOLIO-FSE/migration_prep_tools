import os
from datetime import datetime


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
