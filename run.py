# -*- coding: utf-8 -*-
# @createTime    : 2020/5/20 9:34
# @author  : Huanglg
# @fileName: file_change.py
# @email: luguang.huang@mabotech.com
import time

from watchdog.observers import Observer
from watchdog.events import *

import config
from parse_pdf import parse_pdf
import os

import constants
from utils.Logger import Logger

logger = Logger()

class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_moved(self, event):
        if event.is_directory:
            print("directory moved from {0} to {1}".format(event.src_path,event.dest_path))
        else:
            print("file moved from {0} to {1}".format(event.src_path,event.dest_path))

    def on_created(self, event):
        # 检测到新文件创建开始识别PDF
        if event.is_directory:
            print("directory created:{0}".format(event.src_path))
        else:
            pdf_path = self.convert_path(event.src_path)
            logger.info("file created:{0}".format(event.src_path))
            parse_pdf(pdf_path)

    def on_deleted(self, event):
        if event.is_directory:
            print("directory deleted:{0}".format(event.src_path))
        else:
            print("file deleted:{0}".format(event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            print("directory modified:{0}".format(event.src_path))
        else:
            print("file modified:{0}".format(event.src_path))

    def convert_path(self, path: str) -> str:
        seps = r'\/'
        sep_other = seps.replace(os.sep, '')
        return path.replace(sep_other, os.sep) if sep_other in path else path

if __name__ == "__main__":
    monitor_dir = config.MONITOR_FOLDER
    observer = Observer()
    event_handler = FileEventHandler()
    observer.schedule(event_handler, monitor_dir, True)
    observer.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
