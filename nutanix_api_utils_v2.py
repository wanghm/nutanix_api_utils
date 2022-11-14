#!/bin/env python
"""nutanix_api_utils_v2.py
~~~~~~~~~~~~~~~~~~~~~~

Utility(Wrapper) class for Nutanix Rest API v2

(c) 2022 Huimin Wang
"""
import json
import requests
import urllib3


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
