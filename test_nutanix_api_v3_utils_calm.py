#!/bin/env python
# -*- coding: utf-8 -*-
"""
  Test code of Nutanxi restapi v3 wrapper
  requirements: python 3.x, requsts
"""

import sys
import time
import json
from nutanix_api_v3_utils import Nutanix_restapi_mini_sdk

    
if __name__ == '__main__':
    args = sys.argv
    conf_file = args[1]

    with open(conf_file, "r") as file:
        conf = file.read()
        conf = json.loads(conf)
    prism_addr = conf["prism_central_address"]
    prism_user = conf["user_name"]
    prism_pass = conf["password"]
    
    base_url = 'https://' + prism_addr + ':9440/api/nutanix/v3'
    nutanix_api_v3 = Nutanix_restapi_mini_sdk(prism_user, prism_pass, base_url)


    bp_name = "hm-test1"
    app_name = "hm-test1-app1"

 
    bp_uuid = nutanix_api_v3.get_bp_uuid(bp_name)
    print ("bp_uuid is: " + bp_uuid)

    app_profile_uuid = nutanix_api_v3.get_app_profile_uuid(bp_uuid)

    nutanix_api_v3.launch_bp(app_name, bp_uuid, app_profile_uuid)

