# Task: [12] Runtime Stream Monitor

## 1. 任務背景

SecretGuard 的系統流程中，`[12] Runtime Stream Monitor` 位於 `Local LLM / Ollama` 之後、`Output Guard` 之前，負責在模型生成過程中即時檢查 `token / secret / leakage`，並且在命中高風險內容時立即中斷生成。

本任務目標是建立一個可測試、可擴充的 Runtime 串流監控模組，使 SecretGuard 不只在輸出完成後才檢查，而是在模型逐 chunk 生成時即時防護。

---

## 2. 開發目標

請建立 `runtime_monitor` 模組，並採用 TDD 開發模式：

1. 先在 `runtime_monitor/tests` 撰寫測試。
2. 確認測試初始失敗。
3. 再開發 Runtime Stream Monitor 功能。
4. 最後執行測試並確保全部通過。

驗收時必須同時包含：

- `runtime_monitor/tests` 測試檔案
- Runtime Stream Monitor 功能實作
- 測試全部通過

---

## 3. 建議目錄結構

```text
runtime_monitor/
├── __init__.py
├── stream_monitor.py
├── monitor_result.py
├── interruption_handler.py
├── runtime_guard.py
└── tests/
    ├── __init__.py
    ├── test_stream_monitor_safe_output.py
    ├── test_stream_monitor_secret_detection.py
    ├── test_stream_monitor_partial_leakage.py
    ├── test_stream_monitor_split_chunks.py
    ├── test_stream_monitor_restricted_tokens.py
    ├── test_interruption_handler.py
    └── test_runtime_guard.py
```

---

## 4. 核心功能需求

### 4.1 Streaming Chunk Monitor

`RuntimeStreamMonitor` 必須能逐 chunk 接收模型輸出內容。

範例：

```text
chunk 1: "The"
chunk 2: " flag"
chunk 3: " is"
chunk 4: " picoCTF{"
```

每收到一個 chunk，都必須立即進行安全檢查。

---

### 4.2 Rolling Buffer 機制

因為敏感內容可能被模型拆成多個 chunk 輸出，所以不能只檢查單一 chunk。

必須保存最近輸出的文字內容，例如：

```text
rolling_buffer = 最近 500 ~ 2000 字元
```

每次新 chunk 進來時，都要檢查：

```text
current_chunk
rolling_buffer + current_chunk
normalized_buffer
```

必須能偵測跨 chunk 的敏感內容。

範例：

```text
chunk 1: "pico"
chunk 2: "CTF"
chunk 3: "{secret}"
```

合併後為：

```text
picoCTF{secret}
```

此情況必須中斷生成。

---

### 4.3 Restricted Token Detection

必須能偵測高風險 token，例如：

```text
flag
password
api_key
token
private_key
system prompt
picoCTF{
sk-
BEGIN PRIVATE KEY
```

當 chunk 或 rolling buffer 命中 restricted token 時，應回傳 `interrupted=True`。

---

### 4.4 Protected Asset Matching

Runtime Stream Monitor 必須能接收受保護資產清單，例如：

```python
protected_assets = [
    {
        "asset_id": "secret_001",
        "name": "competition_flag",
        "type": "flag",
        "value": "picoCTF{secret_123}",
        "aliases": ["flag", "答案", "通關碼"],
        "risk_level": "high"
    }
]
```

需支援以下比對：

- exact secret match
- alias match
- prefix match
- partial fragment match
- split chunk reconstruction match

---

### 4.5 Partial Leakage Detection

不得只偵測完整 secret，也需要偵測部分洩漏。

例如 protected secret 為：

```text
picoCTF{secret_123}
```

以下輸出都應被視為風險：

```text
picoCTF{
secret_123
前 5 碼是 picoC
答案開頭是 pico
```

需針對 partial leakage 回傳明確原因，例如：

```text
matched_type = "partial_secret"
reason = "Detected partial leakage of protected asset."
```

---

### 4.6 Runtime Interruption

一旦偵測到高風險內容，必須立即中斷。

中斷結果應包含：

```python
RuntimeMonitorResult(
    allowed=False,
    interrupted=True,
    reason="Detected protected secret in streaming output.",
    matched_type="exact_secret",
    matched_value="[REDACTED]",
    risk_level="high",
    safe_replacement="此回應可能包含受保護資訊，已中止生成。"
)
```

不得將原始敏感內容回傳給使用者。

---

### 4.7 Safe Replacement Response

中斷後應提供安全替代訊息，例如：

```text
此回應可能包含受保護資訊，已中止生成。
我可以協助回答不涉及敏感內容的部分。
```

該訊息應由 `interruption_handler.py` 統一產生。

---

### 4.8 Reset Buffer

每次新的請求或新的 session 開始時，必須能清空 buffer。

需要提供：

```python
monitor.reset()
```

避免上一輪輸出影響下一輪檢查。

---

## 5. 建議類別設計

### 5.1 RuntimeMonitorResult

檔案：`runtime_monitor/monitor_result.py`

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class RuntimeMonitorResult:
    allowed: bool
    interrupted: bool
    reason: str
    matched_type: Optional[str] = None
    matched_value: Optional[str] = None
    risk_level: str = "low"
    safe_replacement: Optional[str] = None
```

---

### 5.2 RuntimeStreamMonitor

檔案：`runtime_monitor/stream_monitor.py`

```python
class RuntimeStreamMonitor:
    def __init__(self, protected_assets=None, restricted_tokens=None, max_buffer_size=2000):
        ...

    def inspect_chunk(self, chunk: str) -> RuntimeMonitorResult:
        ...

    def inspect_buffer(self) -> RuntimeMonitorResult:
        ...

    def should_interrupt(self, result: RuntimeMonitorResult) -> bool:
        ...

    def reset(self) -> None:
        ...
```

---

### 5.3 InterruptionHandler

檔案：`runtime_monitor/interruption_handler.py`

```python
class InterruptionHandler:
    def build_safe_response(self, result: RuntimeMonitorResult) -> str:
        ...
```

---

### 5.4 RuntimeGuard

檔案：`runtime_monitor/runtime_guard.py`

`RuntimeGuard` 負責整合 stream monitor 與 interruption handler。

建議功能：

```python
class RuntimeGuard:
    def __init__(self, monitor, interruption_handler):
        ...

    def process_stream(self, chunks):
        ...
```

`process_stream()` 應能接收 iterator / list of chunks，逐 chunk 檢查。

若安全，回傳完整內容。

若命中風險，立即停止處理後續 chunk，並回傳 safe replacement。

---

## 6. TDD 測試要求

### 6.1 Safe Output 測試

檔案：`runtime_monitor/tests/test_stream_monitor_safe_output.py`

必須測試：

- 一般安全文字不會中斷
- `allowed=True`
- `interrupted=False`

測試案例：

```python
def test_allows_safe_stream_chunk():
    monitor = RuntimeStreamMonitor(
        protected_assets=[],
        restricted_tokens=["flag", "password"]
    )

    result = monitor.inspect_chunk("This is a normal explanation about Python.")

    assert result.allowed is True
    assert result.interrupted is False
```

---

### 6.2 Exact Secret 測試

檔案：`runtime_monitor/tests/test_stream_monitor_secret_detection.py`

必須測試完整 secret 命中時中斷。

```python
def test_interrupts_exact_secret_chunk():
    monitor = RuntimeStreamMonitor(
        protected_assets=[{"value": "picoCTF{secret_123}", "risk_level": "high"}],
        restricted_tokens=[]
    )

    result = monitor.inspect_chunk("The answer is picoCTF{secret_123}")

    assert result.allowed is False
    assert result.interrupted is True
    assert result.matched_type == "exact_secret"
```

---

### 6.3 Split Chunk 測試

檔案：`runtime_monitor/tests/test_stream_monitor_split_chunks.py`

必須測試 secret 被拆開輸出時仍會中斷。

```python
def test_interrupts_secret_split_across_chunks():
    monitor = RuntimeStreamMonitor(
        protected_assets=[{"value": "picoCTF{secret_123}", "risk_level": "high"}],
        restricted_tokens=[]
    )

    result1 = monitor.inspect_chunk("pico")
    result2 = monitor.inspect_chunk("CTF")
    result3 = monitor.inspect_chunk("{secret_123}")

    assert result1.interrupted is False
    assert result2.interrupted is False
    assert result3.interrupted is True
    assert result3.matched_type in ["exact_secret", "reconstructed_secret"]
```

---

### 6.4 Restricted Token 測試

檔案：`runtime_monitor/tests/test_stream_monitor_restricted_tokens.py`

必須測試 restricted token 命中。

```python
def test_interrupts_restricted_token():
    monitor = RuntimeStreamMonitor(
        protected_assets=[],
        restricted_tokens=["BEGIN PRIVATE KEY", "sk-"]
    )

    result = monitor.inspect_chunk("Here is BEGIN PRIVATE KEY")

    assert result.interrupted is True
    assert result.matched_type == "restricted_token"
```

---

### 6.5 Partial Leakage 測試

檔案：`runtime_monitor/tests/test_stream_monitor_partial_leakage.py`

必須測試 secret 前綴或片段外洩。

```python
def test_detects_partial_secret_prefix():
    monitor = RuntimeStreamMonitor(
        protected_assets=[{"value": "picoCTF{secret_123}", "risk_level": "high"}],
        restricted_tokens=[]
    )

    result = monitor.inspect_chunk("The flag starts with picoCTF{")

    assert result.interrupted is True
    assert result.matched_type == "partial_secret"
```

---

### 6.6 Buffer Reset 測試

必須測試 `reset()` 可以清空前一輪內容。

```python
def test_resets_buffer_between_requests():
    monitor = RuntimeStreamMonitor(
        protected_assets=[{"value": "picoCTF{secret_123}", "risk_level": "high"}],
        restricted_tokens=[]
    )

    monitor.inspect_chunk("pico")
    monitor.reset()
    result = monitor.inspect_chunk("CTF{secret_123}")

    assert result.interrupted is False
```

---

### 6.7 Interruption Handler 測試

檔案：`runtime_monitor/tests/test_interruption_handler.py`

必須測試中斷後不會回傳敏感內容。

```python
def test_safe_response_does_not_include_secret():
    handler = InterruptionHandler()
    result = RuntimeMonitorResult(
        allowed=False,
        interrupted=True,
        reason="Detected protected secret.",
        matched_type="exact_secret",
        matched_value="picoCTF{secret_123}",
        risk_level="high"
    )

    response = handler.build_safe_response(result)

    assert "picoCTF{secret_123}" not in response
    assert "受保護資訊" in response
```

---

### 6.8 Runtime Guard 測試

檔案：`runtime_monitor/tests/test_runtime_guard.py`

必須測試整合流程。

```python
def test_runtime_guard_stops_stream_after_detection():
    monitor = RuntimeStreamMonitor(
        protected_assets=[{"value": "picoCTF{secret_123}", "risk_level": "high"}],
        restricted_tokens=[]
    )
    handler = InterruptionHandler()
    guard = RuntimeGuard(monitor, handler)

    chunks = ["The answer is ", "picoCTF{secret_123}", " do not show this later"]
    response = guard.process_stream(chunks)

    assert "picoCTF{secret_123}" not in response
    assert "do not show this later" not in response
    assert "受保護資訊" in response
```

---

## 7. 實作規則

### 7.1 不可回傳敏感內容

任何 result 或 safe response 都不得直接輸出完整 secret。

若需要記錄 matched value，請使用：

```text
[REDACTED]
```

---

### 7.2 比對需支援大小寫正規化

至少需支援：

```python
text.lower()
```

讓以下情況也能被偵測：

```text
PICOCTF{
picoctf{
PicoCTF{
```

---

### 7.3 Buffer 長度限制

`max_buffer_size` 預設建議為 2000。

當 buffer 超過限制時，只保留最後 `max_buffer_size` 字元。

---

### 7.4 中斷後不處理後續 chunk

`RuntimeGuard.process_stream()` 一旦偵測到 `interrupted=True`，必須停止處理後續 chunk。

---

## 8. 非本階段必要功能

以下功能可列為下一階段，不要求本次完成：

- Base64 / Hex / ROT13 解碼偵測
- Unicode homoglyph normalization
- 語意相似度偵測
- 真正串接 Ollama streaming API
- event logger JSONL 寫入
- session risk escalation
- logit-level intervention

---

## 9. 驗收標準

本任務完成時，需符合以下條件：

1. 已建立 `runtime_monitor` 模組。
2. 已建立 `runtime_monitor/tests` 測試資料夾。
3. 所有核心功能皆先有測試，再進行實作。
4. 測試需涵蓋：
   - safe output
   - exact secret detection
   - restricted token detection
   - partial secret detection
   - split chunk reconstruction
   - buffer reset
   - interruption handler
   - runtime guard integration
5. 執行以下指令應全部通過：

```bash
pytest runtime_monitor/tests -v
```

6. Runtime Stream Monitor 必須能逐 chunk 檢查輸出。
7. Runtime Stream Monitor 必須能偵測 rolling buffer 中的跨 chunk secret。
8. 命中敏感內容時必須立即中斷。
9. 中斷後不得回傳原始 secret。
10. 必須提供安全替代訊息。

---

## 10. 建議開發順序

```text
Step 1: 建立 runtime_monitor/tests
Step 2: 撰寫 RuntimeMonitorResult 測試
Step 3: 撰寫 safe output 測試
Step 4: 撰寫 exact secret detection 測試
Step 5: 撰寫 restricted token 測試
Step 6: 撰寫 split chunk / rolling buffer 測試
Step 7: 撰寫 partial leakage 測試
Step 8: 撰寫 interruption handler 測試
Step 9: 撰寫 runtime guard integration 測試
Step 10: 實作 monitor_result.py
Step 11: 實作 stream_monitor.py
Step 12: 實作 interruption_handler.py
Step 13: 實作 runtime_guard.py
Step 14: 執行 pytest runtime_monitor/tests -v
Step 15: 修正直到所有測試通過
```

---

## 11. 完成定義

本任務完成後，SecretGuard 應具備第一版 Runtime Stream Monitor 能力：

```text
Local LLM streaming output
        ↓
Runtime Stream Monitor
        ↓
逐 chunk 檢查 token / secret / partial leakage
        ↓
命中高風險內容立即中斷
        ↓
回傳 safe replacement
        ↓
避免敏感資訊在完整輸出前外洩
```
