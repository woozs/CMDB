#!/usr/bin/env python
# -*- coding:utf-8 -*-
#version:3.5.0
#author:wuzushun
import  subprocess


def get_nic_info(nic_name):
    raw_data = subprocess.Popen("ifconfig %s "%nic_name,stdout=subprocess.PIPE,shell=True).stdout.read().decode().split('\n')
    nic_name = nic_name
    raw_ip_addr = raw_data[1].split()
    if len(raw_ip_addr) > 1:
        nic_ip_addr = raw_ip_addr[1]
        nic_netmask = raw_ip_addr[3]
        nic_broadcast = raw_ip_addr[5]
    else:
        nic_ip_addr = None
        nic_netmask = None
        nic_broadcast = None
    nic_mac_addr = raw_data[3].split()[1]
    nic_dic = {'name': nic_name,
                                'mac': nic_mac_addr,
                                'net_mask': nic_netmask,
                                'network': nic_broadcast,
                                'bonding': 'unknown',
                                'model': 'unknown',
                                'ip_address': nic_ip_addr,
                                }
    return  nic_dic



nic_name_list = subprocess.Popen(" cat /proc/net/dev | awk  -F ':' '{if (NR >=3) print $1}'",stdout=subprocess.PIPE,shell=True).stdout.read().decode().split('\n')
print(nic_name_list)
nic_list = []
for nic_name in nic_name_list:
    if "lo" not in  nic_name and nic_name != "":
        nic_dic = get_nic_info(nic_name)
        nic_list.append(nic_dic)










