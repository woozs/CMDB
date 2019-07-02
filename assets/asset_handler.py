#!/usr/bin/env python
# -*- coding:utf-8 -*-
#version:3.5.0
#author:wuzushun

import json
from assets import models

class NewAsset(object):
    def __init__(self,request,data):
        self.request = request
        self.data = data

    def add_to_new_assets_zone(self):
        defaults = {
            'data': json.dumps(self.data),
            'asset_type': self.data.get('asset_type'),
            'manufacturer': self.data.get('manufacturer'),
            'model': self.data.get('model'),
            'ram_size': self.data.get('ram_size'),
            'cpu_model': self.data.get('cpu_model'),
            'cpu_count': self.data.get('cpu_count'),
            'cpu_core_count': self.data.get('cpu_core_count'),
            'os_distribution': self.data.get('os_distribution'),
            'os_release': self.data.get('os_release'),
            'os_type': self.data.get('os_type'),

        }
        print(defaults)
        models.NewAssetApprovalZone.objects.update_or_create(sn=self.data['sn'],defaults=defaults)
        return '资产已经加入或更新待审批区！'


def log(log_type,msg=None,asset=None,new_asset=None,request=None):
    event = models.EventLog()
    if log_type == "upline":
        event.name  = "%s<%s>:上线"%(asset.name,asset.sn)
        event.asset = asset
        event.detail = "资产上线成功"
        event.user =request.user
    elif log_type == "approve_failed":
        event.name = "%s<%s>:审批失败" % (new_asset.asset_type,new_asset.sn)
        event.asset = new_asset
        event.detail = "审批失败!\n%s"%msg
        event.user = request.user
    event.save()

class ApproveAsset:

    def __init__(self,request,asset_id):
        self.request = request
        self.new_asset = models.NewAssetApprovalZone.objects.get(id=asset_id)
        self.data = json.loads(self.new_asset.data)

    def asset_upline(self):
        func = getattr(self,"_%s_upline"%self.new_asset.asset_type)
        ret = func()
        return ret

    def _server_upline(self):
        asset =  self._crate_asset()
        try:
            self._create_manufacturer(asset)
            self._create_server(asset)
            self._create_CPU(asset)
            self._create_RAM(asset)
            self._create_disk(asset)
            self._create_nic(asset)
            self._delete_original_assets()
        except Exception as e:
            asset.delete()
            log('approve_failed', msg=e, new_asset=self.new_asset, request=self.request)
            print(e)
            return False
        else:
            # 添加日志
            log("upline", asset=asset, request=self.request)
            print("新服务器上线!")
            return True




    def _crate_asset(self):
        asset = models.Asset.objects.create(asset_type=self.new_asset.asset_type,
                                            name="%s:%s"%(self.new_asset.asset_type,self.new_asset.sn),
                                            sn=self.new_asset.sn,
                                            approved_by=self.request.user,)
        return asset

    def _create_manufacturer(self,asset):
        m = self.new_asset.manufacturer
        if m:
            manufacturer_obj, _ = models.Manufacturer.objects.get_or_create(name=m)
            asset.manufacturer = manufacturer_obj
            asset.save()

    def _create_server(self,asset):
        models.Server.objects.create(asset=asset,
                                     model=self.new_asset.model,
                                     os_type=self.new_asset.os_type,
                                     os_distribution=self.new_asset.os_distribution,
                                     os_release=self.new_asset.os_release,)

    def _create_CPU(self,asset):
        cpu = models.CPU.objects.create(asset=asset)
        cpu.cpu_model = self.new_asset.cpu_model
        cpu.cpu_core_count = self.new_asset.cpu_core_count
        cpu.cpu_count = self.new_asset.cpu_count
        cpu.save()

    def _create_RAM(self,asset):
        ram_list = self.data.get('ram')
        if not ram_list:
            return
        for ram_dict in ram_list:
            if not ram_dict.get('slot'):
                raise ValueError("未知的插槽")
            ram = models.RAM()
            ram.asset = asset
            ram.slot = ram_dict.get('slot')
            ram.sn = ram_dict.get('sn')
            ram.model = ram_dict.get('model')
            ram.manufacturer = ram_dict.get('manufacturer')
            ram.capacity = ram_dict.get('capacity', 0)
            ram.save()

    def _create_disk(self, asset):
        """
        存储设备种类多，还有Raid情况，需要根据实际情况具体解决。
        这里只以简单的SATA硬盘为例子。可能有多块硬盘。
        :param asset:
        :return:
        """
        disk_list = self.data.get('physical_disk_driver')
        if not disk_list:  # 一条硬盘数据都没有
            return
        for disk_dict in disk_list:
            if not disk_dict.get('sn'):
                raise ValueError("未知sn的硬盘！")  # 根据sn确定具体某块硬盘。
            disk = models.Disk()
            disk.asset = asset
            disk.sn = disk_dict.get('sn')
            disk.model = disk_dict.get('model')
            disk.manufacturer = disk_dict.get('manufacturer'),
            disk.slot = disk_dict.get('slot')
            disk.capacity = disk_dict.get('capacity', 0)
            iface = disk_dict.get('interface_type')
            if iface in ['SATA', 'SAS', 'SCSI', 'SSD', 'unknown']:
                disk.interface_type = iface

            disk.save()

    def _create_nic(self, asset):
        """
        创建网卡。可能有多个网卡，甚至虚拟网卡。
        :param asset:
        :return:
        """
        nic_list = self.data.get("nic")
        if not nic_list:
            return

        for nic_dict in nic_list:
            if not nic_dict.get('mac'):
                raise ValueError("网卡缺少mac地址！")
            if not nic_dict.get('model'):
                raise ValueError("网卡型号未知！")

            nic = models.NIC()
            nic.asset = asset
            nic.name = nic_dict.get('name')
            nic.model = nic_dict.get('model')
            nic.mac = nic_dict.get('mac')
            nic.ip_address = nic_dict.get('ip_address')
            if nic_dict.get('net_mask'):
                if len(nic_dict.get('net_mask')) > 0:
                    nic.net_mask = nic_dict.get('net_mask')[0]
            nic.save()

    def _delete_original_assets(self):
        """
        这里的逻辑是已经审批上线的资产，就从待审批区删除。
        也可以设置为修改成已审批状态但不删除，只是在管理界面特别处理，不让再次审批，灰色显示。
        不过这样可能导致待审批区越来越大。
        :return:
        """
        self.new_asset.delete()