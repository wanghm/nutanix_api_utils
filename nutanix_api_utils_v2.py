#!/bin/env python
# -*- coding: utf-8 -*-

"""Utility class of Nutanix Rest API v2
(Work In Process)
requirements: python 3.x, requsts
"""
import json
import requests
import urllib3


# Utils class of API v2
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

        Args:
            pd_name (Str): Protection Domain NAme

        Returns:
            (Bol) True: Success| false: Failed
        """

        payload = {
            "name": pd_name
        }
        api_url = self.base_url + f"/protection_domains/{pd_name}/activate"
        response = self.s.post(
            api_url, json.dumps(payload), verify=False).json()

        return response

    def get_pd_status(self, pd_name):
        api_url = self.base_url + f"/protection_domains/?names={pd_name}"
        response = self.s.get(api_url, verify=False).json()
        
        return response

    def get_vm_uuid(self, vm_name):
        # todo
        vm_uuid = ""
        return vm_uuid
    
    def power_on_vm(self, host_uuid, vm_uuid):
        payload = {
            "host_uuid": host_uuid,
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

    def get_vm_host_uuid(self, vm_name):
        # todo
        host_uuid = ""
        vm_uuid = ""
        return host_uuid, vm_uuid
    
    def mount_ngt_vm(self, host_uuid, vm_uuid):
        payload = {
            "operation": "MOUNT",
            "override_guest": "true",
            "uuid": vm_uuid
        }
        api_url = self.base_url + f"/vms/{vm_uuid}/manage_vm_guest_tools"
        task = self.s.post(
            api_url, json.dumps(payload), verify=False).json()

        return task
