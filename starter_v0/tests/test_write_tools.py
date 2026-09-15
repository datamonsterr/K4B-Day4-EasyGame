import importlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

module = importlib.import_module('tools.create_ticket.tool')


class WriteToolTests(unittest.TestCase):
    def test_confirmation_and_sensitive_payload_produce_no_files(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(module, 'TICKET_DIR', Path(directory)):
            self.assertEqual(module.create_ticket('VPN issue', confirmed=False)['status'], 'needs_confirmation')
            self.assertEqual(module.create_ticket('password=SyntheticTestOnly', confirmed=True)['error'], 'restricted_sensitive_data')
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_confirmed_mock_ticket_is_a_real_file(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(module, 'TICKET_DIR', Path(directory)):
            result = module.create_ticket('VPN issue', priority='high', asset_id='LT-204', confirmed=True)
            payload = json.loads(Path(result['path']).read_text())
            self.assertEqual(result['status'], 'created')
            self.assertEqual(payload['summary'], 'VPN issue')
            self.assertEqual(payload['source'], 'educational_local_mock')
            self.assertEqual(len(list(Path(directory).glob('*.json'))), 1)
