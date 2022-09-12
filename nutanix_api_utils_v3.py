#!/bin/env python
# -*- coding: utf-8 -*-

"""nutanix_api_utils_v2.py
~~~~~~~~~~~~~~~~~~~~~~

Utility(Wrapper) class for Nutanix Rest API v2

? 2022 Huimin Wang
"""
import json
import requests
import urllib3


class NutanixRestapiUtils:
    def __init__(self, username, password, prism_addr):
        self.base_url = 'https://' + prism_addr + ':9440/api/nutanix/v3'

        urllib3.disable_warnings()

        self.s = requests.Session()
        self.s.auth = (username, password)
        self.s.headers.update(
            {'Content-Type': 'application/json; charset=utf-8'})

# region VM related SDKs
    def get_vm_uuid(self, payload):
        """Get VM UUID by patload
        """
        api_url = self.base_url + '/vms/list'
        vms_spec = self.s.post(
            api_url, json.dumps(payload), verify=False).json()
        print("vms_spec ------")
        print(json.dumps(vms_spec, indent=2))

        vm_uuid = ''
        for vm in vms_spec['entities']:
            if vm['metadata']:  # sometimes this value will be '{}'
                vm_uuid = vm['metadata']['uuid']
                break  # return the 1st one
        return vm_uuid

    def get_vm_uuid_by_name(self, vm_name):
        """ Get VM UUID by VM Name
        Note: unsupported filter is in use!
        """
        payload = {
            "filter": "vm_name==.*" + vm_name + ".*",
            "kind": "vm"
        }
        return self.get_vm_uuid(payload)

    def get_vm_uuid_by_ip_address(self, ip_address):
        """ Get VM UUID by VM IP address
        Note: unsupported filter is in use!
        """
        payload = {
            "filter": "ip_addresses==" + ip_address,
            "kind": "vm"
        }
        return self.get_vm_uuid(payload)

    def get_vm_spec(self, vm_uuid):
        """ Get VM spec(Json) by VM UUID
        """
        api_url = self.base_url + '/vms/' + vm_uuid
        vm_spec = self.s.get(api_url, verify=False).json()
        del vm_spec['status']
        # print(json.dumps(vm_spec, indent=2))

        return vm_spec

    def update_vm(self, vm_uuid, vm_spec_json):
        """ Get VM UUID by VM spec(Json)
        """
        api_url = self.base_url + '/vms/' + vm_uuid
        task = self.s.put(
            api_url, data=json.dumps(vm_spec_json), verify=False).json()
        return task

    def delete_vm(self, vm_uuid):
        """ Delete VM by VM UUID
        """
        api_url = self.base_url + '/vms/' + vm_uuid
        task = self.s.delete(api_url, verify=False).json()
        return task

    def quarantine_vm(self, vm_uuid, quarantine_method):
        """ Quarentine VM by VM UUID
        """
        vm_spec = self.get_vm_spec(vm_uuid)
        if quarantine_method not in ["Default", "Strict", "Forensics"]:
            raise Exception("Quarantine Method:" +
                            quarantine_method +
                            " is not valid. Valid values: Strict, Forensics")
        vm_spec['metadata']['categories']['Quarantine'] = quarantine_method

        # vm_spec['metadata']['categories']['Quarantine'] = 'Default'
        # vm_spec['metadata']['categories']['Quarantine'] = 'Strict'
        # vm_spec['metadata']['categories']['Quarantine'] = 'Forensics'
        del vm_spec['metadata']['last_update_time']
        print(json.dumps(vm_spec, indent=2))

        task = self.update_vm(vm_uuid, vm_spec)
        return task

    def unquarantine_vm(self, vm_uuid):
        """ Unquarentine VM by VM UUID
        """
        vm_spec = self.get_vm_spec(vm_uuid)
        del vm_spec['metadata']['categories']['Quarantine']
        del vm_spec['metadata']['last_update_time']
        print(json.dumps(vm_spec, indent=2))

        task = self.update_vm(vm_uuid, vm_spec)
        return task

    def mount_ngt_vm(self, vm_name):
        """ Maount NGT by VM Name
        """
        vm_uuid = self.get_vm_uuid_by_name(vm_name)
        print("vm_uuid: " + vm_uuid)
        vm_spec = self.get_vm_spec(vm_uuid)

        ngt_spec = {
                    "nutanix_guest_tools": {
                        "ngt_state": "UNINSTALLED",
                        "iso_mount_state": "MOUNTED",
                        "state": "ENABLED",
                        "enabled_capability_list": []
                    }
        }

        vm_spec["spec"]["resources"]["guest_tools"] = ngt_spec

        print(vm_spec)

        task = self.update_vm(vm_uuid, vm_spec)
        print(task)

        return task
# endregion

# region Calm BP related SDKs
    def get_bp_uuid(self, target_bp_name):
        """Get BP's UUID by BP name
        precondition: BP name is uniq
        """
        api_url = self.base_url + "/blueprints/list"
        payload_dict = {
            "kind": "blueprint"
        }

        payload_json = json.dumps(payload_dict)
        response = self.s.post(api_url, payload_json, verify=False)
        # print(response.text)

        d = json.loads(response.text)
        # print(json.dumps(d, indent=2))
        bps = d["entities"]
        for bp in bps:
            bp_name = bp["status"]["name"]
            bp_uuid = bp["status"]["uuid"]
            print(bp_name + ", " + bp_uuid)
            if (bp_name == target_bp_name):
                break
        return bp_uuid

    def get_app_profile_uuid(self, bp_uuid):
        """# Get UUID of app profile by BP UUID
        """
        api_url = \
            self.base_url + "/blueprints/" + bp_uuid + "/runtime_editables"
        response = self.s.get(api_url, verify=False)

        if not response.ok:
            print(response.text)
            exit(1)

        d = json.loads(response.text)
        # print(json.dumps(d, indent=2))
        resources = d["resources"]
        for resource in resources:
            app_profile_uuid = resource["app_profile_reference"]["uuid"]
            print("app_profile_uuid= " + app_profile_uuid)
            break
        return app_profile_uuid

    def launch_bp(self, app_name, bp_uuid, app_profile_uuid):
        """Launch BP
        """
        api_url = self.base_url + "/blueprints/" + bp_uuid + "/simple_launch"
        payload_dict = {
            "spec": {
                "app_name": app_name,
                "app_description":
                    "Calm application launched via Nutanix Calm REST API",
                "app_profile_reference": {
                    "kind": "app_profile",
                    "name": "Default",
                    "uuid": app_profile_uuid
                }
            }
        }

        response = self.s.post(api_url, json.dumps(payload_dict), verify=False)
        print(response.text)

        return response.json()
# endregion
