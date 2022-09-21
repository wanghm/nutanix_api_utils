# nutanix restapi utilities

## Nutanix Rest API Versions and Base URL

* https://{PrismCentral Host}/api/nutanix/v3/
* https://{PrismCentral Host}/api/nutanix/v2.0/

## Resources

* Code Samples:    
https://www.nutanix.dev/code_samples/
* API references:    
https://www.nutanix.dev/api-reference-v3/    
https://www.nutanix.dev/api_references/prism-v2-0/
* API Explorer:    
https://{PrismCentral}:9440/api/nutanix/v3/api_explorer/index.html
https://{PrismElement}:9440/api/nutanix/v2/api_explorer/index.html

## Requirements

* Python3, requests   
`pip install requests`

## Usage
### config file: auth.json

```
{
    "prism_central_address": "xxx.xxx.xxx.xxx",
    "prism_element_address": "xxx.xxx.xxx.xxx",
    "user_name": "xxxxxxxxx",
    "password": "xxxxxxxxx"
}
```

### import this class
`from nutanix_api_utils_v3 import NutanixApiV3Client, RequestResponse`    
`from nutanix_api_v2_utils import NutanixRestapiUtils`

### Run the test code (Samples)
 `cd test`    
 `python test_nutanix_api_v3_utils.py ../auth.json`   
 `python test_nutanix_api_v3_utils_calm.py ../auth.json`
