#!/usr/bin/env python
# -*- coding:utf-8 -*-
#version:3.5.0
#author:wuzushun
import sys
import platform

class InfoCollection(object):

    def collect(self):
        try:
            func = getattr(self,platform.system().lower())
            info_data =func()
            formatted_data = self.build_report_data(info_data)
            return formatted_data
        except AttributeError:
            sys.exit("不支持当前系统:%s"%platform.system())

    @staticmethod
    def linux():
        from plugins.collect_linux_info import collect
        return collect

    @staticmethod
    def windows():
        from plugins.collect_windows_info import Win32Info
        return Win32Info().collect()

    @staticmethod
    def build_report_data(data):
        pass
        return data