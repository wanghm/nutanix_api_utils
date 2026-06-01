import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from NutanixV4CategoryManager_v4 import NutanixV4CategoryManager


class TestNutanixV4CategoryManager(unittest.TestCase):
    def setUp(self):
        # create manager with dummy creds
        self.manager = NutanixV4CategoryManager(pc_ip="https://example", username="user", password="pass")

        # prepare fake VMs
        vm1 = SimpleNamespace(ext_id="vm-1", name="WEB-SERVER-01")
        vm2 = SimpleNamespace(ext_id="vm-2", name="OTHER-01")
        vms_response = SimpleNamespace(data=[vm1, vm2])

        # patch APIs on the manager instance
        self.manager.vm_api = Mock()
        self.manager.vm_api.list_vms.return_value = vms_response
        self.manager.vm_api.get_vm_by_id.return_value = SimpleNamespace()

        self.manager.vmm_client = Mock()
        self.manager.vmm_client.get_etag.return_value = "etag-1"

        self.manager.category_api = Mock()

    def test_assign_category_by_vm_name_pattern_assigns_matching_vms(self):
        self.manager.assign_category_by_vm_name_pattern("WEB-SERVER", "AppFamily", "Production")

        # associate_category_to_entity should be called once for vm1 only
        self.manager.category_api.associate_category_to_entity.assert_called_once()
        _, kwargs = self.manager.category_api.associate_category_to_entity.call_args
        self.assertEqual(kwargs.get('entity_id'), "vm-1")
        self.assertEqual(kwargs.get('body'), {"categoryKey": "AppFamily", "categoryValue": "Production"})


if __name__ == '__main__':
    unittest.main()
