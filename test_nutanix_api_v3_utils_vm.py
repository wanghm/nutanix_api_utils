#!/bin/env python
# -*- coding: utf-8 -*-
"""Test code of Nutanxi restapi v3 mini SDKs
requirements: python 3.x, requsts
"""

import sys
import time
import json
from nutanix_api_v3_utils import Nutanix_restapi_mini_sdk

def test_get_vm_uuid_by_ip_address(nutanix_api_v3, ip_address):
    vm_uuid = nutanix_api_v3.get_vm_uuid_by_ip_address(ip_address)
    print("vm_uuid: " + vm_uuid)
    return vm_uuid
    
def test_get_vm_uuid_by_name(nutanix_api_v3, vm_name):
    vm_uuid = nutanix_api_v3.get_vm_uuid_by_name(vm_name)
    print("vm_uuid: " + vm_uuid)
    return vm_uuid

def test_delete_vm(nutanix_api_v3, vm_uuid):
    task = nutanix_api_v3.delete_vm(vm_uuid)
    print("response:")
    print(task)
    return task

def test_mount_ngt(nutanix_api_v3, vm_name):
    task = nutanix_api_v3.mount_ngt_vm(vm_name)
    print(task)
    return
    
if __name__ == '__main__':
    args = sys.argv
    conf_file = args[1]

    with open(conf_file, "r") as f:
        conf = json.load(f)
        
    prism_addr = conf["prism_central_address"]
    prism_user = conf["user_name"]
    prism_pass = conf["password"]
    
    base_url = 'https://' + prism_addr + ':9440/api/nutanix/v3'
    nutanix_api_v3 = Nutanix_restapi_mini_sdk(prism_user, prism_pass, base_url)

    test_mount_ngt (nutanix_api_v3, "DevWorkstation-2424")
    
    #test_delete_vm(nutanix_api_v3, "7e82b365-570d-4a53-ae41-58f8d1269699")
    #vm_uuid = test_get_vm_uuid_by_name(nutanix_api_v3,"hm-FILER")
    #nutanix_api_v3.unquarantine_vm(vm_uuid)