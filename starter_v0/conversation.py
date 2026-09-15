"""Shared, evidence-first conversation state for the Streamlit chat and demos."""
from __future__ import annotations

import copy
import json
import re
import uuid
from datetime import datetime, timezone

from agent import HelpdeskAgent
from providers.base import ToolCall
from tools import TOOL_FUNCTIONS


def now():
    return datetime.now(timezone.utc).isoformat()


def reply_text(text):
    raw = (text or '').strip()
    candidate = re.sub(r'^```(?:json)?\s*|\s*```$', '', raw, flags=re.IGNORECASE).strip()
    for attempt in (candidate, raw):
        try:
            value = json.loads(attempt)
            if isinstance(value, dict) and 'reply' in value:
                return str(value['reply']).strip() or 'Không có phản hồi từ mô hình. Hãy thử lại.'
        except (ValueError, TypeError):
            continue
    block = re.search(r'\{.*\}', candidate, re.DOTALL)
    if block:
        try:
            value = json.loads(block.group(0))
            if isinstance(value, dict) and 'reply' in value:
                return str(value['reply']).strip() or 'Không có phản hồi từ mô hình. Hãy thử lại.'
        except (ValueError, TypeError):
            pass
    return candidate or raw or 'Không có phản hồi từ mô hình. Hãy thử lại.'


def render_event(event):
    result = event.get('result', {})
    name = event['tool']
    if result.get('error'):
        return f"**{name} — lỗi: `{result['error']}`.** {result.get('message', '')} Chưa hoàn thành thao tác này."
    if result.get('awaiting_user'):
        return result.get('question', 'Hãy xác nhận nội dung ticket bên dưới.')
    if name == 'check_service_status':
        return f"**{result.get('service')} / {result.get('environment')}: {result.get('status')}**\n\n{result.get('summary', '')}\n\nSnapshot: {result.get('checked_at', 'unknown')}"
    if name == 'inspect_device':
        device = result.get('device', {})
        public_identity = f"{device.get('manufacturer', '')} · {device.get('model', '')}"
        return f"**{result.get('asset_id')} · {result.get('check')}**\n{public_identity}\n\n```json\n{json.dumps(result.get('diagnostics'), ensure_ascii=False, indent=2)}\n```\nSnapshot: {result.get('snapshot_at', 'unknown')}"
    if name == 'format_incident_report':
        return result.get('markdown', '')
    if name in {'search_kb', 'policy'}:
        hits = result.get('results', [])
        if not hits:
            return f'**{name}:** Không tìm thấy tài liệu khớp.'
        label = 'Tài liệu chính sách liên quan' if name == 'policy' else 'Bài hướng dẫn liên quan'
        parts = [f'**{label} ({len(hits)} kết quả):**']
        for hit in hits:
            body = str(hit.get('content') or hit.get('excerpt') or '').strip()
            entry = f"- **{hit.get('title', 'Tài liệu')}**"
            if body:
                summary = body[:500] + ('…' if len(body) > 500 else '')
                entry += f": {summary}"
            parts.append(entry)
        return '\n\n'.join(parts)
    if name == 'create_ticket' and result.get('status') == 'created':
        return f"Đã ghi ticket mô phỏng **{result['ticket_id']}** vào file local."
    return f"**{name} — kết quả thực thi:**\n```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```"


class Conversation:
    def __init__(self, provider, prompt, tools, model, version):
        self.provider, self.prompt, self.tools, self.model = provider, prompt, tools, model
        self.history = []
        self.pending_ticket = None
        self.transcript = {'transcript_id': uuid.uuid4().hex, **version,
                           'provider': 'gemini', 'model': model, 'created_at': now(),
                           'runtime': 'single routing round with verified result rendering and UI write confirmation',
                           'turns': []}

    def _execute(self, call):
        if call.name == 'create_ticket':
            self.pending_ticket = {key: copy.deepcopy(value) for key, value in call.args.items() if key != 'confirmed'}
            return {'tool': call.name, 'args': call.args,
                    'result': {'status': 'needs_confirmation', 'awaiting_user': True,
                               'question': 'Chưa ghi dữ liệu. Rà soát payload rồi bấm Xác nhận ghi ticket.',
                               'proposed_payload': copy.deepcopy(self.pending_ticket)}}
        func = TOOL_FUNCTIONS.get(call.name)
        try:
            result = func(**call.args) if func else {'error': 'unknown_tool'}
        except Exception as exc:
            result = {'error': type(exc).__name__, 'message': str(exc)}
        return {'tool': call.name, 'args': call.args, 'result': result}

    def _save(self, turn):
        turn['ended_at'] = now()
        self.transcript['turns'].append(turn)
        self.transcript['updated_at'] = now()
        self.history.extend([{'role': 'user', 'content': turn['user']},
                             {'role': 'assistant', 'content': turn['assistant_text']}])
        return turn

    def respond(self, user_text):
        # Any new message invalidates the previous review button/payload.
        self.pending_ticket = None
        turn = {'user': user_text, 'started_at': now(), 'tool_events': [], 'tool_calls': []}
        try:
            agent = HelpdeskAgent(self.provider, system_prompt=self.prompt, tools=self.tools,
                                  model=self.model, tool_executor=self._execute)
            run = agent.run([*self.history, {'role': 'user', 'content': user_text}])
            turn['tool_calls'] = [{'name': c.name, 'args': c.args} for c in run.tool_calls]
            turn['tool_events'] = run.tool_results
            turn['model_text_before_execution'] = run.text
            events = run.tool_results
            rendered = [render_event(e) for e in events]
            turn['assistant_text'] = '\n\n'.join(rendered) if events else reply_text(run.text)
            status = ('tool_error' if any(e.get('result', {}).get('error') for e in events)
                      else 'waiting_for_user' if any(e.get('result', {}).get('awaiting_user') for e in events)
                      else 'answered')
            if events and status == 'answered' and run.text:
                closing = reply_text(run.text)
                if closing not in turn['assistant_text']:
                    rendered.append(closing)
                    turn['assistant_text'] = '\n\n'.join(rendered)
            turn['status'] = status
        except Exception as exc:
            turn.update(status='provider_error', error=f'{type(exc).__name__}: {exc}',
                        assistant_text='Gemini chưa trả lời được. Không xác nhận hoàn thành; hãy thử lại.')
        return self._save(turn)

    def confirm_ticket(self):
        if self.pending_ticket is None:
            raise ValueError('No pending ticket to confirm')
        payload = {**self.pending_ticket, 'confirmed': True}
        self.pending_ticket = None  # Consume once, including tool failures.
        try:
            result = TOOL_FUNCTIONS['create_ticket'](**payload)
        except Exception as exc:
            result = {'error': type(exc).__name__, 'message': str(exc)}
        event = {'tool': 'create_ticket', 'args': payload, 'result': result}
        return self._save({'user': '[UI: xác nhận đúng payload đã hiển thị]', 'started_at': now(),
                           'status': 'tool_error' if result.get('error') else 'answered',
                           'tool_calls': [{'name':'create_ticket', 'args':payload}],
                           'tool_events': [event], 'assistant_text': render_event(event),
                           'authorization': 'explicit UI button; pending payload consumed once'})
