from __future__ import annotations

from typing import Optional, Iterable

from config import Config
from input_normalization.input_normalizer import normalize_input
from asset_registry.protected_asset_registry import ProtectedAssetRegistry
from input_guard.input_guard import InputGuard
from attack_classifier.attack_classifier import AttackClassifier
from risk_scoring.risk_scoring_engine import RiskScoringEngine
from policy_engine.defense_policy_engine import DefensePolicyEngine
from skill_router.routing_context import RoutingContext
from skill_router.skill_router import SkillRouter
from prompt_builder.protected_prompt_builder import ProtectedPromptBuilder
from prompt_builder.restricted_token_guard import RestrictedTokenGuard
from llm_gateway.ollama_client import OllamaClient, LLMChunk, LLMResponse
from runtime_monitor.stream_monitor import RuntimeStreamMonitor
from runtime_monitor.interruption_handler import InterruptionHandler
from runtime_monitor.runtime_guard import RuntimeGuard
from output_guard.output_guard import OutputGuard
from leakage_verifier.leakage_verifier import LeakageVerifier
from event_logger.event_logger import EventLogger
from risk_scoring.session_memory import SessionMemory


class SecretGuardPipeline:
    def __init__(self, config: Config | None = None, llm_client: Optional[object] = None):
        self.cfg = config or Config()
        self.registry = ProtectedAssetRegistry()
        self.input_guard = InputGuard()
        self.classifier = AttackClassifier()
        self.risk_engine = RiskScoringEngine()
        self.policy_engine = DefensePolicyEngine(threshold=self.cfg.threshold)
        self.skill_router = SkillRouter()
        self.prompt_builder = ProtectedPromptBuilder()
        self.token_guard = RestrictedTokenGuard()
        self.output_guard = OutputGuard()
        self.leakage_verifier = LeakageVerifier()
        self.event_logger = EventLogger()
        self.session = SessionMemory()
        self.llm_client = llm_client or OllamaClient(ollama_url=self.cfg.ollama_url)

    def handle(self, prompt: str, model: Optional[str] = None, dry_run: bool = False) -> dict:
        result: dict = {
            "success": True,
            "safe_output": "",
            "original_prompt": prompt,
            "normalized_prompt": "",
            "protected_prompt": "",
            "blocked": False,
            "block_reason": None,
            "policy_action": "ALLOW",
            "risk_score": 0,
            "risk_level": "low",
            "attack_categories": [],
            "matched_assets": [],
            "enabled_skills": [],
            "llm_called": False,
            "runtime_interrupted": False,
            "runtime_interrupt_reason": None,
            "output_guard_blocked": False,
            "leakage_detected": False,
            "leakage_type": None,
            "event_logged": False,
            "errors": [],
        }

        try:
            # 1. Normalization
            norm = normalize_input(prompt)
            result["normalized_prompt"] = norm.normalized_text

            # 2. Protected asset match
            assets_res = self.registry.match(norm.normalized_text)
            matched = assets_res.get("matches", []) if assets_res.get("matched") else []
            result["matched_assets"] = matched

            # 3. Input guard
            ig = self.input_guard.check(norm.normalized_text)
            result["input_guard"] = ig

            # 4. Attack classification
            threats = self.classifier.classify_with_context(norm.normalized_text, self.session.get_history_texts())
            cats = [t.get("category") for t in threats]
            result["attack_categories"] = cats

            # 5. Risk scoring
            request_ctx = {
                "attack_category": cats[0] if cats else None,
                "classifier_confidence": threats[0].get("confidence") if threats else 0.0,
                "matched_assets": matched,
                "triggered_rules": ig.get("matched_rules", []),
                "authorization_status": "unknown",
                "session_signals": [],
            }
            risk = self.risk_engine.score(request_ctx)
            result["risk_score"] = risk.risk_score
            result["risk_level"] = risk.risk_level

            # 6. Policy decision
            policy_ctx = {
                "normalized_prompt": norm.normalized_text,
                "attack_category": request_ctx["attack_category"],
                "risk_score": risk.risk_score,
                "risk_level": risk.risk_level,
                "matched_assets": matched,
                "user_role": "guest",
                "is_authorized": False,
                "session_risk_score": self.session.accumulated_risk,
                "input_guard_flags": ig.get("matched_rules", []),
                "classifier_confidence": request_ctx["classifier_confidence"],
            }
            decision = self.policy_engine.decide(policy_ctx)
            action = decision.action.value if hasattr(decision.action, "value") else str(decision.action)
            result["policy_action"] = action

            # Early block by policy or input guard
            if decision.should_block or ig.get("recommended_action") == "block_candidate":
                result["blocked"] = True
                result["block_reason"] = decision.reason
                result["llm_called"] = False
                # log event
                event = {
                    "original_prompt": prompt,
                    "normalized_prompt": norm.normalized_text,
                    "attack_categories": cats,
                    "matched_assets": [a.get("asset_id") for a in matched],
                    "risk_score": risk.risk_score,
                    "risk_level": risk.risk_level,
                    "policy_action": action,
                    "enabled_skills": [],
                    "llm_called": False,
                    "runtime_interrupted": False,
                }
                self.event_logger.log_event(event)
                result["event_logged"] = True
                # return safe response from policy
                result["safe_output"] = decision.reason or self.cfg.rejection_message
                return result

            # 7. Skill routing
            routing_ctx = RoutingContext(
                prompt=norm.normalized_text,
                attack_categories=cats,
                policy_action=action,
                risk_score=risk.risk_score,
                protected_assets=matched,
                matched_rules=ig.get("matched_rules", []),
                session_context={"history": self.session.get_history_texts()},
                user_role="guest",
            )
            route_res = self.skill_router.route(routing_ctx)
            result["enabled_skills"] = route_res.executed_skills
            if route_res.blocked:
                result["blocked"] = True
                result["block_reason"] = "; ".join(route_res.reasons or [])
                self.event_logger.log_event({
                    "original_prompt": prompt,
                    "normalized_prompt": norm.normalized_text,
                    "attack_categories": cats,
                    "matched_assets": [a.get("asset_id") for a in matched],
                    "risk_score": risk.risk_score,
                    "risk_level": risk.risk_level,
                    "policy_action": action,
                    "enabled_skills": route_res.executed_skills,
                    "llm_called": False,
                    "runtime_interrupted": False,
                })
                result["event_logged"] = True
                result["safe_output"] = self.cfg.rejection_message
                return result

            # 8. Build protected prompt
            from prompt_builder.prompt_build_request import PromptBuildRequest

            pbr = PromptBuildRequest(
                original_prompt=prompt,
                normalized_prompt=norm.normalized_text,
                policy_action=action,
                risk_score=risk.risk_score,
                attack_categories=cats,
                protected_assets=matched,
                enabled_skills=route_res.executed_skills,
            )
            built = self.prompt_builder.build(pbr)
            result["protected_prompt"] = built.final_prompt

            # 9. Restricted token guard
            token_res = self.token_guard.detect(built.final_prompt)
            if token_res.get("blocked"):
                result["blocked"] = True
                result["block_reason"] = token_res.get("reason")
                result["llm_called"] = False
                self.event_logger.log_event({
                    "original_prompt": prompt,
                    "normalized_prompt": norm.normalized_text,
                    "attack_categories": cats,
                    "matched_assets": [a.get("asset_id") for a in matched],
                    "risk_score": risk.risk_score,
                    "risk_level": risk.risk_level,
                    "policy_action": action,
                    "enabled_skills": route_res.executed_skills,
                    "llm_called": False,
                    "runtime_interrupted": False,
                })
                result["event_logged"] = True
                result["safe_output"] = self.cfg.rejection_message
                return result

            # 10. Call LLM (unless dry_run)
            final_output = ""
            runtime_interrupted = False
            runtime_reason = None
            if not dry_run:
                # decide streaming vs sync
                if hasattr(self.llm_client, "stream_generate"):
                    monitor = RuntimeStreamMonitor(protected_assets=self.registry.get_all())
                    handler = InterruptionHandler()
                    guard = RuntimeGuard(monitor=monitor, handler=handler)

                    chunks: list[str] = []
                    for chunk in self.llm_client.stream_generate(
                        prompt=built.final_prompt, model=model or self.cfg.model, options=None, should_stop=None
                    ):
                        text = chunk.text if isinstance(chunk, LLMChunk) else str(chunk)
                        chunks.append(text)
                        inspect = monitor.inspect_chunk(text)
                        if monitor.should_interrupt(inspect):
                            runtime_interrupted = True
                            runtime_reason = inspect.reason
                            final_output = handler.build_safe_response(inspect) or self.cfg.rejection_message
                            break
                    if not runtime_interrupted:
                        final_output = "".join(chunks)
                    # additional safety: direct substring check against registry
                    if not runtime_interrupted:
                        for a in self.registry.get_all():
                            val = (a.get("value") or "").strip()
                            if val and val.lower() in final_output.lower():
                                runtime_interrupted = True
                                runtime_reason = "Detected protected secret in streaming output."
                                final_output = InterruptionHandler().build_safe_response(monitor.inspect_buffer()) or self.cfg.rejection_message
                                break
                else:
                    resp: LLMResponse = self.llm_client.generate(prompt=built.final_prompt, model=model or self.cfg.model, options=None)
                    final_output = resp.text if getattr(resp, "text", None) else ""
                result["llm_called"] = True
            else:
                # dry run: don't call LLM but use safe_response from builder
                final_output = built.safe_response or ""
                result["llm_called"] = False

            # 11. Runtime guard post-check (non-stream)
            if not runtime_interrupted:
                # final output check via runtime guard
                monitor2 = RuntimeStreamMonitor(protected_assets=self.registry.get_all())
                handler2 = InterruptionHandler()
                guard2 = RuntimeGuard(monitor=monitor2, handler=handler2)
                check = guard2.check_output(final_output)
                if check.get("blocked"):
                    result["runtime_interrupted"] = True
                    result["runtime_interrupt_reason"] = check.get("reason")
                    final_output = handler2.build_safe_response(monitor2.inspect_buffer()) or self.cfg.rejection_message

            result["runtime_interrupted"] = runtime_interrupted or result.get("runtime_interrupted", False)
            if runtime_interrupted:
                result["runtime_interrupt_reason"] = runtime_reason

            # 12. Output guard
            out = self.output_guard.inspect(final_output, protected_assets=self.registry.get_all())
            result["output_guard_blocked"] = out.is_blocked
            result["safe_output"] = out.safe_output

            # 13. Leakage verifier
            leak = self.leakage_verifier.verify(out.safe_output, self.registry.get_all())
            result["leakage_detected"] = leak.is_leak
            result["leakage_type"] = leak.leak_types[0] if leak.leak_types else None

            # 14. Event logging
            event = {
                "original_prompt": prompt,
                "normalized_prompt": norm.normalized_text,
                "attack_categories": cats,
                "matched_assets": [a.get("asset_id") for a in matched],
                "risk_score": risk.risk_score,
                "risk_level": risk.risk_level,
                "policy_action": action,
                "enabled_skills": route_res.executed_skills,
                "llm_called": result["llm_called"],
                "runtime_interrupted": result["runtime_interrupted"],
                "output_guard_blocked": result["output_guard_blocked"],
                "leakage_detected": result["leakage_detected"],
            }
            self.event_logger.log_event(event)
            result["event_logged"] = True

            return result

        except Exception as e:
            result["success"] = False
            result["errors"].append(str(e))
            return result
