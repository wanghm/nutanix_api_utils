#!/bin/env python
# -*- coding: utf-8 -*-
"""
  A sample wrapper script of Nutanix Rest API v3
  (Work In Process)
  requirements: python 3.x, requsts
"""

import sys
import json
import requests
import urllib3

class Nutanix_restapi_v3_wrapper():
    def __init__(self, username, password, base_url):
        self.username = username
        self.password = password
        self.base_url = base_url

        urllib3.disable_warnings()

        self.s = requests.Session()
        self.s.auth = (self.username, self.password)
        self.s.headers.update({'Content-Type': 'application/json; charset=utf-8'})

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
                exit #return the 1st one
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
                exit #return the 1st one
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
        #todo
        return

    def restore_vm(self, vm_uuid, unix_timestamp):
        #todo
        return
    
    def quarantine(self, vm_uuid):
        vm_spec = self.get_vm_spec(vm_uuid)
        vm_spec['metadata']['categories']['Quarantine'] = 'Default'
        #vm_spec['metadata']['categories']['Quarantine'] = 'Strict'
        #vm_spec['metadata']['categories']['Quarantine'] = 'Forensics'
        del vm_spec['metadata']['last_update_time']
        print(json.dumps(vm_spec, indent=2))

        task = self.update_vm(vm_uuid, vm_spec)
        return task

    def unquarantine(self, vm_uuid):
        vm_spec = self.get_vm_spec(vm_uuid)
        del vm_spec['metadata']['categories']['Quarantine']
        del vm_spec['metadata']['last_update_time']
        print(json.dumps(vm_spec, indent=2))

        task = self.update_vm(vm_uuid, vm_spec)
        return task
