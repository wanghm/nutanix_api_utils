# nutanix restapi utilities

## Nutanix Rest API Versions and Base URL

* https://{PrismCentral Host}/api/nutanix/v4/
* https://{PrismCentral Host}/api/nutanix/v3/
* https://{PrismCentral Host}/api/nutanix/v2.0/

## Resources

* Code Samples:    
https://www.nutanix.dev/code_samples/
* API references:    
https://www.nutanix.dev/api-reference-v4/
https://www.nutanix.dev/api-reference-v3/
https://www.nutanix.dev/api_references/prism-v2-0/
* API Explorer:    
https://{PrismCentral}:9440/api/nutanix/v4/api_explorer/index.html
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

### CLI: `NutanixV4CategoryManager_v4.py`

VM名の部分一致でカテゴリを一括付与するスクリプトの CLI 使用例:

```bash
# 環境内の Python 仮想環境を使う例
/Users/huimin.wang/workspace/2.git_local/nutanix_api_utils/.venv/bin/python NutanixV4CategoryManager_v4.py \
    --host https://10.0.0.1 --username admin --password secret \
    --pattern WEB-SERVER --key AppFamily --value Production --log-level INFO
```

主な引数:
- `--host/-H`: Nutanix PrismCentral のホスト URL（例: `https://10.0.0.1`）
- `--username/-u`: API 用ユーザ名
- `--password/-p`: API 用パスワード
- `--pattern/-P`: VM 名の部分一致パターン（必須）
- `--key/-k`, `--value/-v`: 付与するカテゴリのキーと値（必須）
- `--disable-insecure-warnings`: urllib3 の InsecureRequestWarning を抑止
- `--log-level`: ログレベル（DEBUG/INFO/WARNING/ERROR/CRITICAL）

環境変数からの読み取りも可能です（引数が省略された場合）:
- `NUTANIX_HOST`, `NUTANIX_USER`, `NUTANIX_PASS`

注意: パスワード等の機微情報は安全な方法で管理してください（環境変数やシークレット管理を推奨）。

