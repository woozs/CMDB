#!/usr/bin/env python
# -*- coding:utf-8 -*-
#version:3.5.0
#author:wuzushun
from core import info_collection
from conf import settings

import json
import time
import urllib.parse
import urllib.request


class ArgvHandler(object):

    def __init__(self,args):
        self.args = args
        self.parse_args()

    def parse_args(self):
        """分析参数"""
        if len(self.args) > 1 and hasattr(self,self.args[1]):
            func = getattr(self,self.args[1])
            func()
        else:
            self.help_meg()

    @staticmethod
    def help_meg():
        """帮助说明"""
        msg = """
        参数名                 功能
        conllect_data         测试收集硬件的功能
        report_data           收集硬件信息并且上报    
        """
        print(msg)
    @staticmethod
    def collect_data():
        """收集硬件信息"""
        info = info_collection.InfoCollection()
        asset_data =  info.collect


    @staticmethod
    def report_data():
        """收集硬件信息并且上报"""
        info = info_collection.InfoCollection()
        asset_data = info.collect()
        print(asset_data)

        data = {"asset_data":json.dumps(asset_data)}
        url = "http://%s:%s%s"%(settings.Params['server'],settings.Params['port'],settings.Params['url'])
        print("正在上传数据到【%s】......."%url)
        try:
            data_encode = urllib.parse.urlencode(data).encode()
            response =  urllib.request.urlopen(url=url,data=data_encode,timeout=settings.Params['request_timeout'])
            print("发送完毕")
            message = response.read().decode()
            print("返回结果:%s"%message)
        except Exception as e:
            message = "发送失败" + "失败原因 ：{}".format(e)
            print("发送失败原因：%s"%e)
        with open(settings.PATH,'ab') as f:
            log = "发送时间：%s\t服务器地址：%s\t 返回结果 :%s\n"%(time.strftime('%Y-%m-%d %H:%M:%S'),url,message)
            f.write(log.encode())
            print("日志记录成功")
