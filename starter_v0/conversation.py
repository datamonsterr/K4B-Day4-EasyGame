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
        return result.get('question', 'Hãy xác nhận nội dung ticket bên dưới.').replace('\\n', '\n')
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
    if name == 'search_device_info':
        items = result.get('items', [])
        if not items:
            return f"**{name}:** Không có kết quả web nào được trả về."
        lines = [f"**Kết quả web công khai cho {result.get('manufacturer')} {result.get('model')}:**"]
        for item in items[:5]:
            lines.append(f"- [{item.get('title', 'Liên kết')}]({item.get('url', '#')}) — {item.get('source', '')}")
        lines.append(f"\n_{result.get('external_data_notice', '')}_")
        return '\n'.join(lines)
    if name == 'create_ticket' and result.get('status') == 'created':
        return f"Đã ghi ticket mô phỏng **{result['ticket_id']}** vào file local."
    return f"**{name} — kết quả thực thi:**\n```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```"


class Conversation:
    MAX_ROUNDS = 5
    MAX_CALLS = 12

    def __init__(self, provider, prompt, tools, model, version):
        self.provider, self.prompt, self.tools, self.model = provider, prompt, tools, model
        self.history = []
        self.pending_ticket = None
        self.transcript = {'transcript_id': uuid.uuid4().hex, **version,
                           'provider': 'gemini', 'model': model, 'created_at': now(),
                           'runtime': 'ReAct loop (chat -> tool -> observe -> reason -> final) with loop safeguards and UI write confirmation',
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

    @staticmethod
    def _extract_docs(events):
        docs, by_key = [], {}
        for event in events:
            if event.get('tool') not in {'search_kb', 'policy'}:
                continue
            for hit in event.get('result', {}).get('results', []):
                doc = {'title': str(hit.get('title') or hit.get('doc_id') or 'Tài liệu'),
                       'file': str(hit.get('article_id') or hit.get('doc_id') or 'document'),
                       'section': str(hit.get('section') or ''),
                       'content': str(hit.get('content') or hit.get('facts') or '')}
                key = doc['file']
                if key in by_key:
                    existing = by_key[key]
                    if doc['content'] and doc['content'] not in existing['content']:
                        existing['content'] += f"\n\n## {doc['section']}\n{doc['content']}" if doc['section'] else f"\n\n{doc['content']}"
                    continue
                by_key[key] = doc
                docs.append(doc)
        return docs

    def respond(self, user_text):
        # Any new message invalidates the previous review button/payload.
        self.pending_ticket = None
        turn = {'user': user_text, 'started_at': now(), 'rounds': [], 'tool_events': [], 'tool_calls': []}
        messages = [*self.history, {'role': 'user', 'content': user_text}]
        seen_calls, status, final_text = [], 'answered', None
        try:
            agent = HelpdeskAgent(self.provider, system_prompt=self.prompt, tools=self.tools,
                                  model=self.model, tool_executor=self._execute)
            for round_index in range(1, self.MAX_ROUNDS + 1):
                run = agent.run(messages)
                events = run.tool_results
                turn['rounds'].append({'round': round_index, 'model_text': run.text,
                                       'tool_calls': [{'name': c.name, 'args': c.args} for c in run.tool_calls],
                                       'tool_results': events})
                turn['tool_calls'] += turn['rounds'][-1]['tool_calls']
                turn['tool_events'] += events
                if not run.tool_calls:
                    final_text = reply_text(run.text)
                    status = 'answered'
                    break
                if any(e.get('result', {}).get('awaiting_user') for e in events):
                    status = 'waiting_for_user'
                    break
                if len(turn['tool_calls']) >= self.MAX_CALLS:
                    status, final_text = 'answered', f"Đã dừng sau {round_index} vòng ReAct (giới hạn {self.MAX_CALLS} lần gọi tool). Kết quả đã thu được nằm trong trace."
                    break
                signatures = [(c.name, json.dumps(c.args, sort_keys=True, ensure_ascii=False)) for c in run.tool_calls]
                if all(e.get('result', {}).get('error') for e in events) and round_index >= 2:
                    status = 'tool_error'
                    final_text = 'Các lần gọi tool liên tiếp đều lỗi — dừng vòng ReAct để tránh lặp vô hạn. Xem chi tiết lỗi trong trace.'
                    break
                if any(sig in seen_calls for sig in signatures) or len(signatures) != len(set(signatures)):
                    status = 'answered'
                    final_text = 'Phát hiện lời gọi tool lặp lại — dừng vòng ReAct và trả lời từ kết quả đã có trong trace.'
                    break
                seen_calls += signatures
                messages = messages + [
                    {'role': 'assistant',
                     'content': (run.text or 'Tôi sẽ gọi các công cụ đã nêu.') +
                                f"\nTOOL_CALLS_JSON: {json.dumps(turn['rounds'][-1]['tool_calls'], ensure_ascii=False)}"},
                    {'role': 'user',
                     'content': 'TOOL_OBSERVATIONS_JSON:\n' + json.dumps(events, ensure_ascii=False, default=str)[:20000] +
                                '\n\nSuy luận tiếp từ quan sát trên (ReAct). Nếu đủ dữ liệu, trả lời bằng JSON bốn trường cuối cùng. '
                                'Nếu thiếu, gọi đúng một bước tool kế tiếp. Không lặp lại một lời gọi giống hệt trước đó.'},
                ]
            else:
                status, final_text = 'answered', f"Đã dừng sau {self.MAX_ROUNDS} vòng ReAct (giới hạn vòng). Kết quả có trong trace."
        except Exception as exc:
            turn.update(status='provider_error', error=f'{type(exc).__name__}: {exc}',
                        assistant_text='Gemini chưa trả lời được. Không xác nhận hoàn thành; hãy thử lại.')
            return self._save(turn)

        rendered = [render_event(e) for e in turn['tool_events']]
        turn['docs'] = self._extract_docs(turn['tool_events'])
        has_error = any(e.get('result', {}).get('error') for e in turn['tool_events'])
        parts = []
        if final_text:
            parts.append(final_text)
        parts += rendered
        turn['assistant_text'] = '\n\n'.join(parts) or 'Không có phản hồi từ mô hình. Hãy thử lại.'
        if has_error:
            turn['status'] = 'tool_error'
        else:
            turn['status'] = status
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
