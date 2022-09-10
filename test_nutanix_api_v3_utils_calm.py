#!/bin/env python
# -*- coding: utf-8 -*-
"""Test code of Nutanxi restapi v3 mini SDKs
requirements: python 3.x, requsts
"""
import sys
import json
from nutanix_api_utils_v2 import NutanixRestapiUtils


if __name__ == '__main__':
    args = sys.argv
    conf_file = args[1]

    with open(conf_file, "r") as f:
        conf = json.load(f)

    prism_addr = conf["prism_central_address"]
    prism_user = conf["user_name"]
    prism_pass = conf["password"]

    base_url = 'https://' + prism_addr + ':9440/api/nutanix/v3'
    nutanix_api_v3 = NutanixRestapiUtils(prism_user, prism_pass, base_url)

    bp_name = "hm-test1"
    app_name = "hm-test1-app1"
    bp_uuid = nutanix_api_v3.get_bp_uuid(bp_name)
    print("bp_uuid is: " + bp_uuid)

    app_profile_uuid = nutanix_api_v3.get_app_profile_uuid(bp_uuid)

    nutanix_api_v3.launch_bp(app_name, bp_uuid, app_profile_uuid)
