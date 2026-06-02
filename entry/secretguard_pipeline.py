import re
import uuid
from datetime import datetime

from config import Config
from input_normalization.input_normalizer import normalize_input
from asset_registry.protected_asset_registry import ProtectedAssetRegistry
from input_guard.input_guard import InputGuard
from attack_classifier.attack_classifier import AttackClassifier
from risk_scoring.risk_scoring_engine import RiskScoringEngine
from policy_engine.defense_policy_engine import DefensePolicyEngine
from prompt_builder.protected_prompt_builder import ProtectedPromptBuilder
from prompt_builder.prompt_build_request import PromptBuildRequest
from output_guard.output_guard import OutputGuard
from leakage_verifier.leakage_verifier import LeakageVerifier
from llm_gateway.base_provider import ProviderError
from runtime_monitor.stream_monitor import StreamMonitor
from entry.errors import log_api_event
from entry.guard_result import GuardDecision
from entry.pipeline_context import PipelineContext
from event_logger.event_logger import EventLogger

SIMPLIFIED_RULES = [
    (r"\bapi\s*key\b|\btoken\b|\bpassword\b|\bsecret\b|\bflag\b", "direct_secret_request", 80),
    (r"\bsystem\s*prompt\b|\bdeveloper\s*message\b", "system_prompt_extraction", 75),
    (r"\bignore\s+previous\s+instructions?\b|\bignore\s+all\s+(above|prior)\b", "instruction_override", 75),
    (r"\bbase64\b|\bencode\b|\bdecode\b", "encoding_bypass", 60),
]


class SecretGuardPipeline:
    def __init__(self, config: Config | None = None):
        self.cfg = config or Config()
        self.registry = ProtectedAssetRegistry()
        self.input_guard = InputGuard()
        self.classifier = AttackClassifier()
        self.risk_engine = RiskScoringEngine()
        self.policy_engine = DefensePolicyEngine(threshold=self.cfg.threshold)
        self.event_logger = EventLogger()

    def _apply_simplified_rules(self, text: str) -> tuple[str | None, int]:
        text_lower = text.lower()
        for pattern, attack_type, risk_score in SIMPLIFIED_RULES:
            if re.search(pattern, text_lower):
                return attack_type, risk_score
        return None, 0

    @staticmethod
    def _generate_event_id() -> str:
        now = datetime.now()
        rand = uuid.uuid4().hex[:6]
        return f"evt_{now.strftime('%Y%m%d_%H%M%S')}_{rand}"

    def chat(self, request, provider) -> "ChatResponse":
        from api.schemas import ChatResponse

        decision = self.analyze(
            prompt=request.prompt,
            session_id=request.session_id,
            role=request.role,
        )

        if not decision.allowed or decision.action == "block":
            event_id = self._generate_event_id()
            log_api_event(
                route="/v1/chat",
                model=request.model,
                prompt=request.prompt,
                session_id=request.session_id,
                action="block",
                allowed=False,
                risk_score=decision.risk_score,
                attack_type=decision.attack_type,
                blocked_reason=decision.reason,
                provider_called=False,
                matched_assets=decision.matched_assets,
                logger=self.event_logger,
            )
            return ChatResponse(
                allowed=False,
                action="block",
                risk_score=decision.risk_score,
                attack_type=decision.attack_type or "unknown",
                response=Config().rejection_message,
                blocked_reason=decision.reason,
                event_id=event_id,
            )

        pbr = PromptBuildRequest(
            original_prompt=request.prompt,
            normalized_prompt=request.prompt,
            policy_action=decision.action.upper(),
            risk_score=decision.risk_score,
            attack_categories=[decision.attack_type] if decision.attack_type else [],
            protected_assets=decision.matched_assets,
        )
        builder = ProtectedPromptBuilder()
        built = builder.build(pbr)
        final_prompt = built.final_prompt

        try:
            raw_output = provider.generate(
                model=request.model,
                prompt=final_prompt,
                options=request.options or {},
            )
        except ProviderError as e:
            event_id = self._generate_event_id()
            log_api_event(
                route="/v1/chat",
                model=request.model,
                prompt=request.prompt,
                session_id=request.session_id,
                action=decision.action,
                allowed=True,
                risk_score=decision.risk_score,
                attack_type=decision.attack_type,
                provider_called=True,
                error="provider_error",
                logger=self.event_logger,
            )
            return ChatResponse(
                allowed=True,
                action=decision.action,
                risk_score=decision.risk_score,
                attack_type=decision.attack_type or "benign",
                response="",
                blocked_reason=None,
                event_id=event_id,
                error="provider_error",
                error_message=str(e),
            )

        og = OutputGuard()
        og_result = og.inspect(raw_output, protected_assets=self.registry.get_all())

        lv = LeakageVerifier()
        leak_result = lv.verify(raw_output, self.registry.get_all())

        safe_output = og_result.safe_output
        if leak_result.is_leak:
            safe_output = leak_result.redacted_output or safe_output

        event_id = self._generate_event_id()
        log_api_event(
            route="/v1/chat",
            model=request.model,
            prompt=request.prompt,
            session_id=request.session_id,
            action=decision.action,
            allowed=True,
            risk_score=decision.risk_score,
            attack_type=decision.attack_type,
            provider_called=True,
            leakage_detected=leak_result.is_leak or og_result.is_blocked,
            matched_assets=decision.matched_assets,
            logger=self.event_logger,
        )
        return ChatResponse(
            allowed=True,
            action=decision.action,
            risk_score=decision.risk_score,
            attack_type=decision.attack_type or "benign",
            response=safe_output,
            blocked_reason=None,
            event_id=event_id,
        )

    RESTRICTED_STREAM_PATTERNS = [
        "api_key", "sk-", "picoCTF{",
        "BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY",
        "BEGIN EC PRIVATE KEY", "BEGIN OPENSSH PRIVATE KEY",
    ]

    def chat_stream(self, request, provider):
        decision = self.analyze(
            prompt=request.prompt,
            session_id=request.session_id,
            role=request.role,
        )

        event_id = self._generate_event_id()

        if not decision.allowed or decision.action == "block":
            log_api_event(
                route="/v1/chat/stream",
                model=request.model,
                prompt=request.prompt,
                session_id=request.session_id,
                action="block",
                allowed=False,
                risk_score=decision.risk_score,
                attack_type=decision.attack_type,
                blocked_reason=decision.reason,
                provider_called=False,
                matched_assets=decision.matched_assets,
                logger=self.event_logger,
            )
            yield {
                "type": "blocked",
                "reason": decision.reason or "request blocked",
                "risk_score": decision.risk_score,
            }
            yield {"type": "done", "event_id": event_id}
            return

        yield {
            "type": "start",
            "event_id": event_id,
            "risk_score": decision.risk_score,
            "action": decision.action,
        }

        pbr = PromptBuildRequest(
            original_prompt=request.prompt,
            normalized_prompt=request.prompt,
            policy_action=decision.action.upper(),
            risk_score=decision.risk_score,
            attack_categories=[decision.attack_type] if decision.attack_type else [],
            protected_assets=decision.matched_assets,
        )
        builder = ProtectedPromptBuilder()
        built = builder.build(pbr)
        final_prompt = built.final_prompt

        monitor = StreamMonitor(restricted_patterns=self.RESTRICTED_STREAM_PATTERNS)
        accumulated = []

        try:
            for chunk in provider.stream_generate(
                model=request.model,
                prompt=final_prompt,
                options=request.options or {},
            ):
                result = monitor.inspect_chunk(chunk)
                if not result.allowed:
                    yield {
                        "type": "blocked",
                        "reason": result.reason or "restricted token detected",
                        "risk_score": result.risk_score,
                    }
                    yield {"type": "done", "event_id": event_id}
                    return

                accumulated.append(chunk)
                yield {"type": "token", "content": chunk}

        except ProviderError as e:
            log_api_event(
                route="/v1/chat/stream",
                model=request.model,
                prompt=request.prompt,
                session_id=request.session_id,
                action=decision.action,
                allowed=True,
                risk_score=decision.risk_score,
                attack_type=decision.attack_type,
                provider_called=True,
                leakage_detected=False,
                error="provider_error",
                logger=self.event_logger,
            )
            yield {
                "type": "error",
                "error": "provider_error",
                "message": str(e),
            }
            yield {"type": "done", "event_id": event_id}
            return

        full_output = "".join(accumulated)
        og = OutputGuard()
        og_result = og.inspect(full_output, protected_assets=self.registry.get_all())
        lv = LeakageVerifier()
        leak_result = lv.verify(full_output, self.registry.get_all())

        log_api_event(
            route="/v1/chat/stream",
            model=request.model,
            prompt=request.prompt,
            session_id=request.session_id,
            action=decision.action,
            allowed=True,
            risk_score=decision.risk_score,
            attack_type=decision.attack_type,
            provider_called=True,
            leakage_detected=leak_result.is_leak or og_result.is_blocked,
            matched_assets=decision.matched_assets,
            logger=self.event_logger,
        )

        if not og_result.is_blocked and not leak_result.is_leak:
            yield {"type": "done", "event_id": event_id}
        else:
            yield {
                "type": "blocked",
                "reason": "output guard or leakage detected after streaming",
                "risk_score": 90,
            }
            yield {"type": "done", "event_id": event_id}

    def analyze(
        self,
        prompt: str,
        session_id: str = "default",
        role: str = "user",
    ) -> GuardDecision:
        if not prompt or not prompt.strip():
            return GuardDecision(
                allowed=True,
                action="allow",
                risk_score=0,
                attack_type=None,
                reason=None,
            )

        ctx = PipelineContext(
            prompt=prompt,
            session_id=session_id,
            role=role,
        )

        norm = normalize_input(prompt)
        ctx.normalized_prompt = norm.normalized_text

        assets_res = self.registry.match(norm.normalized_text)
        matched = assets_res.get("matches", []) if assets_res.get("matched") else []

        ig = self.input_guard.check(norm.normalized_text)

        threats = self.classifier.classify_with_context(norm.normalized_text, [])
        cats = [t.get("category") for t in threats]

        simplified_type, simplified_score = self._apply_simplified_rules(norm.normalized_text)

        effective_attack_type = cats[0] if cats else simplified_type
        if simplified_type and simplified_type not in cats:
            cats.append(simplified_type)

        request_ctx = {
            "attack_category": effective_attack_type,
            "classifier_confidence": threats[0].get("confidence") if threats else (0.9 if simplified_type else 0.0),
            "matched_assets": matched,
            "triggered_rules": ig.get("matched_rules", []),
            "authorization_status": "unknown",
            "session_signals": [],
        }
        risk = self.risk_engine.score(request_ctx)

        effective_risk_score = max(risk.risk_score, simplified_score)

        policy_ctx = {
            "normalized_prompt": norm.normalized_text,
            "attack_category": effective_attack_type,
            "risk_score": effective_risk_score,
            "risk_level": risk.risk_level,
            "matched_assets": matched,
            "user_role": role,
            "is_authorized": False,
            "session_risk_score": 0,
            "input_guard_flags": ig.get("matched_rules", []),
            "classifier_confidence": request_ctx["classifier_confidence"],
        }
        decision = self.policy_engine.decide(policy_ctx)
        action = decision.action.value if hasattr(decision.action, "value") else str(decision.action)

        allowed = action.upper() in ("ALLOW", "WARN")
        attack_type = effective_attack_type
        reason = decision.reason if hasattr(decision, "reason") else None

        log_api_event(
            route="/v1/analyze",
            prompt=prompt,
            session_id=session_id,
            action=action.lower(),
            allowed=allowed,
            risk_score=effective_risk_score,
            attack_type=attack_type,
            blocked_reason=reason,
            provider_called=False,
            matched_assets=matched,
            logger=self.event_logger,
        )

        return GuardDecision(
            allowed=allowed,
            action=action.lower(),
            risk_score=effective_risk_score,
            attack_type=attack_type,
            reason=reason,
            matched_assets=matched,
        )
