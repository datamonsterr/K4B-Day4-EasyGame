import unittest
from unittest.mock import patch

from tools.search_device_info.tool import search_device_info


class ExternalBoundaryTests(unittest.TestCase):
    def test_private_identity_is_rejected_before_network(self):
        for model in ['ThinkPad serial=PF123456', 'ThinkPad hostname=corp-laptop',
                      'ThinkPad user@northstar.internal', 'ThinkPad LT-204 EMP-1001',
                      'ThinkPad T14 Gen 4 serial number PF123456',
                      'ThinkPad T14 Gen 4 hostname corp-laptop-204',
                      'ThinkPad T14 Gen 4 location=Finance Floor 7',
                      'ThinkPad T14 Gen 4 assigned user Nguyen Van An']:
            with self.subTest(model=model), patch.dict('os.environ', {'TAVILY_API_KEY': 'synthetic-unit-test'}), patch('requests.post') as post:
                result = search_device_info('Lenovo', model, 'specs')
                self.assertEqual(result.get('error'), 'restricted_internal_identifier')
                post.assert_not_called()

    def test_public_identity_preserves_missing_key_error(self):
        with patch.dict('os.environ', {'TAVILY_API_KEY': ''}):
            self.assertEqual(search_device_info('Dell', 'UltraSharp U2723QE', 'specs')['error'], 'missing_api_key')
