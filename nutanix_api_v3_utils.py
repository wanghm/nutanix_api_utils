#!/bin/env python
# -*- coding: utf-8 -*-
"""
  Utility class (mini SDK) of Nutanix Rest API v3
  (Work In Process)
  requirements: python 3.x, requsts
"""

import sys
import json
import requests
import urllib3

class Nutanix_restapi_mini_sdk():
    def __init__(self, username, password, base_url):
        self.username = username
        self.password = password
        self.base_url = base_url

        urllib3.disable_warnings()

        self.s = requests.Session()
        self.s.auth = (self.username, self.password)
        self.s.headers.update({'Content-Type': 'application/json; charset=utf-8'})

    ############### VM related SDKs ###############
    def get_vm_uuid_by_name(self, vm_name):
        api_url = self.base_url + '/vms/list'
        payload = {
            "filter": "vm_name==.*" + vm_name + ".*",
            "kind": "vm"
        }
        vms_spec = self.s.post(api_url, json.dumps(payload), verify=False).json()
        print ("vms_spec ------")
        print (vms_spec)

        vm_uuid = ''
        for vm in vms_spec['entities']:
           if vm['metadata']: #sometimes this value will be '{}' 
                vm_uuid = vm['metadata']['uuid']
                break #return the 1st one
        return vm_uuid
    
    def get_vm_uuid_by_ip_address(self, ip_address):
        # only one or zero VM will bematched 
        api_url = self.base_url + '/vms/list'
        payload = {
            "filter": "ip_addresses==" + ip_address,
            "kind": "vm"
        }
        #vms_spec = self.post(api_url, json.dumps(payload)).json()
        vms_spec = self.s.post(api_url, data=json.dumps(payload), verify=False).json()
        print ("vms_spec ------")
        print (vms_spec)
        
        vm_uuid = ''
        for vm in vms_spec['entities']:
           if vm['metadata']: #sometimes this value will be '{}' 
                vm_uuid = vm['metadata']['uuid']
                break #return the 1st one
        return vm_uuid

    def get_vm_spec(self, vm_uuid):
        api_url = self.base_url + '/vms/' + vm_uuid
        vm_spec = self.s.get(api_url, verify=False).json()
        del vm_spec['status']
        return vm_spec

    def update_vm(self, vm_uuid, vm_spec_json):
        api_url = self.base_url + '/vms/' + vm_uuid
        task = self.s.put(api_url, data=json.dumps(vm_spec_json), verify=False).json() 
        return task

    def delete_vm(self, vm_uuid):
        api_url = self.base_url + '/vms/' + vm_uuid
        task = self.s.delete(api_url, verify=False).json() 
        return task

    def restore_vm(self, vm_uuid, unix_timestamp):
        #todo
        return
    
    def quarantine_vm(self, vm_uuid):
        vm_spec = self.get_vm_spec(vm_uuid)
        vm_spec['metadata']['categories']['Quarantine'] = 'Default'
        #vm_spec['metadata']['categories']['Quarantine'] = 'Strict'
        #vm_spec['metadata']['categories']['Quarantine'] = 'Forensics'
        del vm_spec['metadata']['last_update_time']
        print(json.dumps(vm_spec, indent=2))

        task = self.update_vm(vm_uuid, vm_spec)
        return task

    def unquarantine_vm(self, vm_uuid):
        vm_spec = self.get_vm_spec(vm_uuid)
        del vm_spec['metadata']['categories']['Quarantine']
        del vm_spec['metadata']['last_update_time']
        print(json.dumps(vm_spec, indent=2))

        task = self.update_vm(vm_uuid, vm_spec)
        return task

    ############### Calm BP related SDKs ###############
    def get_bp_uuid(self, target_bp_name):
        #Get BP's UUID by BP name
        #precondition: BP name is uniq
        api_url = self.base_url + "/blueprints/list"
        payload_dict = {
            "kind":"blueprint"
        }

        payload_json = json.dumps(payload_dict)
        response = self.s.post(api_url, payload_json, verify=False)
        #print(response.text)

        d = json.loads(response.text)
        #print(json.dumps(d, indent=2))
        bps = d["entities"]
        for bp in bps:
            bp_name = bp["status"]["name"]
            bp_uuid = bp["status"]["uuid"]
            print(bp_name + ", " + bp_uuid)
            if (bp_name == target_bp_name):
                break
        return bp_uuid
            
    def get_app_profile_uuid(self, bp_uuid):
        #Get UUID of app profile by BP UUID
        api_url = self.base_url + "/blueprints/" + bp_uuid + "/runtime_editables"
        response = self.s.get(api_url, verify=False)
        
        if not response.ok:
            print(response.text)
            exit(1)

        d = json.loads(response.text)
        #print(json.dumps(d, indent=2))
        resources = d["resources"]
        for resource in resources:
            app_profile_uuid=  resource["app_profile_reference"]["uuid"]
            print("app_profile_uuid= " + app_profile_uuid)
            break
        return app_profile_uuid


    def launch_bp(self, app_name, bp_uuid, app_profile_uuid):
        #Launch BP
        api_url = self.base_url + "/blueprints/" + bp_uuid + "/simple_launch"
        payload_dict = {
            "spec": {
                "app_name": app_name,
                "app_description": "Calm application launched via Nutanix Calm REST API",
                "app_profile_reference": {
                    "kind": "app_profile",
                    "name": "Default",
                    "uuid": app_profile_uuid
                }
            }
        }

        payload_json = json.dumps(payload_dict)
        response = self.s.post(api_url, payload_json, verify=False)
        print(response.text)

        return
    