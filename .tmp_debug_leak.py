from config import Config
from entry.secretguard_pipeline import SecretGuardPipeline
from llm_gateway.model_response import LLMResponse
from event_logger.event_logger import EventLogger

class FakeLeakClient:
    def generate(self, prompt, model, options=None):
        return LLMResponse(success=True, text="picoCTF{example_flag}", model=model or "test", done=True)

p=SecretGuardPipeline(Config(), llm_client=FakeLeakClient())
# ensure registry contains the asset that will be leaked
p.registry.add_asset({"asset_id": "a_flag", "name": "CTF Flag", "type": "exact", "value": "example_flag", "risk_level": "high"})
log='logs/tmp_guard_events.jsonl'
p.event_logger=EventLogger(log)
res=p.handle('normal question', model='mock', dry_run=False)
print('result:', res)
with open(log,'r',encoding='utf-8') as f:
    print('last event:', f.readlines()[-1])

# direct verify
from leakage_verifier.leakage_verifier import LeakageVerifier
lv = LeakageVerifier()
assets = p.registry.get_all()
print('registry assets:', assets)
vr = lv.verify('picoCTF{example_flag}', assets)
print('verify result:', vr)
