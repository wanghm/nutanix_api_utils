# nutanix restapi v3 utility class (mini SDK)

## Nutanix Rest API Versions and Base URL

* https://{PrismCentral Host}/api/nutanix/v3/

## Resources

* Code Samples: https://www.nutanix.dev/code_samples/
* API references: https://www.nutanix.dev/api-reference-v3/
* API Explorer: https://{Prism Central Host}:9440/api/nutanix/v3/api_explorer/index.html

## Requirements

* Python3, requests   
`pip install requests`

## Usage
### config file: auth.json

```
{
    "prism_central_address": "xxx.xxx.xxx.xxx",
    "user_name": "xxxxxxxxx",
    "password": "xxxxxxxxx"
}
```

### import this class
`from nutanix_api_v3_utils import Nutanix_restapi_mini_sdk`

### Run the test code

 `python test_nutanix_api_v3_utils_vm.py ./auth.json`   

 `python test_nutanix_api_v3_utils_calm.py ./auth.json`
