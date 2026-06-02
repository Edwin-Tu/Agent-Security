# task05.md — 建立 /v1/chat/stream 與 Runtime Stream Monitor 整合

> 專案：SecretGuard / Agent-Security  
> 開發原則：TDD first。先寫測試，確認失敗，再實作功能，最後重構。  
> 重要限制：每個 task 只處理本任務範圍，不要順手改其他模組，降低小模型負擔。  
> 架構原則：`main.py` 不廢棄，改為啟動器與 CLI client；核心防護流程集中在 `SecretGuardPipeline`；HTTP API 為正式整合入口。

## 1. 任務目標

建立串流聊天 API：

```http
POST /v1/chat/stream
```

此 API 必須支援逐 chunk 回傳，並在生成過程中透過 Runtime Stream Monitor 即時檢查敏感 token、secret 片段與洩漏風險。

## 2. 核心流程

```text
HTTP Stream ChatRequest
 ↓
SecretGuardPipeline.analyze()
 ↓
若 block → 回傳 blocked event，結束
 ↓
Protected Prompt Builder
 ↓
OllamaProvider.stream_generate()
 ↓
每個 chunk 通過 Runtime Stream Monitor
 ↓
若命中 restricted token / secret → interrupt
 ↓
Output Guard final check
 ↓
Leakage Verifier
 ↓
Event Logger
```

## 3. 預期新增 / 修改檔案

```text
api/
├── routes_chat.py
└── tests/
    └── test_stream_chat_api.py

runtime/
├── stream_monitor.py
├── interruption_handler.py
└── tests/
    └── test_stream_monitor.py

app/
└── tests/
    └── test_secretguard_pipeline_stream.py
```

## 4. Streaming 格式

第一階段使用 NDJSON：

```text
application/x-ndjson
```

正常範例：

```json
{"type":"start","event_id":"evt_001","risk_score":10,"action":"allow"}
{"type":"token","content":"A"}
{"type":"token","content":" Python"}
{"type":"done","event_id":"evt_001"}
```

中斷範例：

```json
{"type":"start","event_id":"evt_002","risk_score":60,"action":"restrict"}
{"type":"token","content":"The"}
{"type":"blocked","reason":"restricted token detected","risk_score":95}
{"type":"done","event_id":"evt_002"}
```

## 5. TDD 測試要求

先建立：

```text
api/tests/test_stream_chat_api.py
runtime/tests/test_stream_monitor.py
app/tests/test_secretguard_pipeline_stream.py
```

至少測試：

1. 正常 prompt 可逐 chunk 回傳 token event。
2. 危險 prompt 在 analyze 階段被 block 時，不呼叫 provider stream。
3. stream 過程命中 `api_key`、`sk-`、`picoCTF{`、private key pattern 時會回傳 blocked event。
4. stream 過程被 blocked 後不得繼續輸出後續 token。
5. 最後必須回傳 done event。
6. Runtime Stream Monitor 可累積 chunk，以偵測跨 chunk secret。
7. provider stream error 時回傳 error event，不讓 server crash。

## 6. Runtime Stream Monitor 實作要求

建立：

```python
class StreamMonitor:
    def __init__(self, restricted_patterns: list[str] | None = None):
        ...

    def inspect_chunk(self, chunk: str) -> StreamCheckResult:
        ...
```

建立：

```python
class StreamCheckResult:
    allowed: bool
    reason: str | None
    risk_score: int
    matched_pattern: str | None
```

必須支援：

1. 單 chunk 敏感字偵測。
2. 跨 chunk buffer 偵測。
3. 命中後標記 `allowed = False`。
4. 不直接 print，不直接 exit，由 pipeline 決定中斷。

## 7. 驗收標準

執行：

```bash
pytest api/tests runtime/tests app/tests -v
```

使用 curl 測試：

```bash
curl -N -X POST http://127.0.0.1:8765/v1/chat/stream   -H "Content-Type: application/json"   -d "{"model":"qwen2.5-coder:7b","prompt":"explain python list"}"
```

必須逐行回傳 NDJSON。

## 8. 不在本任務範圍

- 不做 SSE。
- 不做 OpenAI-compatible streaming。
- 不做 Ollama-compatible proxy。
