#!/bin/env python
# -*- coding: utf-8 -*-
"""Test code of Nutanxi restapi v3 mini SDKs
requirements: python 3.x, requsts
"""
import sys
import json
sys.path.append('../')
from nutanix_api_utils_v3 import NutanixApiV3Client, RequestResponse


def test_get_vm_uuid_by_ip_address(nutanix_api_v3, ip_address):
    vm_uuid = nutanix_api_v3.get_vm_uuid_by_ip_address(ip_address)
    print("vm_uuid: " + vm_uuid)
    return vm_uuid


def test_get_vm_uuid_by_name(nutanix_api_v3, vm_name):
    vm_uuid = nutanix_api_v3.get_vm_uuid_by_name(vm_name)
    print("vm_uuid: " + vm_uuid)

    return vm_uuid


def test_delete_vm(nutanix_api_v3, vm_uuid):
    response = nutanix_api_v3.delete_vm(vm_uuid)
    print(response.json)

    return response.json


def test_mount_ngt(nutanix_api_v3, vm_name):
    response = nutanix_api_v3.mount_ngt_vm(vm_name,
            ssr_enabled=True, vss_snapshot_enabled=True)
    print(response.json)

    return response.json


def test_get_cluster_uuid(nutanix_api_v3, cluster_name):
    cluster_uuid = nutanix_api_v3.get_cluster_uuid(cluster_name)

    print("cluster_uuid: " + cluster_uuid)

    return cluster_uuid


def test_update_cluster_ntp(nutanix_api_v3, cluster_name, ntp_servers):
    response = nutanix_api_v3.update_cluster_ntp(cluster_name, ntp_servers)
    print(response.json)

    return response.json


if __name__ == '__main__':
    args = sys.argv
    conf_file = args[1]

    with open(conf_file, "r") as f:
        conf = json.load(f)

    prism_user = conf["user_name"]
    prism_pass = conf["password"]
    prism_addr = conf["prism_central_address"]  # v3 API endpoint

    nutanix_api_v3 = NutanixApiV3Client(prism_user, prism_pass, prism_addr)

    test_get_cluster_uuid(nutanix_api_v3, "SGDCNXRXC04")
    ntp_servers = ["0.sg.pool.ntp.org", "1.sg.pool.ntp.org"]
    test_update_cluster_ntp(nutanix_api_v3, "SGDCNXRXC04", ntp_servers)

    # test_mount_ngt(nutanix_api_v3, "RHEL84-IP63")

    # test_delete_vm(nutanix_api_v3, "7e82b365-570d-4a53-ae41-xxxxxxxxxxxxx")
    vm_uuid = test_get_vm_uuid_by_name(nutanix_api_v3, "RHEL84-IP62-2")
    nutanix_api_v3.quarantine_vm(vm_uuid, "Strict")
