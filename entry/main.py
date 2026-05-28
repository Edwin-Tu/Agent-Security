import sys
import argparse
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from config import Config
from attack_classifier.attack_classifier import AttackClassifier
from attack_classifier.attack_taxonomy import AttackTaxonomy
from skill_router.skill_router import SkillRouter
from input_guard.defense_context import DefenseContext
from risk_scoring.session_memory import SessionMemory
from risk_scoring.risk_scoring_engine import RiskScoringEngine
from policy_engine.defense_policy_engine import DefensePolicyEngine
from asset_registry.protected_asset_registry import ProtectedAssetRegistry
from policy_engine.policy_builder import PolicyBuilder
from prompt_builder.protected_prompt_builder import ProtectedPromptBuilder
from asset_registry.secret_matcher import SecretMatcher
from leakage_verifier.leakage_verifier import LeakageVerifier
from input_normalization.token_expander import TokenExpander
from input_guard.input_guard import InputGuard
from output_guard.output_guard import OutputGuard
from prompt_builder.restricted_token_guard import RestrictedTokenGuard
from input_guard.authorization_guard import AuthorizationGuard
from llm_gateway.ollama_client import OllamaClient
from runtime_monitor.runtime_guard import RuntimeGuard
from runtime_monitor.interruption_handler import InterruptionHandler
from defensive_skills.base_skill import BaseSkill


def print_banner():
    print("\n" + "=" * 60)
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║       SecretGuard - Attack-Aware Defense Framework       ║")
    print("║    Local LLM Runtime Protection System                  ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print("=" * 60 + "\n")


def init_skills() -> SkillRouter:
    router = SkillRouter()
    for cls in BaseSkill.__subclasses__():
        try:
            router.register(cls())
        except Exception:
            pass
    return router


def ollama_mode(cfg: Config):
    print("Ollama Integration Mode\n")
    client = OllamaClient(ollama_url=cfg.ollama_url, model=cfg.model)
    print("Checking Ollama service...")
    if not client.is_available():
        print("Ollama service is not available (ollama serve)\n")
        return
    model = cfg.model
    models = client.list_models()
    if models and model not in models:
        model = models[0]
        print(f"Using model: {model}")
    client.model = model
    text = input("\nEnter prompt:\n> ")
    if not text.strip():
        return
    rt_guard = RuntimeGuard()
    result = client.generate(prompt=text, restricted_tokens=[])
    print("\n" + "-" * 60)
    if not result["success"]:
        print(f"Error: {result['reason']}")
    elif result["blocked"]:
        print(cfg.rejection_message)
        print(f"Blocked tokens: {', '.join(result['matched_tokens'])}")
    else:
        print(f"Safe output:\n{result['output']}")
    print()


def analyze_mode(cfg: Config):
    print("Multi-Layer Analysis Mode\n")
    router = init_skills()
    taxonomy = AttackTaxonomy()
    classifier = AttackClassifier()
    registry = ProtectedAssetRegistry()
    risk_engine = RiskScoringEngine()
    policy_engine = DefensePolicyEngine(threshold=cfg.threshold)
    leaker = LeakageVerifier()
    memory = SessionMemory()
    print(f"Loaded {len(taxonomy.all())} attack patterns, {len(registry.get_all())} protected assets, {len(BaseSkill.__subclasses__())} skills\n")
    while True:
        text = input("Enter text to analyze (or 'quit'):\n> ")
        if text.lower() in ("quit", "exit", "q"):
            break
        threats = classifier.classify_with_context(text, memory.get_history_texts())
        assets_result = registry.match(text)
        assets = assets_result.get("matches", []) if assets_result.get("matched") else []
        risk = risk_engine.compute(threats, assets, memory.get_history_texts())
        decision = policy_engine.decide(risk, {"accumulated_risk": memory.accumulated_risk})
        categories = [t["category"] for t in threats]
        skill_results = router.process(text, categories, {"history": memory.get_history_texts()})
        intercepted = any(sr["result"]["intervened"] for sr in skill_results)
        memory.record({"input": text, "blocked": intercepted, "analysis": {"threats": threats, "risk": risk, "decision": decision}})
        if decision["action"] == "block":
            memory.add_risk(3)
        elif decision["action"] in ("warn", "restrict"):
            memory.add_risk(1)

        print(f"\n  Threats: {[t['category'] for t in threats] or 'none'}")
        if assets:
            print("  [Protected Assets Detected]")
            for asset in assets:
                print(f"    - {asset.get('asset_id')} | {asset.get('name')} | risk={asset.get('risk_level')} | fragments={asset.get('matched_fragments')}")
        print(f"  Assets matched: {len(assets)}")
        print(f"  Risk: {risk['level']} ({risk['score']})")
        print(f"  Decision: {decision['action']}")
        print(f"  Skills intervened: {intercepted}")
        print(f"  Stats: {memory.stats()}\n")


def list_attacks_mode():
    print("Available Attack Patterns\n")
    taxonomy = AttackTaxonomy()
    for attack_id, config in taxonomy.all().items():
        print(f"  [{config.get('risk_level', '?').upper()}] {config.get('name', attack_id)}")
        print(f"        {config.get('description', '')}")
        print(f"        Mitigation: {config.get('mitigation', 'N/A')}\n")
    print(f"Total: {len(taxonomy.all())} attack patterns\n")


def list_assets_mode():
    print("Protected Assets\n")
    registry = ProtectedAssetRegistry()
    for asset in registry.get_all():
        print(f"  [{asset.get('risk_level', '?').upper()}] {asset.get('name', '?')} ({asset.get('type', '?')})")
        print(f"        Source: {asset.get('source', 'system')}")
        print(f"        Aliases: {', '.join(asset.get('aliases', []))}")
        print(f"        Protection: {', '.join(asset.get('protection_modes', []))}\n")
    print(f"Total: {len(registry.get_all())} protected assets\n")


def benchmark_mode():
    from benchmark.run_benchmark import run_benchmark
    run_benchmark()


def main():
    parser = argparse.ArgumentParser(
        description="SecretGuard - Attack-Aware Defensive Skill Framework for Local LLMs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 main.py --analyze         Multi-layer analysis (no Ollama needed)
  python3 main.py --list-attacks    List 20 attack patterns
  python3 main.py --list-assets     List protected assets
  python3 main.py --benchmark       Run component tests
  python3 main.py --ollama          Real-time Ollama protection
  python3 main.py                   Interactive menu
        """,
    )
    parser.add_argument("--ollama", action="store_true", help="Ollama integration mode")
    parser.add_argument("--analyze", action="store_true", help="Multi-layer analysis mode")
    parser.add_argument("--list-attacks", action="store_true", help="List attack patterns")
    parser.add_argument("--list-assets", action="store_true", help="List protected assets")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark")
    args = parser.parse_args()

    cfg = Config()
    print_banner()

    if args.ollama:
        ollama_mode(cfg)
    elif args.analyze:
        analyze_mode(cfg)
    elif args.list_attacks:
        list_attacks_mode()
    elif args.list_assets:
        list_assets_mode()
    elif args.benchmark:
        benchmark_mode()
    else:
        print("Select mode:\n")
        print("  1. Analyze (multi-layer)")
        print("  2. List Attacks")
        print("  3. List Assets")
        print("  4. Benchmark")
        print("  5. Ollama Integration")
        print("  0. Exit\n")
        choice = input("Choice (0-5): ").strip()
        if choice == "1":
            analyze_mode(cfg)
        elif choice == "2":
            list_attacks_mode()
        elif choice == "3":
            list_assets_mode()
        elif choice == "4":
            benchmark_mode()
        elif choice == "5":
            ollama_mode(cfg)
        elif choice == "0":
            print("Exiting.\n")
        else:
            print("Invalid choice.\n")


if __name__ == "__main__":
    main()
