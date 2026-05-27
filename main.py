import sys
import argparse
from pathlib import Path

_project_root = Path(__file__).resolve().parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from config import Config
from core.attack_classifier import AttackClassifier
from core.defense_router import DefenseRouter
from core.defense_context import DefenseContext
from core.risk_score import RiskScore
from core.session_memory import SessionMemory
from core.token_expander import TokenExpander
from attacks.attack_taxonomy import AttackTaxonomy
from guards.restricted_token_guard import RestrictedTokenGuard
from guards.risk_level_guard import RiskLevelGuard
from guards.input_guard import InputGuard
from guards.output_guard import OutputGuard
from runtime.ollama_client import OllamaClient
from runtime.stream_monitor import StreamMonitor
from runtime.runtime_guard import RuntimeGuard
from skills.direct_request_skill import DirectRequestSkill
from skills.role_play_skill import RolePlaySkill
from skills.instruction_override_skill import InstructionOverrideSkill
from skills.system_prompt_extraction_skill import SystemPromptExtractionSkill
from skills.encoding_bypass_skill import EncodingBypassSkill
from skills.partial_disclosure_skill import PartialDisclosureSkill
from skills.translation_bypass_skill import TranslationBypassSkill
from skills.structured_output_skill import StructuredOutputSkill
from skills.log_access_skill import LogAccessSkill
from skills.multi_turn_probe_skill import MultiTurnProbeSkill
from skills.policy_confusion_skill import PolicyConfusionSkill
from skills.indirect_prompt_injection_skill import IndirectPromptInjectionSkill
from skills.format_smuggling_skill import FormatSmugglingSkill
from skills.output_constraint_bypass_skill import OutputConstraintBypassSkill
from skills.reasoning_trap_skill import ReasoningTrapSkill
from skills.refusal_suppression_skill import RefusalSuppressionSkill
from skills.persona_override_skill import PersonaOverrideSkill
from skills.data_reconstruction_skill import DataReconstructionSkill
from skills.cross_language_injection_skill import CrossLanguageInjectionSkill
from skills.homoglyph_obfuscation_skill import HomoglyphObfuscationSkill


def print_banner():
    print("\n" + "=" * 60)
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║       SecretGuard - Multi-Layer Defense System       ║")
    print("║    Runtime Guardrail for Local LLMs (Ollama)             ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print("=" * 60 + "\n")


def init_router(cfg: Config) -> DefenseRouter:
    router = DefenseRouter()
    router.context.set_threshold(cfg.threshold)
    router.register_guard(InputGuard())
    router.register_guard(OutputGuard())
    router.register_guard(RestrictedTokenGuard())
    router.register_guard(RiskLevelGuard(threshold=cfg.threshold))
    skills = [
        DirectRequestSkill(), RolePlaySkill(), InstructionOverrideSkill(),
        SystemPromptExtractionSkill(), EncodingBypassSkill(), PartialDisclosureSkill(),
        TranslationBypassSkill(), StructuredOutputSkill(), LogAccessSkill(),
        MultiTurnProbeSkill(), PolicyConfusionSkill(), IndirectPromptInjectionSkill(),
        FormatSmugglingSkill(), OutputConstraintBypassSkill(), ReasoningTrapSkill(),
        RefusalSuppressionSkill(), PersonaOverrideSkill(), DataReconstructionSkill(),
        CrossLanguageInjectionSkill(), HomoglyphObfuscationSkill(),
    ]
    for s in skills:
        router.register_skill(s)
    return router


def init_runtime_guard(cfg: Config) -> RuntimeGuard:
    return RuntimeGuard(threshold=cfg.threshold)


def _resolve_model(client: OllamaClient, preferred: str = "mistral") -> str:
    models = client.list_models()
    if preferred in models:
        return preferred
    if models:
        print(f"  model '{preferred}' not available, using '{models[0]}'")
        return models[0]
    return preferred


def ollama_mode(cfg: Config):
    print("Ollama Integration Mode\n")
    client = OllamaClient(ollama_url=cfg.ollama_url, model=cfg.model)
    print("Checking Ollama service...")
    if not client.is_available():
        print("Ollama service is not available")
        print("Please ensure Ollama is running: ollama serve\n")
        return
    print("Ollama service is available")
    model = _resolve_model(client, cfg.model)
    client.model = model
    print(f"Using model: {model}\n")
    print("Enter your prompt:")
    raw_input = input("> ")
    if not raw_input.strip():
        print("Empty input, exiting.\n")
        return
    rt_guard = init_runtime_guard(cfg)
    result = client.generate(prompt=raw_input, restricted_tokens=rt_guard.token_guard.restricted_tokens)
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
    router = init_router(cfg)
    taxonomy = AttackTaxonomy()
    print(f"Loaded {len(taxonomy.all())} attack patterns from taxonomy")
    print()
    while True:
        text = input("Enter text to analyze (or 'quit' to exit):\n> ")
        if text.lower() in ("quit", "exit", "q"):
            break
        result = router.process(text)
        print()
        if result["blocked"]:
            print(f"Blocked: {result['analysis']['risk']['level']}")
            print(f"Threats: {[t['category'] for t in result['analysis']['threats']]}")
        else:
            print("Passed all defense layers")
        print(f"Stats: {router.memory.stats()}")
        print()


def list_attacks_mode():
    print("Available Attack Patterns\n")
    taxonomy = AttackTaxonomy()
    attacks = taxonomy.all()
    for attack_id, config in attacks.items():
        print(f"  [{config.get('risk_level', '?').upper()}] {config.get('name', attack_id)}")
        print(f"        {config.get('description', '')}")
        print(f"        Mitigation: {config.get('mitigation', 'N/A')}")
        print()
    print(f"Total: {len(attacks)} attack patterns\n")


def benchmark_mode():
    print("Running Benchmark...\n")
    from benchmark.run_benchmark import run_benchmark
    run_benchmark()


def main():
    parser = argparse.ArgumentParser(
        description="SecretGuard - Multi-Layer Defense System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 main.py --ollama          Ollama real-time protection
  python3 main.py --analyze         Multi-layer analysis mode
  python3 main.py --list-attacks    List attack patterns
  python3 main.py --benchmark       Run benchmark
  python3 main.py                   Interactive menu
        """,
    )
    parser.add_argument("--ollama", action="store_true", help="Ollama integration mode")
    parser.add_argument("--analyze", action="store_true", help="Multi-layer analysis mode")
    parser.add_argument("--list-attacks", action="store_true", help="List attack patterns")
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
    elif args.benchmark:
        benchmark_mode()
    else:
        print("Select mode:\n")
        print("  1. Ollama Integration (real-time protection)")
        print("  2. Multi-Layer Analysis")
        print("  3. List Attack Patterns")
        print("  4. Run Benchmark")
        print("  0. Exit\n")
        choice = input("Choice (0-4): ").strip()
        if choice == "1":
            ollama_mode(cfg)
        elif choice == "2":
            analyze_mode(cfg)
        elif choice == "3":
            list_attacks_mode()
        elif choice == "4":
            benchmark_mode()
        elif choice == "0":
            print("Exiting.\n")
        else:
            print("Invalid choice.\n")


if __name__ == "__main__":
    main()
