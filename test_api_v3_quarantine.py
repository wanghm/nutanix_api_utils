#!/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import requests
import urllib3

args = sys.argv
conf_file = args[1]
vm_uuid = args[2]
vm_quarantine = args[3]

with open(conf_file, "r") as file:
    conf = file.read()
    conf = json.loads(conf)
prism_addr = conf["prism_address"]
prism_user = conf["user_name"]
prism_pass = conf["password"]

def get_ntnx_v3_vm_spec(vm_uuid):
  api_url = 'https://' + prism_addr + ':9440/api/nutanix/v3/vms/' + vm_uuid
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
  s = requests.Session()
  s.auth = (prism_user, prism_pass)
  s.headers.update({'Content-Type': 'application/json; charset=utf-8'})
  vm_spec = s.get(api_url, verify=False).json()
  del vm_spec['status']
  return vm_spec

def update_ntnx_v3_vm(vm_uuid, vm_spec_json):
  api_url = 'https://' + prism_addr + ':9440/api/nutanix/v3/vms/' + vm_uuid
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
  s = requests.Session()
  s.auth = (prism_user, prism_pass)
  s.headers.update({'Content-Type': 'application/json; charset=utf-8'})
  task = s.put(api_url, data=json.dumps(vm_spec_json), verify=False).json()
  return task

def main():
  vm = get_ntnx_v3_vm_spec(vm_uuid)
  print('Before update ----------')
  print(json.dumps(vm, indent=2))
  print('------------------------------')

  if (vm_quarantine == "on"):
    vm['metadata']['categories']['Quarantine'] = 'Default'
    #vm['metadata']['categories']['Quarantine'] = 'Strict'
    #vm['metadata']['categories']['Quarantine'] = 'Forensics'
  else:
    del vm['metadata']['categories']['Quarantine']

  del vm['metadata']['last_update_time']
  print('Config ----------')
  print(json.dumps(vm, indent=2))

  task = update_ntnx_v3_vm(vm_uuid, vm)
  print('Return ----------')
  print(json.dumps(task, indent=2))

if __name__ == '__main__':
  main()