# -*- coding: utf-8 -*-
# @createTime    : 2020/5/11 17:53
# @author  : Huanglg
# @fileName: Logger.py
# @email: luguang.huang@mabotech.com
# _*_ coding: utf-8 _*_
import logging
import config
import os
import time

project_path = 'logs'


class Logger(object):
    def __init__(self):
        # 指定保存日志的文件路径，日志级别，以及调用文件
        # 将日志存入到指定的文件中

        current_time = time.strftime('%Y%m%d%H%M',
                                     time.localtime(time.time()))  # 返回当前时间
        current_path = os.path.dirname(os.path.abspath(project_path))  # 返回当前目录
        path1 = current_path.split(project_path)  # 指定分隔符对字符串进行切片
        path2 = path1[0]
        path3 = ''
        new_name = path3.join(path2) + '/logs/'  # 在该路径下新建下级目录

        dir_time = time.strftime('%Y%m%d', time.localtime(time.time()))  # 返回当前时间的年月日作为目录名称
        is_exists = os.path.exists(new_name + dir_time)  # 判断该目录是否存在
        if not is_exists:
            os.makedirs(new_name + dir_time)

        else:
            # 如果目录存在则不创建，并提示目录已存在
            pass
            # print(new_name + "目录 %s 已存在" % dir_time)

        try:
            # 创建一个logger(初始化logger)
            self.log = logging.getLogger()
            self.log.setLevel(logging.DEBUG)

            # 创建一个handler，用于写入日志文件

            # 如果case组织结构式 /testsuit/featuremodel/xxx.py ， 那么得到的相对路径的父路径就是项目根目录
            log_name = new_name + dir_time + '/' + current_time + '.log'  # 定义日志文件的路径以及名称

            fh = logging.FileHandler(log_name)
            fh.setLevel(config.LOG_LEVEL)

            # 再创建一个handler，用于输出到控制台
            ch = logging.StreamHandler()
            ch.setLevel(config.LOG_LEVEL)

            # 定义handler的输出格式
            formatter = logging.Formatter('[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)

            # 给logger添加handler
            self.log.addHandler(fh)
            self.log.addHandler(ch)
        except Exception as e:
            print("输出日志失败！ %s" % e)

    # 日志接口，用户只需调用这里的接口即可，这里只定位了INFO, WARNING, ERROR三个级别的日志，可根据需要定义更多接口

    def info(cls, msg):
        cls.log.info(msg)
        return

    def warning(cls, msg):
        cls.log.warning(msg)
        return

    def error(cls, msg):
        cls.log.error(msg)
        return


if __name__ == '__main__':
    logger = Logger()
    logger.info('This is info')
    logger.warning('This is warning')
    logger.error('This is error')
