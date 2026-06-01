# LLM Gateway

> SecretGuard Local LLM / Ollama Gateway module  
> SecretGuard 第 `[11] Local LLM / Ollama` 流程模組

---

## 1. 模組定位

`llm_gateway` 是 SecretGuard 中負責與本地大型語言模型溝通的模組，主要任務是將前面流程產生的 `safe_prompt` 傳送給 Ollama，並把模型回應統一整理成 SecretGuard 可處理的標準格式。

在完整 SecretGuard 防禦流程中，本模組位於：

```text
[9] Protected Prompt Builder
        ↓
[10] Restricted Token Guard
        ↓
[11] Local LLM / Ollama / LLM Gateway
        ↓
[12] Runtime Stream Monitor
        ↓
[13] Output Guard
        ↓
[14] Leakage Verifier
        ↓
[15] Event Logger
```

也就是說，`llm_gateway` 不直接負責判斷攻擊，也不直接負責洩漏驗證；它的職責是提供一個穩定、可測試、可替換的模型呼叫層，讓 SecretGuard 可以安全地與 Ollama 串接。

---

## 2. 核心功能

目前 `llm_gateway` 提供以下功能：

```text
1. Ollama 連線檢查
2. Ollama 模型清單讀取
3. 非串流文字生成
4. 串流文字生成
5. 串流過程中支援 guard callback 中斷
6. 統一模型回應格式
7. 統一 chunk 回傳格式
8. 模型參數驗證
9. 安全錯誤處理
10. 避免錯誤訊息洩漏原始敏感 prompt
```

---

## 3. 目錄結構

```text
llm_gateway/
├── __init__.py
├── base_llm.py
├── errors.py
├── gateway.py
├── model_config.py
├── model_response.py
├── ollama_client.py
└── tests/
    ├── __init__.py
    ├── test_gateway_errors.py
    ├── test_llm_gateway.py
    ├── test_ollama_client_connection.py
    ├── test_ollama_client_generate.py
    ├── test_ollama_client_models.py
    └── test_ollama_client_stream.py
```

---

## 4. 檔案說明

### 4.1 `gateway.py`

`LLMGateway` 是對外主要入口。

它負責接收 SecretGuard 前面流程產生的 `safe_prompt`，再委派給底層 `OllamaClient` 執行生成。

主要方法：

```python
LLMGateway.generate(...)
LLMGateway.stream_generate(...)
```

功能重點：

```text
- 要求 safe_prompt 不可為空
- 統一呼叫 OllamaClient
- 保留模型回應 metadata
- 支援串流生成
- 支援 Runtime Guard 中斷 callback
```

---

### 4.2 `ollama_client.py`

`OllamaClient` 是實際與 Ollama API 溝通的類別。

預設連線位置：

```text
http://localhost:11434
```

使用的 Ollama API：

```text
GET  /api/tags
POST /api/generate
```

主要方法：

```python
check_connection()
list_models()
generate(prompt, model, options=None)
stream_generate(prompt, model, options=None, should_stop=None)
```

功能重點：

```text
- 檢查 Ollama 是否啟動
- 讀取本地已安裝模型
- 發送非串流生成請求
- 發送串流生成請求
- 將 Ollama 原始 response 轉成 LLMResponse
- 將 Ollama 串流 line 轉成 LLMChunk
- 處理 connection / timeout / model not found / generation error
```

---

### 4.3 `model_config.py`

`ModelOptions` 定義模型生成參數。

```python
@dataclass
class ModelOptions:
    temperature: float = 0.2
    top_p: float = 0.9
    num_ctx: int = 4096
    num_predict: int = 512
    seed: int | None = None
    stream: bool = True
    timeout_seconds: int = 60
```

參數驗證規則：

```text
temperature      必須 >= 0
top_p            必須介於 0 到 1
num_ctx          必須 > 0
num_predict      必須 > 0
timeout_seconds  必須 > 0
```

如果參數不合法，會拋出：

```python
InvalidModelOptionsError
```

---

### 4.4 `model_response.py`

定義 LLM Gateway 的標準資料格式。

#### `LLMResponse`

用於非串流生成結果。

```python
@dataclass
class LLMResponse:
    success: bool
    text: str
    model: str
    done: bool
    error_type: str | None = None
    error_message: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_duration_ms: int | None = None
    stopped_by_guard: bool = False
    raw: dict | None = None
```

欄位說明：

| 欄位 | 說明 |
|---|---|
| `success` | 是否成功生成 |
| `text` | 模型輸出文字 |
| `model` | 使用的模型名稱 |
| `done` | Ollama 是否完成生成 |
| `error_type` | 錯誤類型 |
| `error_message` | 安全化後的錯誤訊息 |
| `prompt_tokens` | prompt token 數 |
| `completion_tokens` | completion token 數 |
| `total_duration_ms` | 生成耗時，單位毫秒 |
| `stopped_by_guard` | 是否被 guard 中斷 |
| `raw` | Ollama 原始回應 |

#### `LLMChunk`

用於串流生成結果。

```python
@dataclass
class LLMChunk:
    text: str
    model: str
    done: bool = False
    raw: dict | None = None
    stopped_by_guard: bool = False
```

欄位說明：

| 欄位 | 說明 |
|---|---|
| `text` | 當前 chunk 文字 |
| `model` | 模型名稱 |
| `done` | 是否為最後一個 chunk |
| `raw` | Ollama 原始 chunk |
| `stopped_by_guard` | 是否因 guard callback 命中而停止 |

#### `OllamaModelInfo`

用於模型清單結果。

```python
@dataclass
class OllamaModelInfo:
    name: str
    modified_at: str = ""
    size: int = 0
```

---

### 4.5 `errors.py`

定義 LLM Gateway 相關錯誤類型。

```python
LLMGatewayError
├── OllamaConnectionError
├── OllamaModelNotFoundError
├── OllamaTimeoutError
├── OllamaGenerationError
├── OllamaStreamError
└── InvalidModelOptionsError
```

目前多數 Ollama 呼叫錯誤會被轉換為 `LLMResponse` 或安全 chunk，而不是直接把底層 exception 暴露給上層。

---

### 4.6 `base_llm.py`

`BaseLLM` 是抽象介面，預留未來支援其他模型 Provider。

```python
class BaseLLM(ABC):
    def is_available(self) -> bool: ...
    def generate(self, prompt: str, **kwargs) -> dict: ...
    def generate_text(self, prompt: str, system_prompt: str = "") -> str: ...
    def list_models(self) -> list[str]: ...
```

未來若要支援 OpenAI-compatible API、vLLM、LM Studio 或其他本地模型服務，可以依此介面擴充。

---

## 5. 安裝與前置需求

### 5.1 Python 套件

本模組使用：

```text
Python 3.10+
requests
pytest
```

安裝依賴：

```bash
pip install requests pytest
```

### 5.2 Ollama

請先安裝並啟動 Ollama。

```bash
ollama serve
```

確認 Ollama API 可用：

```bash
curl http://localhost:11434/api/tags
```

下載模型範例：

```bash
ollama pull qwen2.5-coder:7b
```

---

## 6. 使用方式

### 6.1 檢查 Ollama 連線

```python
from llm_gateway import OllamaClient

client = OllamaClient()
result = client.check_connection()

if result.success:
    print("Ollama is available")
else:
    print(result.error_type, result.error_message)
```

---

### 6.2 列出本地模型

```python
from llm_gateway import OllamaClient

client = OllamaClient()
models = client.list_models()

for model in models:
    print(model.name, model.size)
```

---

### 6.3 使用 `LLMGateway` 產生回應

```python
from llm_gateway import LLMGateway, ModelOptions

gateway = LLMGateway()

options = ModelOptions(
    temperature=0.2,
    top_p=0.9,
    num_ctx=4096,
    num_predict=512,
    timeout_seconds=60,
)

response = gateway.generate(
    safe_prompt="Explain what a Python list is in two sentences.",
    model="qwen2.5-coder:7b",
    options=options,
)

if response.success:
    print(response.text)
else:
    print(response.error_type, response.error_message)
```

---

### 6.4 串流生成

```python
from llm_gateway import LLMGateway

gateway = LLMGateway()

for chunk in gateway.stream_generate(
    safe_prompt="Explain what a Python list is.",
    model="qwen2.5-coder:7b",
):
    print(chunk.text, end="")

    if chunk.done:
        break
```

---

### 6.5 串流生成搭配 Guard 中斷

`stream_generate()` 支援 `should_stop` callback，可讓 Runtime Stream Monitor 在生成過程中即時阻擋敏感輸出。

```python
from llm_gateway import LLMGateway, LLMChunk

gateway = LLMGateway()

restricted_terms = ["api_key", "secret", "private_key"]

def should_stop(chunk: LLMChunk) -> bool:
    text = chunk.text.lower()
    return any(term in text for term in restricted_terms)

for chunk in gateway.stream_generate(
    safe_prompt="Safe prompt from Protected Prompt Builder",
    model="qwen2.5-coder:7b",
    should_stop=should_stop,
):
    print(chunk.text, end="")

    if chunk.stopped_by_guard:
        print("\n[Generation stopped by guard]")
        break
```

---

## 7. 與 SecretGuard 流程串接

### 7.1 建議串接流程

```python
from llm_gateway import LLMGateway, ModelOptions

# 前面流程已完成：
# 1. input normalization
# 2. input guard
# 3. attack classifier
# 4. risk scoring
# 5. defense policy
# 6. protected prompt builder
# 7. restricted token guard

safe_prompt = "..."  # Protected Prompt Builder 產生的安全 prompt
model = "qwen2.5-coder:7b"

options = ModelOptions(
    temperature=0.2,
    num_predict=512,
    timeout_seconds=90,
)

gateway = LLMGateway()
response = gateway.generate(safe_prompt, model, options)

# 後續交給 Output Guard / Leakage Verifier / Event Logger
if response.success:
    model_output = response.text
else:
    model_output = ""
```

---

### 7.2 Runtime Stream Monitor 串接方式

```text
LLMGateway.stream_generate()
        ↓
yield LLMChunk
        ↓
Runtime Stream Monitor 檢查 chunk
        ↓
命中敏感內容時 should_stop 回傳 True
        ↓
chunk.stopped_by_guard = True
        ↓
停止生成
        ↓
交給 Event Logger 記錄
```

---

## 8. 錯誤處理設計

### 8.1 非串流生成錯誤

`generate()` 不會直接把大多數底層錯誤拋出，而是回傳標準化 `LLMResponse`。

常見錯誤類型：

| `error_type` | 說明 |
|---|---|
| `connection_error` | 無法連線到 Ollama |
| `timeout` | 請求逾時 |
| `model_not_found` | 指定模型不存在 |
| `generation_error` | 生成過程發生錯誤 |

範例：

```python
response = gateway.generate("safe prompt", "missing-model")

if not response.success:
    print(response.error_type)
    print(response.error_message)
```

---

### 8.2 串流生成錯誤

`stream_generate()` 發生錯誤時，會 yield 一個安全的結束 chunk：

```python
LLMChunk(
    text="",
    model=model,
    done=True,
    raw=None,
)
```

這樣上層 Runtime Monitor 不需要額外處理大量 exception 分支。

---

### 8.3 敏感 Prompt 不外洩

測試已涵蓋錯誤訊息不應包含原始 secret prompt。

例如，當傳入 prompt 為：

```text
my-secret-token-abc123
```

即使底層生成失敗，`error_message` 也不應回傳該 secret。

---

## 9. 測試

### 9.1 執行測試

在專案根目錄執行：

```bash
pytest llm_gateway/tests -v
```

或在本模組目錄外層執行：

```bash
pytest llm_gateway/tests -q
```

---

### 9.2 目前測試結果

目前測試結果：

```text
27 passed
```

---

### 9.3 測試覆蓋範圍

目前測試包含：

```text
1. LLMGateway 是否正確委派給 OllamaClient
2. safe_prompt 不可為空
3. LLMResponse 標準格式
4. token / duration metadata 保留
5. Ollama 連線成功與失敗處理
6. 模型清單讀取
7. 非串流生成成功
8. 模型不存在處理
9. timeout 處理
10. 錯誤訊息不得洩漏敏感 prompt
11. 串流 chunk 標準化
12. done chunk 處理
13. should_stop callback 中斷生成
14. ModelOptions 參數驗證
```

---

## 10. 開發注意事項

### 10.1 `safe_prompt` 是必要輸入

`LLMGateway` 接收的是已經經過前面防護流程處理過的 `safe_prompt`，不建議直接把使用者原始 prompt 傳入本模組。

正確流程：

```text
raw user prompt
    ↓
Input Normalization
    ↓
Input Guard
    ↓
Attack Classifier
    ↓
Risk Scoring
    ↓
Defense Policy
    ↓
Protected Prompt Builder
    ↓
safe_prompt
    ↓
LLM Gateway
```

---

### 10.2 不要在錯誤訊息中輸出原始 Prompt

因為 prompt 可能包含：

```text
API Key
Token
Password
Private Key
Flag
System Prompt
內部文件內容
```

所以錯誤訊息應保持泛化，例如：

```text
An unexpected error occurred during generation.
```

而不是：

```text
Failed to generate for prompt: sk-xxxx...
```

---

### 10.3 串流模式應優先支援 Runtime Guard

SecretGuard 的研究重點之一是生成期間即時防護，因此 `stream_generate()` 的 `should_stop` callback 是後續 Runtime Stream Monitor 的重要掛接點。

---

## 11. 後續優化方向

建議後續可加入：

```text
1. 實作 BaseLLM 與 OllamaClient 的正式繼承關係
2. 增加 OpenAI-compatible API provider
3. 增加 LM Studio / vLLM provider
4. 增加 retry 機制
5. 增加 request id / trace id
6. 增加 structured logging
7. 增加模型不存在時的建議 pull 指令
8. 增加 health check CLI
9. 增加 token usage 統計整合到 Event Logger
10. 將 stream error chunk 加上 error_type / error_message
11. 將 should_stop callback 擴充為 RuntimeGuard 介面
12. 支援 system prompt / context messages 結構化輸入
13. 支援 chat API `/api/chat`
14. 支援 benchmark metadata 回傳
```

---

## 12. 模組摘要

`llm_gateway` 是 SecretGuard 與本地 LLM/Ollama 之間的標準化橋接層。

它的核心價值是：

```text
讓 SecretGuard 不直接依賴 Ollama 原始 API，
而是透過 LLMGateway 取得穩定、可測試、可中斷、可擴充的模型呼叫介面。
```

目前模組已支援：

```text
- Ollama 連線檢查
- 模型清單讀取
- 非串流生成
- 串流生成
- Guard callback 中斷
- 標準 LLMResponse
- 標準 LLMChunk
- 安全錯誤處理
- ModelOptions 驗證
```

因此它可以作為後續 Runtime Stream Monitor、Output Guard、Leakage Verifier 與 Event Logger 的穩定模型輸出來源。
