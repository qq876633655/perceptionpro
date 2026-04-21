# -*- coding: utf-8 -*-
"""
Time:2021/6/29 13:28
Author:YANGLEI
File:log.py
"""

import os
import time
import logging


class Log:
    def __init__(self):
        """
        日志记录
        """
        self.log_path = os.path.join(os.path.dirname(__file__), '../logs')
        self.log_name = os.path.join(self.log_path, f"{time.strftime('%Y-%m-%d')}.log")
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # 创建一个 handler，用于写入日志文件
        fh = logging.FileHandler(self.log_name, 'a', encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)

        # 再创建一个 handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)

        # 给 logger 添加 handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def debug(self, message, *args, **kwargs):
        """
        记录调试信息
        :param message:
        :return:
        """
        self.logger.debug(message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        """
        记录事件信息
        :param message:
        :return:
        """
        self.logger.info(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        """
        记录警告信息
        :param message:
        :return:
        """
        self.logger.warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        """
        记录错误信息，程序仍可运行
        :param message: 错误消息
        """
        self.logger.error(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        """
        记录严重信息，程序无法继续运行
        :param message: 错误消息
        """
        self.logger.critical(message, *args, **kwargs)


my_log = Log()

if __name__ == '__main__':
    try:
        result = 1 / 0
    except Exception as e:
        # 方式1：使用专门的异常方法
        # 方式2：在error方法中传入exc_info=True
        my_log.error("数学运算错误", exc_info=True)
    # my_log.debug('test debug')
    # my_log.info('test info')
    # my_log.warning('test warning')
    # my_log.error('test error')
    # my_log.critical('test critical')
