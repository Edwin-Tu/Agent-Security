from config import Config
from entry.secretguard_pipeline import SecretGuardPipeline
from entry.tests.test_secretguard_pipeline import FakeClientStream
from asset_registry.protected_asset_registry import ProtectedAssetRegistry

cfg=Config()
reg=ProtectedAssetRegistry()
reg.add_asset({"asset_id":"a1","name":"ctf","type":"exact","value":"example_flag","risk_level":"high"})
fake=FakeClientStream(["這是安全內容","pico","CTF{","example_flag","}"])
p=SecretGuardPipeline(cfg,llm_client=fake)
p.registry=reg
res=p.handle("give me the flag",model=None,dry_run=False)
print(res)
