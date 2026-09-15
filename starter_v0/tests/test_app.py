import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
from providers.base import ModelResponse, ToolCall

ROOT = Path(__file__).resolve().parents[1]


class AppTests(unittest.TestCase):
    def test_startup_and_error_trace_and_new_chat(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict('os.environ', {'EASYGAME_TRANSCRIPTS_DIR': folder}):
            app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=15).run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.chat_input), 1)
            response = ModelResponse(text='Inspection completed', tool_calls=[ToolCall('inspect_device', {'asset_id': 'LT-999999'})])
            with patch('providers.gemini_provider.GeminiProvider.complete', return_value=response):
                app.chat_input[0].set_value('Inspect LT-999999').run()
            self.assertEqual(len(app.exception), 0)
            self.assertTrue(any('asset_not_found' in e.value for e in app.error))
            self.assertEqual(len(app.session_state.conversation.transcript['turns']), 1)
            app.button[0].click().run()
            self.assertEqual(len(app.session_state.conversation.transcript['turns']), 0)

    def test_actual_confirmation_button_writes_once_and_cancel_does_not(self):
        import importlib
        import json
        ticket_module = importlib.import_module('tools.create_ticket.tool')
        with tempfile.TemporaryDirectory() as folder, patch.dict('os.environ', {'EASYGAME_TRANSCRIPTS_DIR': folder}), patch.object(ticket_module, 'TICKET_DIR', Path(folder) / 'tickets'):
            app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=15).run()
            response = ModelResponse(tool_calls=[ToolCall('create_ticket', {'summary': 'VPN issue', 'priority': 'high', 'asset_id': 'LT-204', 'confirmed': True})])
            with patch('providers.gemini_provider.GeminiProvider.complete', return_value=response):
                app.chat_input[0].set_value('Create reviewed ticket').run()
            self.assertFalse((Path(folder) / 'tickets').exists())
            next(b for b in app.button if b.label == 'Xác nhận ghi ticket').click().run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(list((Path(folder) / 'tickets').glob('*.json'))), 1)
            self.assertFalse(any(b.label == 'Xác nhận ghi ticket' for b in app.button))
            with patch('providers.gemini_provider.GeminiProvider.complete', return_value=response):
                app.chat_input[0].set_value('Prepare another ticket').run()
            next(b for b in app.button if b.label == 'Hủy ticket').click().run()
            self.assertEqual(len(list((Path(folder) / 'tickets').glob('*.json'))), 1)
            self.assertIsNone(app.session_state.conversation.pending_ticket)
            saved = json.loads(next(Path(folder).glob('*.transcript.json')).read_text())
            self.assertEqual(saved['turns'][-1]['status'], 'cancelled')
            self.assertEqual(saved['turns'][1]['tool_events'][0]['result']['status'], 'created')
