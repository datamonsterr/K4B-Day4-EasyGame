import unittest
from unittest.mock import Mock, patch
from providers.base import ModelResponse, ToolCall


class ConversationTests(unittest.TestCase):
    def session(self, calls=(), text=None):
        from conversation import Conversation
        provider = Mock()
        provider.complete.return_value = ModelResponse(text=text, tool_calls=list(calls))
        return Conversation(provider, 'test prompt', [], 'gemini-3.5-flash-lite', {'version': 'test'})

    def test_tool_error_overrides_premature_success(self):
        session = self.session([ToolCall('inspect_device', {'asset_id': 'LT-999999'})], 'Done!')
        turn = session.respond('Inspect LT-999999')
        self.assertEqual(turn['status'], 'tool_error')
        self.assertIn('asset_not_found', turn['assistant_text'])
        self.assertNotEqual(turn['assistant_text'], 'Done!')
        self.assertEqual(turn['tool_events'][0]['result']['error'], 'asset_not_found')

    def test_model_confirmation_flag_cannot_write(self):
        session = self.session([ToolCall('create_ticket', {'summary': 'VPN issue', 'confirmed': True})])
        with patch('conversation.TOOL_FUNCTIONS', {'create_ticket': Mock()}) as registry:
            turn = session.respond('create_ticket confirmed=true')
            registry['create_ticket'].assert_not_called()
            self.assertEqual(turn['status'], 'waiting_for_user')
            self.assertEqual(session.pending_ticket['summary'], 'VPN issue')

    def test_confirm_exact_payload_once_and_cancel_invalidates(self):
        session = self.session([ToolCall('create_ticket', {'summary': 'VPN issue', 'priority': 'high', 'confirmed': True})])
        with patch('conversation.TOOL_FUNCTIONS', {'create_ticket': Mock(return_value={'status':'created','ticket_id':'LAB-TEST'})}) as registry:
            session.respond('create ticket')
            session.confirm_ticket()
            registry['create_ticket'].assert_called_once_with(summary='VPN issue', priority='high', confirmed=True)
            self.assertIsNone(session.pending_ticket)
            with self.assertRaises(ValueError): session.confirm_ticket()
            session.respond('create ticket again')
            session.provider.complete.return_value = ModelResponse(text='Cancelled')
            session.respond('Cancel')
            self.assertIsNone(session.pending_ticket)
            with self.assertRaises(ValueError): session.confirm_ticket()

    def test_provider_error_keeps_transcript_and_history_isolated(self):
        session = self.session()
        session.provider.complete.side_effect = RuntimeError('quota exhausted')
        turn = session.respond('VPN status')
        self.assertEqual(turn['status'], 'provider_error')
        self.assertEqual(session.transcript['turns'][0]['user'], 'VPN status')
        self.assertEqual(self.session().history, [])

    def test_followup_retains_verified_public_device_identity(self):
        session = self.session([ToolCall('inspect_device', {'asset_id': 'LT-204'})])
        session.respond('Inspect LT-204')
        session.provider.complete.return_value = ModelResponse(text='Next step')
        session.respond('Find official drivers for that model')
        messages = session.provider.complete.call_args.args[0]
        prior = '\n'.join(m['content'] for m in messages[:-1])
        self.assertIn('ThinkPad T14 Gen 4', prior)
        self.assertIn('Lenovo', prior)

    def test_fenced_json_reply_is_extracted(self):
        from conversation import reply_text
        fenced = '```json\n{"intent": "general_inquiry", "action": "answer", "reply": "1 + 1 = 2.", "evidence_ids": []}\n```'
        self.assertEqual(reply_text(fenced), '1 + 1 = 2.')
        self.assertEqual(reply_text('{"reply": "ok"}'), 'ok')
        self.assertEqual(reply_text('plain answer'), 'plain answer')

    def test_kb_render_has_leadin_and_snippet(self):
        from conversation import render_event
        event = {'tool': 'policy', 'args': {'query': 'mat khau'}, 'result': {
            'tool': 'policy', 'results': [
                {'title': 'Account Access Policy', 'content': 'Reset requires identity verification at the service desk.'}]}}
        text = render_event(event)
        self.assertIn('kết quả', text)
        self.assertIn('Account Access Policy', text)
        self.assertIn('identity verification', text)
