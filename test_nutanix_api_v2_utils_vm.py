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


if __name__ == '__main__':
    args = sys.argv
    conf_file = args[1]

    with open(conf_file, "r") as f:
        conf = json.load(f)

    prism_user = conf["user_name"]
    prism_pass = conf["password"]
    # prism_addr = conf["prism_central_address"]  # v3 API endpoint
    prism_addr = conf["prism_element_address"]  # v2 API endpoint

    # base_url = 'https://' + prism_central_addr + ':9440/api/nutanix/v3'
    nutanix_api = NutanixRestapiUtils(prism_user, prism_pass, prism_addr)

    test_mount_ngt(nutanix_api, "DevWorkstation-2424")
