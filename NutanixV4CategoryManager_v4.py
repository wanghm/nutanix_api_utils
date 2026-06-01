import os
import argparse
import urllib3
import logging
from typing import List, Optional

try:
    import ntnx_vmm_py_client
    from ntnx_vmm_py_client import ApiClient as VmmClient
    from ntnx_vmm_py_client.rest import ApiException as VmmApiException
except Exception:
    ntnx_vmm_py_client = None
    VmmClient = None
    VmmApiException = Exception

try:
    import ntnx_prism_py_client
    from ntnx_prism_py_client import ApiClient as PrismClient
    from ntnx_prism_py_client.rest import ApiException as PrismApiException
except Exception:
    ntnx_prism_py_client = None
    PrismClient = None
    PrismApiException = Exception

# Optional: disable insecure request warnings when explicitly requested
if os.getenv("DISABLE_INSECURE_WARNINGS") == "1":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NutanixV4CategoryManager:
    def __init__(self, pc_ip: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None):
        """Initialize Nutanix v4 SDK clients.

        If parameters are omitted, environment variables are used:
        `NUTANIX_HOST`, `NUTANIX_USER`, `NUTANIX_PASS`.
        """
        self.logger = logging.getLogger(__name__)

        pc_ip = pc_ip or os.getenv("NUTANIX_HOST")
        username = username or os.getenv("NUTANIX_USER")
        password = password or os.getenv("NUTANIX_PASS")

        if not (pc_ip and username and password):
            raise ValueError("pc_ip, username and password must be provided via args or environment variables")

        # VMM (Virtual Machine Management) configuration
        if ntnx_vmm_py_client is not None:
            self.vmm_config = ntnx_vmm_py_client.Configuration()
            self.vmm_config.host = pc_ip
            self.vmm_config.username = username
            self.vmm_config.password = password
            self.vmm_client = VmmClient(self.vmm_config)
            self.vm_api = ntnx_vmm_py_client.VmApi(self.vmm_client)
        else:
            # allow tests or offline usage to set these attributes later
            self.vmm_config = None
            self.vmm_client = None
            self.vm_api = None

        # Prism (Category/Task Management) configuration
        if ntnx_prism_py_client is not None:
            self.prism_config = ntnx_prism_py_client.Configuration()
            self.prism_config.host = pc_ip
            self.prism_config.username = username
            self.prism_config.password = password
            self.prism_client = PrismClient(self.prism_config)
            self.category_api = ntnx_prism_py_client.CategoryApi(self.prism_client)
        else:
            self.prism_config = None
            self.prism_client = None
            self.category_api = None

    def assign_category_by_vm_name_pattern(self, name_pattern: str, cat_key: str, cat_value: str) -> None:
        """Find VMs whose name contains `name_pattern` and assign a category.

        This orchestrates find/get/assign operations and logs results.
        """
        # OData v3 フィルタ: contains を使用。シングルクォートは OData で'' にエスケープ。
        safe_pattern = name_pattern.replace("'", "''")
        filter_query = f"contains(name,'{safe_pattern}')"

        self.logger.info("Searching for VMs matching pattern: '%s'", name_pattern)
        try:
            vms_response = self.vm_api.list_vms(_filter=filter_query)
            vms = getattr(vms_response, "data", []) or []

            if not vms:
                self.logger.info("No VMs found matching the pattern.")
                return

            self.logger.info("Found %d VMs. Starting processing...", len(vms))

            for vm in vms:
                vm_ext_id = getattr(vm, "ext_id", None) or getattr(vm, "uuid", None)
                vm_name = getattr(vm, "name", "<unknown>")

                # ensure match locally in case server-side filter was not applied
                if name_pattern not in vm_name:
                    self.logger.debug("Skipping VM that does not match pattern: %s", vm_name)
                    continue

                if not vm_ext_id:
                    self.logger.warning("Skipping VM with no ID: %s", vm_name)
                    continue

                try:
                    vm_detail = self.vm_api.get_vm_by_id(vm_ext_id)
                    etag = self._get_vm_etag(vm_detail)

                    body = {"categoryKey": cat_key, "categoryValue": cat_value}

                    self._assign_category(vm_ext_id, body, etag, vm_name)

                except (VmmApiException, PrismApiException) as inner_e:
                    # ApiException may not have `reason` attribute reliably
                    self.logger.error("Failed to process VM %s: %s", vm_name, getattr(inner_e, 'reason', str(inner_e)))

        except Exception:
            self.logger.exception("A general error occurred while assigning categories")

    def _get_vm_etag(self, vm_detail) -> Optional[str]:
        try:
            etag = self.vmm_client.get_etag(vm_detail)
            return etag
        except Exception:
            self.logger.exception("Failed to obtain ETag for VM detail")
            return None

    def _assign_category(self, entity_id: str, body: dict, if_match: Optional[str], vm_name: str) -> None:
        try:
            self.category_api.associate_category_to_entity(
                entity_type="vm",
                entity_id=entity_id,
                body=body,
                if_match=if_match,
            )
            self.logger.info("Successfully assigned %s:%s to VM: %s", body.get('categoryKey'), body.get('categoryValue'), vm_name)
        except (VmmApiException, PrismApiException):
            self.logger.exception("Failed to associate category to VM %s", vm_name)


def configure_logging(level: str = "INFO") -> None:
    numeric = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(level=numeric, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Assign Nutanix categories to VMs by name pattern")
    parser.add_argument("--host", "-H", help="Nutanix host (e.g. https://10.0.0.1)")
    parser.add_argument("--username", "-u", help="Username for Nutanix API")
    parser.add_argument("--password", "-p", help="Password for Nutanix API")
    parser.add_argument("--pattern", "-P", required=True, help="VM name substring to match")
    parser.add_argument("--key", "-k", required=True, help="Category key to assign")
    parser.add_argument("--value", "-v", required=True, help="Category value to assign")
    parser.add_argument("--disable-insecure-warnings", action="store_true", help="Disable urllib3 insecure request warnings")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Logging level")

    args = parser.parse_args()

    configure_logging(args.log_level)

    if args.disable_insecure_warnings:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Do not log sensitive info like password
    logging.getLogger(__name__).info("Starting category assignment: host=%s user=%s pattern=%s key=%s", args.host, args.username, args.pattern, args.key)

    manager = NutanixV4CategoryManager(pc_ip=args.host, username=args.username, password=args.password)
    manager.assign_category_by_vm_name_pattern(args.pattern, args.key, args.value)


if __name__ == "__main__":
    main()

