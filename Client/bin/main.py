#!/usr/bin/env python
# -*- coding:utf-8 -*-
#version:3.5.0
#author:wuzushun
import os
import sys

BASE_DIR = os.path.dirname(os.getcwd())
sys.path.append(BASE_DIR)


from core import handler

if __name__ == '__main__':
    handler.ArgvHandler(sys.argv)

