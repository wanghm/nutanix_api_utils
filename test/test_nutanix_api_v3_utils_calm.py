#!/bin/env python
"""Test code of Nutanxi restapi v3 utility
requirements: python 3.x, requsts
"""
import sys
sys.path.append('../')
from nutanix_api_utils_v2 import NutanixRestapiUtils
import json


if __name__ == '__main__':
    args = sys.argv
    conf_file = args[1]

    with open(conf_file, "r") as f:
        conf = json.load(f)

    prism_user = conf["user_name"]
    prism_pass = conf["password"]
    prism_addr = conf["prism_element_address"]  # v2 API endpoint

    nutanix_api = NutanixRestapiUtils(prism_user, prism_pass, prism_addr)

    bp_name = "test1"
    app_name = "test1-app1"
    bp_uuid = nutanix_api.get_bp_uuid(bp_name)
    print("bp_uuid is: " + bp_uuid)

    app_profile_uuid = nutanix_api.get_app_profile_uuid(bp_uuid)

    nutanix_api.launch_bp(app_name, bp_uuid, app_profile_uuid)
