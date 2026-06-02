# [11] Local LLM / Ollama — llm_gateway 開發任務

## 1. 任務目標

本任務目標是完成 SecretGuard 系統流程中的 **[11] Local LLM / Ollama** 模組，建立一個可被上游防護模組安全呼叫、可被下游 Runtime Monitor 監控的本地 LLM Gateway。

此模組資料夾命名為：

```text
llm_gateway/
```

測試檔案必須放置於：

```text
llm_gateway/tests/
```

本階段開發必須採用 **TDD（Test-Driven Development）測試驅動開發策略**：

1. 先撰寫測試
2. 確認測試失敗
3. 再實作功能
4. 讓測試通過
5. 最後重構與補強錯誤處理

驗收必須同時包含：

```text
1. llm_gateway/tests 測試完成
2. llm_gateway 功能開發完成
3. pytest llm_gateway/tests -v 可通過
```

---

## 2. 系統定位

`llm_gateway` 對應 SecretGuard 系統流程中的：

```text
[11] Local LLM / Ollama
```

它位於：

```text
[10] Restricted Token Guard
        ↓
[11] Local LLM / Ollama
        ↓
[12] Runtime Stream Monitor
```

因此本模組不是主要防禦判斷層，而是 **模型呼叫與生成串流管理層**。

它的核心責任是：

```text
接收安全化後的 Prompt
呼叫本地 Ollama 模型
支援一般生成與串流生成
將生成結果以標準格式回傳
允許 Runtime Monitor 在生成期間中斷輸出
提供模型執行 metadata 給 Event Logger / Report Generator
```

---

## 3. 不在本模組處理的範圍

`llm_gateway` 不應負責以下工作：

```text
攻擊分類
風險分數計算
防禦政策決策
Defensive Skill 掛載
Protected Prompt 產生
Restricted Token 檢查
Output Guard 檢查
Leakage Verifier 驗證
Event Logger 寫入
```

這些分別由其他模組負責。

`llm_gateway` 只需要保證：

```text
安全地呼叫模型
穩定地取得輸出
可串流
可中斷
可回傳標準資料格式
可處理錯誤
```

---

## 4. 建議資料夾結構

請建立或調整為以下結構：

```text
llm_gateway/
├── __init__.py
├── ollama_client.py
├── gateway.py
├── model_config.py
├── model_response.py
├── errors.py
└── tests/
    ├── __init__.py
    ├── test_ollama_client_connection.py
    ├── test_ollama_client_models.py
    ├── test_ollama_client_generate.py
    ├── test_ollama_client_stream.py
    ├── test_llm_gateway.py
    └── test_gateway_errors.py
```

---

## 5. 核心功能需求

### 5.1 Ollama Client

建立 `ollama_client.py`，封裝 Ollama API 呼叫。

應提供：

```python
class OllamaClient:
    def check_connection(self) -> OllamaHealthResult:
        ...

    def list_models(self) -> list[OllamaModelInfo]:
        ...

    def generate(self, prompt: str, model: str, options: ModelOptions | None = None) -> LLMResponse:
        ...

    def stream_generate(self, prompt: str, model: str, options: ModelOptions | None = None):
        ...
```

功能要求：

```text
可設定 Ollama host，預設為 http://localhost:11434
可檢查 Ollama 是否啟動
可列出本機已安裝模型
可用指定模型產生回應
可支援 streaming chunk 輸出
可處理 timeout / connection error / model not found
```

---

### 5.2 LLM Gateway

建立 `gateway.py`，作為 SecretGuard 其他模組呼叫 LLM 的統一入口。

建議介面：

```python
class LLMGateway:
    def generate(self, safe_prompt: str, model: str, options: ModelOptions | None = None) -> LLMResponse:
        ...

    def stream_generate(self, safe_prompt: str, model: str, options: ModelOptions | None = None):
        ...
```

注意：本模組應接收 **safe_prompt**，不應直接處理未經前面防護流程處理的 raw user prompt。

---

### 5.3 Model Config

建立 `model_config.py`。

應支援模型生成參數：

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

要求：

```text
temperature 不可小於 0
top_p 需介於 0 到 1
num_ctx 需大於 0
num_predict 需大於 0
timeout_seconds 需大於 0
```

若參數不合法，需丟出明確錯誤或回傳標準錯誤結果。

---

### 5.4 Model Response

建立 `model_response.py`。

應定義標準資料格式，避免上層直接依賴 Ollama 原始 JSON。

建議格式：

```python
@dataclass
class LLMChunk:
    text: str
    model: str
    done: bool = False
    raw: dict | None = None
```

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

---

### 5.5 Error Handling

建立 `errors.py`。

建議錯誤類型：

```python
class LLMGatewayError(Exception):
    pass

class OllamaConnectionError(LLMGatewayError):
    pass

class OllamaModelNotFoundError(LLMGatewayError):
    pass

class OllamaTimeoutError(LLMGatewayError):
    pass

class OllamaGenerationError(LLMGatewayError):
    pass

class OllamaStreamError(LLMGatewayError):
    pass

class InvalidModelOptionsError(LLMGatewayError):
    pass
```

錯誤處理要求：

```text
Ollama 未啟動時，不可讓程式直接崩潰
模型不存在時，需回傳 model_not_found 類型錯誤
timeout 時，需回傳 timeout 類型錯誤
stream 中斷時，需回傳 stream_error
錯誤訊息不可包含完整 secret 或敏感 prompt
```

---

### 5.6 Streaming Support

`stream_generate()` 必須支援逐 chunk 回傳。

預期流程：

```python
for chunk in gateway.stream_generate(safe_prompt, model):
    # chunk 必須是 LLMChunk
    print(chunk.text)
```

每個 chunk 至少需要：

```text
text
model
done
raw
```

目的：

```text
讓 [12] Runtime Stream Monitor 可以逐 chunk 檢查
若偵測到 secret / leakage，可立即中斷生成流程
```

---

### 5.7 Runtime Monitor 中斷整合預留

本模組不需要完整實作 Runtime Stream Monitor，但必須預留中斷能力。

建議支援：

```python
def stream_generate(
    self,
    safe_prompt: str,
    model: str,
    options: ModelOptions | None = None,
    should_stop: Callable[[LLMChunk], bool] | None = None,
):
    ...
```

當 `should_stop(chunk)` 回傳 `True` 時：

```text
停止後續生成
回傳 stopped_by_guard=True
不可繼續輸出可疑內容
```

---

### 5.8 Metadata

模型回應需盡可能提供 metadata：

```text
model
prompt length
response length
duration
prompt tokens
completion tokens
total duration
是否被 guard 中斷
錯誤類型
```

目的：

```text
供 Event Logger 記錄
供 Report Generator 產生模型測試報告
供 benchmark 比較不同模型安全性與穩定性
```

---

## 6. TDD 開發策略

本任務必須採用 TDD。

開發順序如下：

```text
Step 1：先建立 llm_gateway/tests
Step 2：先寫測試案例
Step 3：執行 pytest，確認測試失敗
Step 4：實作最小功能讓測試通過
Step 5：補強錯誤處理與邊界案例
Step 6：重構程式碼
Step 7：再次執行全部測試
```

禁止先完整開發功能後才補測試。

---

## 7. 必要測試項目

### 7.1 Connection 測試

檔案：

```text
llm_gateway/tests/test_ollama_client_connection.py
```

測試案例：

```text
test_check_connection_success
test_check_connection_failed_when_ollama_is_down
test_connection_error_returns_safe_error
```

驗證：

```text
Ollama 可連線時，回傳 success
Ollama 不可連線時，回傳 connection error
不可讓未處理 exception 直接中斷測試
```

---

### 7.2 Model List 測試

檔案：

```text
llm_gateway/tests/test_ollama_client_models.py
```

測試案例：

```text
test_list_models_returns_model_info
test_list_models_handles_empty_model_list
test_list_models_handles_invalid_response
```

驗證：

```text
可解析 Ollama 模型清單
空清單可正常處理
回傳格式異常時可安全失敗
```

---

### 7.3 Generate 測試

檔案：

```text
llm_gateway/tests/test_ollama_client_generate.py
```

測試案例：

```text
test_generate_returns_llm_response
test_generate_uses_safe_prompt
test_generate_with_invalid_model_returns_model_not_found
test_generate_timeout_returns_timeout_error
test_generate_does_not_log_raw_secret_in_error
```

驗證：

```text
generate() 回傳 LLMResponse
response.success 正確
response.text 正確
response.model 正確
錯誤時 response.error_type 正確
錯誤內容不可包含完整 secret
```

---

### 7.4 Streaming 測試

檔案：

```text
llm_gateway/tests/test_ollama_client_stream.py
```

測試案例：

```text
test_stream_generate_yields_chunks
test_stream_generate_chunk_is_standardized
test_stream_generate_handles_done_chunk
test_stream_generate_can_be_interrupted
test_stream_generate_stops_when_should_stop_returns_true
```

驗證：

```text
stream_generate() 可逐 chunk 回傳
每個 chunk 都是 LLMChunk
done=True 時結束
should_stop 命中時停止
停止後不可繼續輸出後續 chunk
```

---

### 7.5 Gateway 測試

檔案：

```text
llm_gateway/tests/test_llm_gateway.py
```

測試案例：

```text
test_gateway_generate_delegates_to_ollama_client
test_gateway_stream_delegates_to_ollama_client
test_gateway_requires_safe_prompt
test_gateway_returns_standard_response
test_gateway_preserves_metadata
```

驗證：

```text
LLMGateway 正確呼叫 OllamaClient
輸入名稱使用 safe_prompt
回傳格式統一
metadata 可被保留
```

---

### 7.6 Error 測試

檔案：

```text
llm_gateway/tests/test_gateway_errors.py
```

測試案例：

```text
test_invalid_temperature_raises_error
test_invalid_top_p_raises_error
test_invalid_num_ctx_raises_error
test_invalid_num_predict_raises_error
test_invalid_timeout_raises_error
test_error_response_does_not_expose_sensitive_prompt
```

驗證：

```text
不合法模型參數會被拒絕
錯誤訊息安全
secret 不應出現在錯誤訊息中
```

---

## 8. Mock 測試要求

由於 CI 或本機環境不一定有啟動 Ollama，單元測試必須支援 mock。

測試中應使用：

```python
unittest.mock
pytest monkeypatch
fake response object
fake streaming iterator
```

避免測試強依賴本機實際模型。

可以另外保留 integration test，但預設 pytest 不應因為本機未安裝 Ollama 而失敗。

建議：

```text
單元測試：使用 mock，必須可穩定通過
整合測試：可用 pytest marker 標記為 integration
```

例如：

```python
@pytest.mark.integration
def test_real_ollama_generate():
    ...
```

---

## 9. 驗收標準

本任務完成時，必須滿足以下條件：

```text
[ ] 已建立 llm_gateway 模組
[ ] 已建立 llm_gateway/tests 測試資料夾
[ ] 已完成 OllamaClient
[ ] 已完成 LLMGateway
[ ] 已完成 ModelOptions
[ ] 已完成 LLMChunk / LLMResponse
[ ] 已完成錯誤類型 errors.py
[ ] generate() 可回傳標準 LLMResponse
[ ] stream_generate() 可逐 chunk 回傳 LLMChunk
[ ] stream_generate() 支援 should_stop 中斷條件
[ ] 錯誤處理不會洩漏 raw secret
[ ] pytest llm_gateway/tests -v 通過
```

---

## 10. 建議執行指令

在專案根目錄執行：

```bash
pytest llm_gateway/tests -v
```

若有 integration test：

```bash
pytest llm_gateway/tests -v -m integration
```

---

## 11. 最小完成版本定義

最小完成版本需至少支援：

```text
OllamaClient.check_connection()
OllamaClient.list_models()
OllamaClient.generate()
OllamaClient.stream_generate()
LLMGateway.generate()
LLMGateway.stream_generate()
ModelOptions validation
LLMResponse / LLMChunk standard format
basic error handling
mock-based pytest tests
```

---

## 12. 後續可擴充方向

本階段完成後，可在後續任務擴充：

```text
OpenAI-compatible API Gateway
multi-model benchmark
token usage 統計
runtime guard 深度整合
model latency report
model safety comparison report
local quantized model support
conversation chat format support
```

---

## 13. 開發提醒

此模組是 SecretGuard 的模型執行核心，但不應把所有防禦功能塞進來。

請保持架構乾淨：

```text
前面模組負責防禦判斷
llm_gateway 負責安全呼叫模型
後面模組負責 runtime 監控與 leakage 驗證
```

最終目標是讓 SecretGuard 可以穩定支援：

```text
Protected Prompt
    ↓
Restricted Token Guard
    ↓
llm_gateway
    ↓
Runtime Stream Monitor
    ↓
Output Guard
    ↓
Leakage Verifier
```
