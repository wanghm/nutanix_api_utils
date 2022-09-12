#!/bin/env python
# -*- coding: utf-8 -*-
"""Test code of Nutanxi restapi v2 mini SDKs
requirements: python 3.x, requsts
"""

import sys
import json
from nutanix_api_utils_v2 import NutanixRestapiUtils


def test_mount_ngt(nutanix_api, vm_name):
    host_uuid, vm_uuid = nutanix_api.get_vm_host_uuid(vm_name)
    print(f"vm_name={vm_name}. host_uuid={host_uuid}. vm_uuid={vm_uuid}")
    task = nutanix_api.mount_ngt_vm(host_uuid, vm_uuid)
    print(task)
    return


def test_take_snapshot_vm(nutanix_api, snapshot_name, vm_name):
    host_uuid, vm_uuid = nutanix_api.get_vm_host_uuid(vm_name)
    print(f"vm_name={vm_name}. host_uuid={host_uuid}. vm_uuid={vm_uuid}")

    task = nutanix_api.take_snapshot_vm(snapshot_name, vm_uuid)
    print(task)
    return


def test_set_power_state_vm(nutanix_api, power_state, vm_name):
    host_uuid, vm_uuid = nutanix_api.get_vm_host_uuid(vm_name)
    print(f"vm_name={vm_name}. host_uuid={host_uuid}. vm_uuid={vm_uuid}")
    if power_state == "ON":
        task = nutanix_api.power_on_vm(vm_uuid)
    else:
        task = nutanix_api.power_off_vm(host_uuid, vm_uuid)

    print(task)
    return

def test_get_pd_vms(nutanix_api, pd_name):
    vms = nutanix_api.get_pd_vms(pd_name)
    print(vms)
    return

if __name__ == '__main__':
    args = sys.argv
    conf_file = args[1]

    with open(conf_file, "r") as f:
        conf = json.load(f)

    prism_user = conf["user_name"]
    prism_pass = conf["password"]
    # prism_addr = conf["prism_central_address"]  # v3 API endpoint
    prism_addr = conf["prism_element_address"]  # v2 API endpoint

    nutanix_api = NutanixRestapiUtils(prism_user, prism_pass, prism_addr)

    # test_mount_ngt(nutanix_api, "DevWorkstation-2424")
    # test_take_snapshot_vm(nutanix_api, "snapshot_2222", "DevWorkstation-2424")
    # test_set_power_state_vm(nutanix_api, "ON", "DevWorkstation-2424")

    test_get_pd_vms(nutanix_api, "secom-test2")
