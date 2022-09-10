#!/bin/env python
# -*- coding: utf-8 -*-

# (1) Get (virus)infected VMs from security center (by API)
# (2) Retieve VM UUID
# (3) Qurantine the VMs
import sys
import json
import slackweb
from nutanix_api_utils_v2 import Nutanix_restapi_mini_sdk


def get_infected_vm_ips():
    # ToDo
    vm_ips = ["xxx.xxx.xxx.xxx", "yyy.yyy.yyy.yyy"]
    return vm_ips


if __name__ == '__main__':
    args = sys.argv
    conf_file = args[1]

    with open(conf_file, "r") as f:
        conf = json.load(f)
    prism_addr = conf["prism_central_address"]
    prism_user = conf["user_name"]
    prism_pass = conf["password"]
    slack_webhook_url = conf["slack_webhook_url"]

    base_url = 'https://' + prism_addr + ':9440/api/nutanix/v3'
    nutanix_api_v3 = Nutanix_restapi_mini_sdk(prism_user, prism_pass, base_url)

    slack = slackweb.Slack(url=slack_webhook_url)

    # Get (virus)infected VM IPs
    vm_ips = get_infected_vm_ips()

    # Quraantine the infected VMs
    if vm_ips:
        for vm_ip in vm_ips:
            print("infected VM:" + vm_ip)
            vm_uuid = nutanix_api_v3.get_vm_uuid_by_ip_address(vm_ip)
            nutanix_api_v3.quarantine_vm(vm_uuid)

            slack.notify(text="infected VM:" + vm_ip + " has been qurantined.")
    else:
        print("no incidents")
