# Runtime Monitor

## SecretGuard Runtime Stream Monitor Module

> SecretGuard 第 `[12] Runtime Stream Monitor` 模組  
> 在本地 LLM 生成過程中，逐 chunk 即時檢查輸出內容，若偵測到受保護資產、限制 token 或部分洩漏，立即中止生成並回傳安全訊息。

---

## 一、模組定位

`runtime_monitor` 是 SecretGuard 防禦流程中的 Runtime 層監控模組。

它位於：

```text
[11] Local LLM / Ollama
        ↓
[12] Runtime Stream Monitor
        ↓
[13] Output Guard
        ↓
[14] Leakage Verifier
        ↓
[15] Event Logger
```

一般 Output Guard 是在模型完整輸出後才檢查，而 Runtime Monitor 的重點是：

```text
模型正在生成時就檢查
命中敏感內容時立即中斷
避免完整 secret 被輸出到使用者端
```

因此它是 SecretGuard 從「輸出後過濾」升級到「生成中防護」的重要模組。

---

## 二、核心功能

Runtime Monitor 目前支援：

- 串流 chunk 即時檢查
- rolling buffer 跨 chunk 偵測
- exact secret 偵測
- partial secret leakage 偵測
- restricted token 偵測
- case-insensitive 比對
- 偵測後立即 interruption
- 回傳不含敏感值的安全替代訊息
- 限制 buffer 大小，避免長對話造成記憶體無限制成長
- 支援 stream 模式與完整 output check 模式

---

## 三、模組架構

```text
runtime_monitor/
├── __init__.py
├── stream_monitor.py              # RuntimeStreamMonitor：逐 chunk 檢查核心
├── monitor_result.py              # RuntimeMonitorResult：監控結果資料結構
├── interruption_handler.py        # InterruptionHandler：中斷狀態與安全回覆
├── runtime_guard.py               # RuntimeGuard：整合 monitor + handler
└── tests/
    ├── test_interruption_handler.py
    ├── test_runtime_guard.py
    ├── test_stream_monitor_partial_leakage.py
    ├── test_stream_monitor_restricted_tokens.py
    ├── test_stream_monitor_safe_output.py
    ├── test_stream_monitor_secret_detection.py
    └── test_stream_monitor_split_chunks.py
```

---

## 四、主要元件說明

### 4.1 RuntimeStreamMonitor

檔案：

```text
runtime_monitor/stream_monitor.py
```

負責逐段檢查模型輸出的 chunk。

主要方法：

```python
inspect_chunk(chunk: str) -> RuntimeMonitorResult
inspect_buffer() -> RuntimeMonitorResult
should_interrupt(result: RuntimeMonitorResult) -> bool
reset() -> None
```

主要偵測項目：

```text
1. exact_secret
   偵測完整受保護資產值

2. restricted_token
   偵測被限制輸出的 token，例如 sk-、BEGIN PRIVATE KEY

3. partial_secret
   偵測受保護資產的部分片段
```

---

### 4.2 RuntimeMonitorResult

檔案：

```text
runtime_monitor/monitor_result.py
```

Runtime 監控結果資料結構。

```python
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

欄位說明：

| 欄位 | 說明 |
|---|---|
| `allowed` | 是否允許該 chunk 繼續輸出 |
| `interrupted` | 是否需要中止生成 |
| `reason` | 偵測原因 |
| `matched_type` | 命中類型，例如 `exact_secret`、`partial_secret`、`restricted_token` |
| `matched_value` | 命中值；目前會以 `[REDACTED]` 表示，避免二次洩漏 |
| `risk_level` | 風險等級 |
| `safe_replacement` | 可選的安全替代內容 |

---

### 4.3 InterruptionHandler

檔案：

```text
runtime_monitor/interruption_handler.py
```

負責記錄中斷狀態與產生安全回覆。

主要方法：

```python
interrupt(reason: str = "", stage: str = "")
clear()
is_interrupted() -> bool
get_reason() -> str
build_safe_response(result: RuntimeMonitorResult) -> Optional[str]
```

當偵測到敏感內容時，會回傳：

```text
此回應可能包含受保護資訊，已中止生成。
我可以協助回答不涉及敏感內容的部分。
```

這個訊息不會包含原始 secret、partial secret 或 restricted token。

---

### 4.4 RuntimeGuard

檔案：

```text
runtime_monitor/runtime_guard.py
```

`RuntimeGuard` 是整合層，將 `RuntimeStreamMonitor` 與 `InterruptionHandler` 包裝成可直接使用的 runtime 防護器。

主要方法：

```python
process_stream(chunks: Iterable[str]) -> str
check_stream(chunks: Iterable[str]) -> str
check_output(text: str) -> dict
reset()
```

行為：

```text
安全 chunk → 繼續累積輸出
危險 chunk → 立即中止，不輸出危險內容，也不繼續處理後續 chunk
```

---

## 五、基本使用方式

### 5.1 檢查單一 chunk

```python
from runtime_monitor.stream_monitor import RuntimeStreamMonitor

monitor = RuntimeStreamMonitor(
    protected_assets=[
        {
            "value": "picoCTF{secret_123}",
            "risk_level": "high",
        }
    ],
    restricted_tokens=["BEGIN PRIVATE KEY", "sk-"],
)

result = monitor.inspect_chunk("The answer is picoCTF{secret_123}")

print(result.allowed)       # False
print(result.interrupted)   # True
print(result.matched_type)  # exact_secret
print(result.matched_value) # [REDACTED]
```

---

### 5.2 檢查串流輸出

```python
from runtime_monitor.stream_monitor import RuntimeStreamMonitor
from runtime_monitor.interruption_handler import InterruptionHandler
from runtime_monitor.runtime_guard import RuntimeGuard

monitor = RuntimeStreamMonitor(
    protected_assets=[
        {"value": "picoCTF{secret_123}", "risk_level": "high"}
    ],
    restricted_tokens=["sk-"],
)

handler = InterruptionHandler()
guard = RuntimeGuard(monitor, handler)

chunks = [
    "The answer is ",
    "picoCTF{secret_123}",
    " and this should not be shown.",
]

response = guard.process_stream(chunks)
print(response)
```

輸出：

```text
此回應可能包含受保護資訊，已中止生成。
我可以協助回答不涉及敏感內容的部分。
```

後續 chunk 不會繼續輸出。

---

### 5.3 安全輸出通過

```python
chunks = ["This is ", "a safe ", "response."]
response = guard.process_stream(chunks)

print(response)
```

輸出：

```text
This is a safe response.
```

---

### 5.4 完整輸出檢查

除了串流模式，也可以用於完整文字檢查：

```python
result = guard.check_output("Here is sk-abc123")
print(result)
```

可能輸出：

```python
{
    "blocked": True,
    "reason": "Detected restricted token in streaming output.",
    "matched_tokens": ["restricted_token"],
}
```

---

## 六、跨 chunk 偵測設計

LLM 串流輸出時，secret 可能不會一次出現在同一個 chunk，例如：

```text
chunk 1: pico
chunk 2: CTF
chunk 3: {secret_123}
```

Runtime Monitor 使用 rolling buffer 保存近期輸出內容，因此可以在多個 chunk 組合後偵測出完整 secret。

```python
monitor.inspect_chunk("pico")
monitor.inspect_chunk("CTF")
result = monitor.inspect_chunk("{secret_123}")

assert result.interrupted is True
```

這能避免攻擊者或模型透過分段輸出繞過單 chunk 檢查。

---

## 七、Partial Secret 偵測

Runtime Monitor 會根據受保護資產產生片段集合，用來偵測部分洩漏。

例如受保護資產：

```text
picoCTF{secret_123}
```

以下內容都可能被中止：

```text
picoCTF{
secret_123
CTF{sec
```

命中後回傳：

```text
matched_type = partial_secret
matched_value = [REDACTED]
```

目前 partial fragment 產生邏輯：

```text
長度 >= 7 的片段
若包含特殊字元則保留
或長度 >= 8 則保留
```

---

## 八、Restricted Token 偵測

可用來阻擋高風險 token 或敏感格式前綴，例如：

```text
BEGIN PRIVATE KEY
sk-
password
flag
```

範例：

```python
monitor = RuntimeStreamMonitor(
    protected_assets=[],
    restricted_tokens=["BEGIN PRIVATE KEY", "sk-"],
)

result = monitor.inspect_chunk("Here is BEGIN PRIVATE KEY")

assert result.interrupted is True
assert result.matched_type == "restricted_token"
```

比對採 case-insensitive。

---

## 九、建議串接流程

### 9.1 與 LLM Gateway 串接

```python
monitor = RuntimeStreamMonitor(
    protected_assets=protected_assets,
    restricted_tokens=restricted_tokens,
)
handler = InterruptionHandler()
guard = RuntimeGuard(monitor, handler)

safe_response = guard.process_stream(
    ollama_client.stream_generate(prompt)
)
```

流程：

```text
LLM Gateway stream chunk
        ↓
RuntimeGuard.process_stream()
        ↓
RuntimeStreamMonitor.inspect_chunk()
        ↓
若安全：append chunk
若危險：InterruptionHandler.build_safe_response()
```

---

### 9.2 與 Output Guard 串接

Runtime Monitor 是生成中防護，Output Guard 是輸出後防護。

建議兩者同時使用：

```text
Runtime Monitor
    ↓ 若未中斷
Output Guard
    ↓
Leakage Verifier
```

原因：

```text
Runtime Monitor 可提前中斷高風險生成
Output Guard 可做最後完整輸出檢查與 redaction
Leakage Verifier 可做更細緻的洩漏驗證
```

---

### 9.3 與 Event Logger 串接

當 Runtime Monitor 中止生成時，建議記錄事件：

```python
event = {
    "stage": "runtime_monitor",
    "action": "interrupt",
    "matched_type": result.matched_type,
    "risk_level": result.risk_level,
    "reason": result.reason,
}
```

注意：

```text
matched_value 應維持 [REDACTED]
不要把原始 secret 寫入 log
```

---

## 十、測試方式

在專案根目錄執行：

```bash
pytest runtime_monitor/tests -v
```

或在模組資料夾外層執行：

```bash
python -m pytest runtime_monitor/tests -v
```

目前測試結果：

```text
27 passed
```

---

## 十一、測試涵蓋範圍

目前測試涵蓋：

| 測試檔案 | 測試重點 |
|---|---|
| `test_stream_monitor_safe_output.py` | 安全 chunk、空 chunk、多段安全輸出、buffer 長度限制 |
| `test_stream_monitor_secret_detection.py` | 完整 secret、大小寫不敏感、matched value redaction |
| `test_stream_monitor_partial_leakage.py` | prefix、suffix、middle fragment 部分洩漏 |
| `test_stream_monitor_restricted_tokens.py` | restricted token、`sk-` 前綴、rolling buffer 命中 |
| `test_stream_monitor_split_chunks.py` | secret 跨 chunk 重組、buffer reset |
| `test_interruption_handler.py` | 安全回覆不包含 secret、restricted token 不外洩 |
| `test_runtime_guard.py` | 偵測後停止 stream、安全 stream 正常輸出 |

---

## 十二、目前限制

目前版本仍屬 Runtime Monitor 的基礎實作，限制包括：

1. 尚未支援語意型洩漏偵測
2. 尚未支援 Base64 / Hex / ROT13 等編碼型 runtime 偵測
3. partial fragment 規則仍偏固定，可能需要依資產類型調整
4. 尚未支援 token-level logits intervention
5. 尚未支援 async stream
6. 尚未與實際 Ollama stream API 完整綁定錯誤處理
7. 尚未輸出完整 audit metadata，例如 chunk index、timestamp、session id
8. 尚未支援多資產 hit ranking 或風險加權

---

## 十三、後續優化方向

建議下一階段可加入：

- async generator 版本的 `process_stream_async()`
- chunk index / token index / timestamp 紀錄
- encoding leakage runtime detection
- semantic leakage runtime detection
- reconstruction leakage 更精細化
- 與 `leakage_verifier` 共用 matcher 規則
- 與 `restricted_token_guard` 共用 token policy
- 支援不同風險等級的處置策略
- 支援 `redact_and_continue` 模式，而非一律中止
- 支援使用者自訂 safe response template
- 支援 Event Logger 自動紀錄 runtime interruption event
- 支援 Ollama / OpenAI-compatible API / local quantized model 多後端串流

---

## 十四、在 SecretGuard 中的價值

Runtime Monitor 的核心價值是：

```text
在模型真正把敏感內容完整輸出前攔截
```

它讓 SecretGuard 不只依賴輸出後檢查，而是在生成過程中就能執行防護。

完整防線可形成：

```text
Protected Prompt Builder
        ↓
Restricted Token Guard
        ↓
LLM Gateway
        ↓
Runtime Stream Monitor
        ↓
Output Guard
        ↓
Leakage Verifier
        ↓
Event Logger
```

這使 SecretGuard 更接近一套真正的 Local LLM Runtime Protection System。
