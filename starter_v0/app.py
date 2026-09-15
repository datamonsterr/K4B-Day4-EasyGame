"""Run: python -m streamlit run app.py"""
import json
import os
from pathlib import Path

import streamlit as st

from conversation import Conversation
from env_loader import load_lab_env
from providers.gemini_provider import GeminiProvider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).resolve().parent
load_lab_env(ROOT)
MODEL = 'gemini-3.5-flash-lite'
VERSION = (ROOT / 'artifacts/CURRENT_VERSION').read_text().strip() if (ROOT / 'artifacts/CURRENT_VERSION').exists() else 'v3'
st.set_page_config(page_title='IT Helpdesk', page_icon='🛠️', layout='wide', initial_sidebar_state='collapsed')

GREETING = 'Xin chào, bạn cần trợ giúp gì liên quan tới IT?'

st.markdown(
    '<style>'
    '.stButton>button,[data-testid="stDownloadButton"]>button,[data-testid="baseButton-secondary"]'
    '{border-radius:0.75rem;}'
    '[data-testid="stSidebar"]>div{border-radius:0 0 1rem 1rem;}'
    '[data-testid="stExpander"],.stJson{border-radius:0.75rem;}'
    '[data-testid="stMainBlockContainer"]{padding-bottom:0.4rem;}'
    '[data-testid="stChatInput"]{position:relative;border-radius:0.75rem;}'
    '[data-testid="stChatInput"]::after{content:"gemini/' + MODEL + '";'
    'position:absolute;right:3.6rem;top:50%;transform:translateY(-50%);'
    'color:#8A8A8A;font-size:0.72rem;pointer-events:none;}'
    '[data-testid="stBottom"]>div{max-width:820px;}'
    '.stChatMessage,[data-testid="stExpander"],.stJson,[data-testid="stMarkdownContainer"]{overflow-anchor:none;}'
    '#chat-anchor{height:1px;overflow-anchor:auto;}'
    '</style>',
    unsafe_allow_html=True,
)


def new_conversation():
    prompt = ROOT / 'artifacts/system_prompt.md'
    declarations = ROOT / 'artifacts/tools.yaml'
    version = artifact_version_dict(build_artifact_version(VERSION, prompt, declarations))
    return Conversation(GeminiProvider(default_model=MODEL), prompt.read_text(),
                        to_openai_tools(load_tool_declarations(declarations)), MODEL, version)


def show_event(event):
    result = event.get('result', {})
    failed = bool(result.get('error') or event.get('error'))
    state = 'Lỗi' if failed else 'Chờ xác nhận' if result.get('awaiting_user') else 'Kết quả'
    with st.expander(f"{event.get('tool', 'unknown')} · {state}", expanded=failed):
        st.caption('Đầu vào')
        st.json(event.get('args', {}))
        st.caption('Kết quả thực thi')
        st.json(result or event)
        if failed:
            st.error(f"Công cụ chưa hoàn thành: {result.get('error', event.get('error'))}")


def save_chat(chat):
    path = Path(os.getenv('EASYGAME_TRANSCRIPTS_DIR', str(ROOT / 'transcripts'))) / f"{chat.transcript['transcript_id']}.transcript.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(chat.transcript, ensure_ascii=False, indent=2), encoding='utf-8')


if 'conversation' not in st.session_state:
    st.session_state.conversation = new_conversation()
chat = st.session_state.conversation

with st.sidebar:
    nav = st.radio('Nội dung', ['💬 Chat', '📊 Runs & evidence'], horizontal=True,
                   label_visibility='collapsed')
    if st.button('Hội thoại mới', use_container_width=True):
        st.session_state.conversation = new_conversation()
        st.rerun()
    st.download_button('Tải transcript JSON', json.dumps(chat.transcript, ensure_ascii=False, indent=2),
                       file_name=f"{chat.transcript['transcript_id']}.transcript.json", mime='application/json',
                       use_container_width=True)
    st.caption('Chỉ dùng dữ liệu giả lập. Tool trace lưu cả lỗi. Ticket được ghi local sau khi bấm xác nhận payload.')

if nav == '💬 Chat':
    chat_area = st.container()
    with chat_area:
        if not chat.transcript['turns']:
            st.markdown(f"<h2 style='text-align:center;margin-top:3rem;font-weight:600'>{GREETING}</h2>", unsafe_allow_html=True)
        for turn in chat.transcript['turns']:
            with st.chat_message('user'):
                st.write(turn['user'])
            with st.chat_message('assistant'):
                st.markdown(turn.get('assistant_text', ''))
                if turn.get('error'):
                    st.error(turn['error'])
                for event in turn.get('tool_events', []):
                    show_event(event)
                st.caption(f"{turn['status']} · {turn.get('ended_at', '')}")
        if chat.pending_ticket is not None:
            st.warning('Rà soát ticket. Một tin nhắn mới sẽ hủy payload đang chờ này.')
            st.json(chat.pending_ticket)
            yes, no = st.columns(2)
            if yes.button('Xác nhận ghi ticket', type='primary', use_container_width=True):
                chat.confirm_ticket()
                save_chat(chat)
                st.rerun()
            if no.button('Hủy ticket', use_container_width=True):
                chat.pending_ticket = None
                chat._save({'user': '[UI: hủy ticket]', 'started_at': '', 'status': 'cancelled',
                            'assistant_text': 'Đã hủy. Không ghi ticket.', 'tool_calls': [], 'tool_events': []})
                save_chat(chat)
                st.rerun()
        st.markdown('<div id="chat-anchor"></div>', unsafe_allow_html=True)

    user_text = st.chat_input('Nhập yêu cầu IT Helpdesk…', submit_mode='disable')
    if user_text:
        with st.chat_message('user'):
            st.write(user_text)
        with st.chat_message('assistant'):
            with st.status('Đang suy nghĩ · chọn công cụ với Gemini…', expanded=True) as status:
                st.write('Đang xử lý yêu cầu và kiểm tra kết quả công cụ.')
                turn = chat.respond(user_text)
                for event in turn.get('tool_events', []):
                    show_event(event)
                failed = turn['status'] in {'tool_error', 'provider_error'}
                status.update(label='Có lỗi — xem trace' if failed else 'Đã xử lý', state='error' if failed else 'complete')
            st.markdown(turn['assistant_text'])
        save_chat(chat)
        st.rerun()

else:
    st.markdown('### 📊 Runs & evidence')
    paths = sorted((ROOT / 'runs').glob('*.json'), reverse=True)
    if not paths:
        st.info('Chạy run_eval.py để tạo evidence.')
    else:
        selected = st.selectbox('Run đã lưu', paths, format_func=lambda p: p.name)
        run = json.loads(selected.read_text())
        summary = run['summary']
        valid = summary['provider_error_cases'] == 0 and summary['measured_cases'] == summary['total_cases']
        if not valid:
            st.error('Run chưa đo đủ case; không dùng điểm này làm kết quả hợp lệ.')
        a, b = st.columns(2)
        a.metric('Routing + args PASS', f"{summary['passed_cases']}/{summary['total_cases']}")
        b.metric('Provider errors', summary['provider_error_cases'])
        tool_errors = sum(bool(e.get('result', {}).get('error') or e.get('error')) for case in run['results'] for e in case.get('tool_results', []))
        st.caption(f"{run['artifact_version']} · {run['model']} · {run['generated_at']} · tool errors: {tool_errors}")
        case = st.selectbox('Tình huống', run['results'], format_func=lambda x: x['id'])
        st.write(case.get('input'))
        st.json(case['result'])
        for event in case.get('tool_results', []):
            show_event(event)
        st.download_button('Tải run JSON', selected.read_bytes(), file_name=selected.name, mime='application/json',
                           use_container_width=True)
