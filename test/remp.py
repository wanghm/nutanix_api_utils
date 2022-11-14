import json
import urllib3
import requests
from requests.auth import HTTPBasicAuth

prism_addr = "10.48.70.69"
prism_user ="admin"
prism_pass ="P@ssw0rd001"
snapshot_name = "test_snapshot_xxxxxx"


request_headers = {"Content-Type": "application/json", "charset": "utf-8"}
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_vm_specs():
    # get all VM specs
    endpoint = f'https://{prism_addr}:9440/api/nutanix/v2.0/vms'

    results = requests.get(
        endpoint,
        headers=request_headers,
        verify=False,
        auth=HTTPBasicAuth(prism_user, prism_pass),
    ).json()

    vm_specs = results["entities"]
    return vm_specs

def take_snapshot(snapshot_name, vm_uuid):
    payload = {
            "snapshot_specs": [
                {
                    "snapshot_name": snapshot_name,
                    "vm_uuid": vm_uuid
                }
            ]
    }
    endpoint = f'https://{prism_addr}:9440/api/nutanix/v2.0/snapshots'
    results = requests.post(
        endpoint,
        data=json.dumps(payload),
        headers=request_headers,
        verify=False,
        auth=HTTPBasicAuth(prism_user, prism_pass)
    )
    return results
    

if __name__ == '__main__':
    
    vm_specs = get_vm_specs()

    for vm in vm_specs:
        vm_name = vm.get("name")
        vm_uuid = vm.get("uuid")
        print(f"vm_name:{vm_name} vm_uuid:{vm_uuid}")

        task = take_snapshot(snapshot_name, vm_uuid)
        print(task.text)
