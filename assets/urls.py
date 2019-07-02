#!/usr/bin/env python
# -*- coding:utf-8 -*-
#version:3.5.0
#author:wuzushun
from django.urls import path
from assets import views

app_name = 'assets'

urlpatterns = [
    path('report', views.report, name='report'),
]

