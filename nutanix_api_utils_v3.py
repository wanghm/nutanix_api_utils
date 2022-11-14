#!/bin/env python
# -*- coding: utf-8 -*-
"""nutanix_api_utils_v3.py
~~~~~~~~~~~~~~~~~~~~~~

RestAPIClient class of Nutanix Rest API v3

(c) 2022 Huimin Wang
"""
from dataclasses import dataclass
import json
import requests
import urllib3
import logging


@dataclass
class RequestResponse:
    """class to hold the response from the requests
    """
    def __init__(self):
        self.code = 0
        self.message = ""
        self.json = ""
        self.details = ""


class NutanixApiV3Client:
    """RestAPIClient class for Nutanix Rest API v3"""
    def __init__(self, username, password, prism_addr):
        """Class constructor
        Args:
            username (str): username
            password (str): password
            prism_addr (str): IP of DNS namwe of API Endpont(V3=Prism Element)
        """
        self.base_url = 'https://' + prism_addr + ':9440/api/nutanix/v3'
        urllib3.disable_warnings()

        self.s = requests.Session()
        self.s.auth = (username, password)
        self.s.headers.update(
            {'Content-Type': 'application/json; charset=utf-8'})

        self.logger = logging.getLogger(__name__)

    def send(self, method, url, payload=None):
        """Send the request to the API endpoint
        Args:
            method(str): HTTP method
            url(str): URL of the API endpoint
            payload(str): payload of the request
        Returns:
            RequestResponse: response from the API endpoint
        Exceptions:
            Exception: if the response code is not 200
        """
        response = RequestResponse()
        try:
            if method == "GET":
                result = self.s.get(url, verify=False)
            elif method == "POST":
                result = self.s.post(url, json.dumps(payload), verify=False)
            elif method == "PUT":
                result = self.s.put(url, json.dumps(payload), verify=False)
            elif method == "DELETE":
                result = self.s.delete(url, verify=False)
            else:
                result = None
                raise Exception("Invalid method")

            response.code = 0
            response.message = "Success"
            response.json = result.json()

        except requests.exceptions.ConnectTimeout:
            print("Connection timeout")
            response.code = -99
            response.message = "Connection has timed out."
            response.details = "Exception: requests.exceptions.ConnectTimeout"

        except Exception as e:
            print(e)
            response.code = -99
            response.message = "Exception has occurred"
            response.details = f"Exception: {e}"

        return response

# region VM related
    def get_vm_uuid(self, payload):
        """Get VM UUID by paylod (in V3 API get VM API uses POST method)
        Args:
            payload (dict): payload of the request
        returns:
            str: VM UUID
        """
        response = \
            self.send("POST", self.base_url + '/vms/list', payload)

        vm_specs = response.json['entities']

        vm_uuid = ''
        for vm in vm_specs:
            if vm['metadata']:
                vm_uuid = vm['metadata']['uuid']
                break  # return the 1st one
        return vm_uuid

    def get_vm_uuid_by_name(self, vm_name):
        """ Get VM UUID by VM Name
        Args:
            vm_name (str): VM name
        Returns:
            str: VM UUID
        Note:
            Unsupported filter is in use!
        """
        payload = {
            "filter": "vm_name==.*" + vm_name + ".*",
            "kind": "vm"
        }
        return self.get_vm_uuid(payload)

    def get_vm_uuid_by_ip_address(self, ip_address):
        """ Get VM UUID by VM IP address
        Args:
            ip_address (str): VM IP address
        returns:
            str: VM UUID
        Note:
            Unsupported filter is in use!
        """
        payload = {
            "filter": "ip_addresses==" + ip_address,
            "kind": "vm"
        }
        return self.get_vm_uuid(payload)

    def get_vm_spec(self, vm_uuid):
        """ Get VM spec(Json) by VM UUID
        Args:
            vm_uuid (str): VM UUID
        Returns:
            dict: VM spec(Json)
        """
        response = self.send("GET", url=self.base_url + "/vms/" + vm_uuid)
        vm_spec = response.json

        del vm_spec['status']

        return vm_spec

    def update_vm(self, vm_uuid, vm_spec_json):
        """ Get VM UUID by VM spec(Json)
        Args:
            vm_uuid (str): VM UUID
            vm_spec_json (dict): VM spec(Json)
        Returns:
            RequestResponse: response from the API endpoint
        """
        response = \
            self.send("PUT", self.base_url + '/vms/' + vm_uuid, vm_spec_json)

        return response

    def delete_vm(self, vm_uuid):
        """ Delete VM by VM UUID
        Args:
            vm_uuid (str): VM UUID
        Returns:
            RequestResponse: response from the API endpoint
        """
        response = \
            self.send("DELETE", self.base_url + '/vms/' + vm_uuid)

        return response

    def quarantine_vm(self, vm_uuid, quarantine_method):
        """ Quarentine VM by VM UUID
        Args:
            vm_uuid (str): VM UUID
            quarantine_method (str): "Strict" or "Forensics"
        returns:
            RequestResponse: response from the API endpoint
        """
        vm_spec = self.get_vm_spec(vm_uuid)
        if quarantine_method not in ["Default", "Strict", "Forensics"]:
            raise Exception("Quarantine Method:" + quarantine_method +
                            " is not valid. Valid values: Strict, Forensics")
        vm_spec['metadata']['categories']['Quarantine'] = quarantine_method
        del vm_spec['metadata']['last_update_time']
        print(json.dumps(vm_spec, indent=2))

        response = self.update_vm(vm_uuid, vm_spec)
        return response

    def unquarantine_vm(self, vm_uuid):
        """ Unquarentine VM by VM UUID
        Args:
            vm_uuid (str): VM UUID
        Returns:
            RequestResponse: response from the API endpoint
        """
        vm_spec = self.get_vm_spec(vm_uuid)
        del vm_spec['metadata']['categories']['Quarantine']
        del vm_spec['metadata']['last_update_time']
        print(json.dumps(vm_spec, indent=2))

        response = self.update_vm(vm_uuid, vm_spec)
        return response

    def mount_ngt_vm(self, vm_name,
                     ssr_enabled=False, vss_snapshot_enabled=False):
        """ Maount NGT by VM Name
        Args:
            vm_name (str): VM name
            ssr_enabled (bool): SSR enabled
            vss_snapshot_enabled (bool): VSS snapshot enabled
        Returns:
            RequestResponse: response from the API endpoint
        """
        vm_uuid = self.get_vm_uuid_by_name(vm_name)
        print("vm_uuid: " + vm_uuid)
        vm_spec = self.get_vm_spec(vm_uuid)

        ngt_spec = {
                    "nutanix_guest_tools": {
                        "ngt_state": "UNINSTALLED",
                        "iso_mount_state": "MOUNTED",
                        "state": "ENABLED",
                        "enabled_capability_list": [
                        ]
                    }
        }
        if ssr_enabled:
            ngt_spec["nutanix_guest_tools"]["enabled_capability_list"].append("SELF_SERVICE_RESTORE")
        if vss_snapshot_enabled:
            ngt_spec["nutanix_guest_tools"]["enabled_capability_list"].append("VSS_SNAPSHOT")

        vm_spec["spec"]["resources"]["power_state"] = "ngt_spec"

        print(vm_spec)

        response = self.update_vm(vm_uuid, vm_spec)
        print(response.json)

        return response

    def power_on_vm(self, vm_name):
        vm_uuid = self.get_vm_uuid_by_name(vm_name)
        print("vm_uuid: " + vm_uuid)
        vm_spec = self.get_vm_spec(vm_uuid)
        vm_spec["spec"]["resources"]["power_state"] = "ON"
        print(vm_spec)

        response = self.update_vm(vm_uuid, vm_spec)
        print(response.json)

        return response
        
    def power_off_vm(self, vm_name):
        vm_uuid = self.get_vm_uuid_by_name(vm_name)
        print("vm_uuid: " + vm_uuid)
        vm_spec = self.get_vm_spec(vm_uuid)
        vm_spec["spec"]["resources"]["power_state"] = "OFF"
        print(vm_spec)

        response = self.update_vm(vm_uuid, vm_spec)
        print(response.json)

        return response
# endregion

# region cluster related
    def get_cluster_spec(self, cluster_name):
        """ Get cluster spec
        Args:
            cluster_name (str): cluster name
        Returns:
            dict: cluster spec
        """
        payload = {"kind": "cluster"}

        response = \
            self.send("POST", self.base_url + '/clusters/list', payload)

        cluster_spec = None
        clusters = response.json['entities']

        for cluster_spec in clusters:
            del cluster_spec["status"]
            if cluster_spec['spec']['name'] == cluster_name:
                break

        return cluster_spec

    def get_cluster_uuid(self, cluster_name):
        """ Get cluster UUID
        Args:
            cluster_name (str): cluster name
        Returns:
            str: cluster UUID
        """
        cluster_spec = self.get_cluster_spec(cluster_name)
        cluster_uuid = cluster_spec['metadata']['uuid']

        return cluster_uuid

    def update_cluster_ntp(self, cluster_name, ntp_servers):
        """ Update cluster: NTP servers
        Args:
            cluster_name (str): cluster name
            ntp_servers (list): NTP servers
        Returns:
            RequestResponse: response from the API endpoint
        """
        cluster_spec = self.get_cluster_spec(cluster_name)
        cluster_uuid = cluster_spec['metadata']['uuid']

        # update cluster_spec_json : change the ntp_servers
        cluster_spec["spec"]["resources"]["network"]["ntp_server_ip_list"] = ntp_servers

        print(cluster_spec)

        response = \
            self.send("PUT", self.base_url + '/clusters/' + cluster_uuid, cluster_spec)

        return response

# endregion

# region Calm BP related
    def get_bp_uuid(self, target_bp_name):
        """Get BP's UUID by BP name
        Args:
            target_bp_name (str): BP name
        Returns:
            str: BP UUID
        """
        payload = {
            "kind": "blueprint"
        }

        response = self.send("POST", self.base_url + "/blueprints/list", payload)

        d = json.loads(response.json)
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
        """ Get UUID of app profile by BP UUID
        Args:
            bp_uuid (str): BP UUID
        Returns:
            str: app profile UUID
        """
        response = \
            self.send("GET", self.base_url + "/blueprints/" + bp_uuid + "/runtime_editables")

        d = response.json
        resources = d["resources"]
        for resource in resources:
            app_profile_uuid = resource["app_profile_reference"]["uuid"]
            print("app_profile_uuid= " + app_profile_uuid)
            break
        return app_profile_uuid

    def launch_bp(self, app_name, bp_uuid, app_profile_uuid):
        """Launch BP
        Args:
            app_name (str): app name
            bp_uuid (str): BP UUID
            app_profile_uuid (str): app profile UUID
        Returns:
            RequestResponse: response from the API endpoint
        """
        api_url = self.base_url + "/blueprints/" + bp_uuid + "/simple_launch"
        payload = {
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

        response = self.send("POST", api_url, payload)

        return response.json
# endregion
