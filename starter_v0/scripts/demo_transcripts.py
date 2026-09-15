"""Run five live Gemini demonstrations through the exact Streamlit conversation runtime."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from conversation import Conversation
from env_loader import load_lab_env
from providers.gemini_provider import GeminiProvider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


def main():
    load_lab_env(ROOT)
    version_label = (ROOT / 'artifacts/CURRENT_VERSION').read_text().strip()
    prompt, tools = ROOT / 'artifacts/system_prompt.md', ROOT / 'artifacts/tools.yaml'
    version = artifact_version_dict(build_artifact_version(version_label, prompt, tools))
    scenarios = {
        'normal': ['Kiểm tra trạng thái VPN production.'],
        'clarification_multiturn': ['Kiểm tra Wi-Fi trên laptop của mình.', 'Mã máy là LT-240, kiểm tra network nhé.', 'Giữ máy đó nhưng kiểm tra security.'],
        'tool_errors': ['Kiểm tra tổng thể máy LT-999999.', 'Tìm thông số Dell UltraSharp U2723QE trên web.'],
        'write_confirmation': ['Tạo ticket lỗi VPN trên LT-204 mức high.', 'Tôi xác nhận ticket lỗi VPN trên LT-204 mức high.'],
        'cancellation': ['Tạo ticket lỗi máy in PR-404 mức medium.', 'Hủy đi, không tạo ticket nữa.'],
    }
    out = ROOT / 'transcripts/demo'
    out.mkdir(parents=True, exist_ok=True)
    for name, inputs in scenarios.items():
        chat = Conversation(GeminiProvider(default_model='gemini-3.5-flash-lite'), prompt.read_text(),
                            to_openai_tools(load_tool_declarations(tools)), 'gemini-3.5-flash-lite', version)
        chat.transcript['evidence_kind'] = 'live scripted conversation; real Gemini responses and local tools'
        chat.transcript['scenario'] = name
        before = {p.name for p in (ROOT / 'tickets').glob('*.json')}
        for user_text in inputs:
            turn = chat.respond(user_text)
            print(name, turn['status'], [e['tool'] for e in turn['tool_events']], flush=True)
            time.sleep(5)
        if name == 'write_confirmation' and chat.pending_ticket is not None:
            turn = chat.confirm_ticket()
            turn['authorization'] = 'script explicitly invokes same reviewed-payload confirmation method as UI button'
            print(name, 'confirmed', turn['status'], flush=True)
        after = {p.name for p in (ROOT / 'tickets').glob('*.json')}
        created = sorted(after-before)
        chat.transcript['side_effect_audit'] = {'new_ticket_files': created,
            'ticket_payloads': [json.loads((ROOT/'tickets'/p).read_text()) for p in created],
            'scope': 'local mock ticket directory; no production ticketing integration'}
        target = out / f'{version_label}_{name}_{chat.transcript["transcript_id"]}.transcript.json'
        target.write_text(json.dumps(chat.transcript, ensure_ascii=False, indent=2), encoding='utf-8')
        print(target, flush=True)


if __name__ == '__main__':
    main()
