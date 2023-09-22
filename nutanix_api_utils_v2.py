#!/bin/env python
"""nutanix_api_utils_v2.py
~~~~~~~~~~~~~~~~~~~~~~

Utility(Wrapper) class for Nutanix Rest API v2

(c) 2022 Huimin Wang
"""
import json
import requests
import urllib3
import datetime
import time

class NutanixRestapiUtils:
    def __init__(self, username, password, prism_addr):
        self.base_url = 'https://' + prism_addr + ':9440/api/nutanix/v2.0'
        urllib3.disable_warnings()

        self.s = requests.Session()
        self.s.auth = (username, password)
        self.s.headers.update(
            {'Content-Type': 'application/json; charset=utf-8'})

    def activate_pd(self, pd_name):
        """Activate protection domain (Unplanned failover)
        """
        payload = {
            "name": pd_name
        }
        api_url = self.base_url + f"/protection_domains/{pd_name}/activate"
        response = self.s.post(
            api_url, json.dumps(payload), verify=False).json()

        return response

    def get_pd_vms(self, pd_name):
        """get VM list in the PD
        """
        api_url = self.base_url + f"/protection_domains/{pd_name}"
        response = self.s.get(api_url, verify=False).json()

        vms = response.get("vms")
        print(vms)

        return vms

    def get_pd_status(self, pd_name):
        api_url = self.base_url + f"/protection_domains/?names={pd_name}"
        response = self.s.get(api_url, verify=False).json()

        return response

    def power_on_vm(self, vm_uuid):
        payload = {
            "transition": "ON",
            "uuid": vm_uuid
        }
        api_url = self.base_url + f"/vms/{vm_uuid}/set_power_state/"
        task = self.s.post(
            api_url, json.dumps(payload), verify=False).json()

        return task

    def power_off_vm(self, host_uuid, vm_uuid):
        payload = {
            "host_uuid": host_uuid,
            "transition": "OFF",
            "uuid": vm_uuid
        }
        api_url = self.base_url + f"/vms/{vm_uuid}/set_power_state/"
        task = self.s.post(
            api_url, json.dumps(payload), verify=False).json()

        return task

    def get_all_vm_spec(self, vm_name):
        api_url = self.base_url + "/vms"
        response = self.s.get(api_url, verify=False)

        d = json.loads(response.text)

        vms = d["entities"]

        return vms

    def get_vm_spec(self, vm_name):

        vms = self.get_all_vm_spec(self)

        index = 0
        vm_spec = ""

        for vm in vms:
            if vm_name == vm.get("name"):
                vm_uuid = vm.get("uuid")
                host_uuid = vm.get("host_uuid")
                print(f"vm_uuid={vm_uuid}, host_uuid={host_uuid}")
                vm_spec = vms[index]
                break
            index += 1

        print(vm_spec)

        return vm_spec

    def get_vm_host_uuid(self, vm_name):
        vm_spec = self.get_vm_spec(vm_name)

        # host_uuid is None if VM is Powered off
        host_uuid = vm_spec.get("host_uuid")
        vm_uuid = vm_spec.get("uuid")

        return host_uuid, vm_uuid

    def mount_ngt_vm(self, host_uuid, vm_uuid):
        """this doesn't work
        payload = {
            "applications": {
                "file_level_restore": "true",
                "vss_snapshot": "true"
            },
            "operation": "MOUNT",
            "override_guest": "true",
            "uuid": vm_uuid
        }
        """

        payload = {
            "operation": "MOUNT",
            "override_guest": "true",
            "uuid": vm_uuid
        }
        api_url = self.base_url + f"/vms/{vm_uuid}/manage_vm_guest_tools"

        task = self.s.post(
            api_url, json.dumps(payload), verify=False).json()

        return task

    def take_snapshot_vm(self, snapshot_name, vm_uuid):
        payload = {
                "snapshot_specs": [
                    {
                        "snapshot_name": snapshot_name,
                        "vm_uuid": vm_uuid
                    }
                ]
        }
        api_url = self.base_url + "/snapshots"
        # task = self.s.post(api_url, payload, verify=False)
        task = self.s.post(
            api_url, json.dumps(payload), verify=False).json()

        print("task info returned in take_snapshot_vm:")
        print(task)

        return task
    
    def generate_image_config(img_name, img_annotation, dev_bus, dev_index, vmdisk_uuid):
        return {
            'annotation': img_annotation,
            'image_type': 'DISK_IMAGE',
            'name': img_name,
            'vm_disk_clone_spec': {
                'disk_address': {
                    'device_bus': dev_bus,
                    'device_index': dev_index,
                    'vmdisk_uuid': vmdisk_uuid
                }
            }
        }

    def create_image_from_vm_disks(self, vm_name, img_name):
        """Create disk images from VM

        """
        src_vm = self.get_vm_spec(vm_name)
        img_vm_name = src_vm['name']
        # img_vm_uuid = src_vm['uuid']

        img_timestamp = datetime.datetime.now()
        img_timestamp_str = img_timestamp.strftime('%Y%m%d%H%M%S')
        img_timestamp_annotation = img_timestamp.strftime('%Y/%m/%d %H:%M:%S')
    
        for vdisk in src_vm['vm_disk_info']:
            if vdisk['disk_address']['device_bus'] == 'scsi':
                img_disk_label = vdisk['disk_address']['disk_label']
                img_disk_bus = vdisk['disk_address']['device_bus']
                img_disk_index = vdisk['disk_address']['device_index']
                img_vmdisk_uuid = vdisk['disk_address']['vmdisk_uuid']

                if img_name == "":
                    img_name = '_'.join([img_vm_name, img_disk_label, img_timestamp_str])
            
                image_config = self.generate_image_config(
                    img_name, img_timestamp_annotation, img_disk_bus, img_disk_index, img_vmdisk_uuid)
            
                api_url = self.base_url + "/images"
                task = self.s.post(
                    api_url, json.dumps(image_config), verify=False).json()

                print("task info returned in take_snapshot_vm:")
                print(task)
        return
    
