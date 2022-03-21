# nutanix_api_v3 : test code of Nutanix Rest API v3

## Requirements

Python3, requests
`pip install requests`

## config file: auth.json

```
{
    "prism_central_address": "xxx.xxx.xxx.xxx",
    "user_name": "xxxxxxxxx",
    "password": "xxxxxxxxx"
}
```

## Quarantine a VM (set category)

`python test_api_v3_quarantine.py ./auth.json <VM UUID> on`

`python test_api_v3_quarantine.py ./auth.json <VM UUID> off`
