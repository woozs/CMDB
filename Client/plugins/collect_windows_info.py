#!/usr/bin/env python
# -*- coding:utf-8 -*-
#version:3.5.0
#author:wuzushun
import platform
import win32com
import win32com.client
import wmi


class Win32Info(object):

    def __init__(self):
        self.wmi_obj = wmi.WMI()
        self.wmi_service_obj = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        self.wmi_service_connector = self.wmi_service_obj.ConnectServer('.',"root\cimv2")

    def collect(self):
        data = {
            'os_type' : platform.system(),
            'os_release' : '%s %s %s'%(platform.release(),platform.architecture()[0],platform.version()),
            'os_distribution':'Microsoft',
            'asset_type': 'server'

        }
        data.update(self.get_cpu_info())
        data.update(self.get_ram_info())
        data.update(self.get_motherboard_info())
        data.update(self.get_disk_info())
        data.update(self.get_nic_info())
        return data

    def get_cpu_info(self):
        data = {}
        cpu_lists = self.wmi_obj.Win32_Processor()
        cpu_core_count = 0
        for cpu in cpu_lists:
            cpu_core_count += cpu.NumberOfCores
        cpu_model = cpu_lists[0].name
        data["cpu_count"] = len(cpu_lists)  # CPU个数
        data["cpu_model"] = cpu_model
        data["cpu_core_count"] = cpu_core_count

        return data

    def get_ram_info(self):
        data = []
        ram_collections = self.wmi_service_connector.ExecQuery("Select * from Win32_PhysicalMemory")
        for ram in ram_collections:
            ram_size = int(int(ram.Capacity)/(1024**3))
            item_data = {
                "slot": ram.DeviceLocator.strip(),
                "capacity": ram_size,
                "model": ram.Caption,
                "manufacturer": ram.Manufacturer,
                "sn": ram.SerialNumber,
            }
            data.append(item_data)

        return {"ram": data}

    def get_motherboard_info(self):
        """
        获取主板信息
        :return:
        """
        computer_info = self.wmi_obj.Win32_ComputerSystem()[0]
        system_info = self.wmi_obj.Win32_OperatingSystem()[0]
        data = {}
        data['manufacturer'] = computer_info.Manufacturer
        data['model'] = computer_info.Model
        data['wake_up_type'] = computer_info.WakeUpType
        data['sn'] = system_info.SerialNumber
        return data

    def get_disk_info(self):
        """
        硬盘信息
        :return:
        """
        data = []
        for disk in self.wmi_obj.Win32_DiskDrive():  # 每块硬盘都要获取相应信息
            disk_data = {}
            interface_choices = ["SAS", "SCSI", "SATA", "SSD"]
            for interface in interface_choices:
                if interface in disk.Model:
                    disk_data['interface_type'] = interface
                    break
            else:
                disk_data['interface_type'] = 'unknown'

            disk_data['slot'] = disk.Index
            disk_data['sn'] = disk.SerialNumber
            disk_data['model'] = disk.Model
            disk_data['manufacturer'] = disk.Manufacturer
            disk_data['capacity'] = int(int(disk.Size) / (1024 ** 3))
            data.append(disk_data)

        return {'physical_disk_driver': data}

    def get_nic_info(self):
        """
        网卡信息
        :return:
        """
        data = []
        for nic in self.wmi_obj.Win32_NetworkAdapterConfiguration():
            if nic.MACAddress is not None:
                nic_data = {}
                nic_data['mac'] = nic.MACAddress
                nic_data['model'] = nic.Caption
                nic_data['name'] = nic.Index
                if nic.IPAddress is not None:
                    nic_data['ip_address'] = nic.IPAddress[0]
                    nic_data['net_mask'] = nic.IPSubnet
                else:
                    nic_data['ip_address'] = ''
                    nic_data['net_mask'] = ''
                data.append(nic_data)

        return {'nic': data}


if __name__ == "__main__":
    # 测试代码
    data = Win32Info().collect()
    for key in data:
        print(key, ":", data[key])