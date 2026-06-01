import json
import time
from typing import Callable, Generator
import requests

from .errors import (
    LLMGatewayError,
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaTimeoutError,
    OllamaGenerationError,
    OllamaStreamError,
)
from .model_config import ModelOptions
from .model_response import LLMResponse, LLMChunk, OllamaModelInfo


class OllamaClient:
    def __init__(self, ollama_url: str = "http://localhost:11434", timeout: int = 60):
        self.ollama_url = ollama_url.rstrip("/")
        self.default_timeout = timeout

    def _build_payload(self, prompt: str, model: str, options: ModelOptions | None) -> dict:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        if options:
            payload["stream"] = options.stream
            opts = {}
            if options.temperature != 0.2:
                opts["temperature"] = options.temperature
            if options.top_p != 0.9:
                opts["top_p"] = options.top_p
            if options.num_ctx != 4096:
                opts["num_ctx"] = options.num_ctx
            if options.num_predict != 512:
                opts["num_predict"] = options.num_predict
            if options.seed is not None:
                opts["seed"] = options.seed
            if opts:
                payload["options"] = opts
        return payload

    def _get_timeout(self, options: ModelOptions | None) -> int:
        if options is not None:
            return options.timeout_seconds
        return self.default_timeout

    def check_connection(self) -> LLMResponse:
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                return LLMResponse(
                    success=True,
                    text="",
                    model="",
                    done=True,
                )
            return LLMResponse(
                success=False,
                text="",
                model="",
                done=True,
                error_type="connection_error",
                error_message=f"Ollama returned status {resp.status_code}",
            )
        except requests.ConnectionError:
            return LLMResponse(
                success=False,
                text="",
                model="",
                done=True,
                error_type="connection_error",
                error_message="Cannot connect to Ollama. Please ensure it is running.",
            )
        except Exception:
            return LLMResponse(
                success=False,
                text="",
                model="",
                done=True,
                error_type="connection_error",
                error_message="Failed to connect to Ollama.",
            )

    def list_models(self) -> list[OllamaModelInfo]:
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                models = data.get("models", [])
                return [
                    OllamaModelInfo(
                        name=m.get("name", ""),
                        modified_at=m.get("modified_at", ""),
                        size=m.get("size", 0),
                    )
                    for m in models
                ]
            return []
        except Exception:
            return []

    def generate(
        self,
        prompt: str,
        model: str,
        options: ModelOptions | None = None,
    ) -> LLMResponse:
        timeout = self._get_timeout(options)
        payload = self._build_payload(prompt, model, options)
        payload["stream"] = False
        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=timeout,
            )
            if resp.status_code == 404:
                return LLMResponse(
                    success=False,
                    text="",
                    model=model,
                    done=True,
                    error_type="model_not_found",
                    error_message=f"Model '{model}' not found on Ollama.",
                )
            resp.raise_for_status()
            data = resp.json()
            return LLMResponse(
                success=True,
                text=data.get("response", ""),
                model=data.get("model", model),
                done=data.get("done", True),
                prompt_tokens=data.get("prompt_eval_count"),
                completion_tokens=data.get("eval_count"),
                total_duration_ms=(
                    data.get("total_duration", 0) // 1_000_000
                    if data.get("total_duration")
                    else None
                ),
                raw=data,
            )
        except requests.ConnectionError:
            return LLMResponse(
                success=False,
                text="",
                model=model,
                done=True,
                error_type="connection_error",
                error_message="Cannot connect to Ollama.",
            )
        except (requests.Timeout, TimeoutError):
            return LLMResponse(
                success=False,
                text="",
                model=model,
                done=True,
                error_type="timeout",
                error_message="Request timed out.",
            )
        except requests.HTTPError as e:
            error_type = "model_not_found" if resp.status_code == 404 else "generation_error"
            return LLMResponse(
                success=False,
                text="",
                model=model,
                done=True,
                error_type=error_type,
                error_message="Model generation failed.",
            )
        except Exception:
            return LLMResponse(
                success=False,
                text="",
                model=model,
                done=True,
                error_type="generation_error",
                error_message="An unexpected error occurred during generation.",
            )

    def stream_generate(
        self,
        prompt: str,
        model: str,
        options: ModelOptions | None = None,
        should_stop: Callable[[LLMChunk], bool] | None = None,
    ) -> Generator[LLMChunk, None, None]:
        timeout = self._get_timeout(options)
        payload = self._build_payload(prompt, model, options)
        payload["stream"] = True
        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                stream=True,
                timeout=timeout,
            )
            resp.raise_for_status()
            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    chunk = LLMChunk(
                        text=data.get("response", ""),
                        model=data.get("model", model),
                        done=data.get("done", False),
                        raw=data,
                    )
                    if should_stop and should_stop(chunk):
                        chunk.stopped_by_guard = True
                        yield chunk
                        return
                    yield chunk
                    if chunk.done:
                        return
                except json.JSONDecodeError:
                    continue
        except requests.ConnectionError:
            yield LLMChunk(
                text="",
                model=model,
                done=True,
                raw=None,
            )
        except (requests.Timeout, TimeoutError):
            yield LLMChunk(
                text="",
                model=model,
                done=True,
                raw=None,
            )
        except Exception:
            yield LLMChunk(
                text="",
                model=model,
                done=True,
                raw=None,
            )
