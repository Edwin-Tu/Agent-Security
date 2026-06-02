# task03.md — 建立 LLM Provider 介面與 OllamaProvider

> 專案：SecretGuard / Agent-Security  
> 開發原則：TDD first。先寫測試，確認失敗，再實作功能，最後重構。  
> 重要限制：每個 task 只處理本任務範圍，不要順手改其他模組，降低小模型負擔。  
> 架構原則：`main.py` 不廢棄，改為啟動器與 CLI client；核心防護流程集中在 `SecretGuardPipeline`；HTTP API 為正式整合入口。

## 1. 任務目標

建立模型供應層 Provider，使 SecretGuard 不直接綁死 Ollama，未來可以替換 LM Studio、llama.cpp server 或 OpenAI-compatible local server。

本任務只負責 Provider，不做 API chat，不做完整防護流程。

## 2. 架構定位

```text
SecretGuardPipeline
        ↓
BaseLLMProvider
        ↓
OllamaProvider
        ↓
Ollama HTTP API
```

## 3. 預期新增 / 修改檔案

```text
providers/
├── __init__.py
├── base_provider.py
├── ollama_provider.py
└── tests/
    ├── __init__.py
    └── test_ollama_provider.py

api/
├── routes_models.py
└── tests/
    └── test_models_api.py
```

## 4. Provider 介面需求

建立：

```python
class BaseLLMProvider:
    def list_models(self) -> list[dict]:
        raise NotImplementedError

    def generate(self, model: str, prompt: str, options: dict | None = None) -> str:
        raise NotImplementedError

    def stream_generate(self, model: str, prompt: str, options: dict | None = None):
        raise NotImplementedError
```

建立：

```python
class ProviderError(Exception):
    pass
```

## 5. OllamaProvider 需求

支援：

1. `list_models()` → 呼叫 Ollama `GET /api/tags`。
2. `generate()` → 呼叫 Ollama `POST /api/generate` 或 `/api/chat`。
3. `stream_generate()` → 支援逐 chunk yield。
4. Ollama 連線失敗時丟出 `ProviderError`，不要讓 server crash。
5. base_url 預設為 `http://127.0.0.1:11434`。

## 6. API 需求

新增：

```http
GET /v1/models
```

Response:

```json
{
  "provider": "ollama",
  "models": [
    {"name": "qwen2.5-coder:7b"}
  ]
}
```

Provider error 時：

```json
{
  "provider": "ollama",
  "models": [],
  "error": "provider_error",
  "message": "Ollama is not available"
}
```

## 7. TDD 測試要求

先建立：

```text
providers/tests/test_ollama_provider.py
api/tests/test_models_api.py
```

至少測試：

1. `list_models()` 可以正確解析 `/api/tags` response。
2. `generate()` 可以正確解析 Ollama response。
3. `stream_generate()` 可以逐 chunk yield。
4. 連線失敗時轉為 `ProviderError`。
5. `/v1/models` 正常時回傳模型清單。
6. `/v1/models` 在 Ollama 掛掉時仍回傳可讀錯誤，不讓 API crash。

測試需 mock HTTP，不可依賴真實 Ollama。

## 8. 實作建議

可使用：

```text
httpx
```

或使用標準庫，但建議 httpx 較適合測試與 timeout 控制。

預設 timeout 建議：

```text
connect timeout: 5s
generate timeout: 120s
```

## 9. 驗收標準

執行：

```bash
pytest providers/tests api/tests -v
```

啟動 server 後：

```bash
curl http://127.0.0.1:8765/v1/models
```

若 Ollama 正常，回傳模型清單。
若 Ollama 未啟動，回傳 provider_error，但 SecretGuard API 不崩潰。

## 10. 不在本任務範圍

- 不做 `/v1/chat`。
- 不做 Runtime Stream Monitor。
- 不做 OpenAI-compatible API。
