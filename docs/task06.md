# task06.md — 建立 Event Logger 與統一錯誤處理

> 專案：SecretGuard / Agent-Security  
> 開發原則：TDD first。先寫測試，確認失敗，再實作功能，最後重構。  
> 重要限制：每個 task 只處理本任務範圍，不要順手改其他模組，降低小模型負擔。  
> 架構原則：`main.py` 不廢棄，改為啟動器與 CLI client；核心防護流程集中在 `SecretGuardPipeline`；HTTP API 為正式整合入口。

## 1. 任務目標

建立 SecretGuard HTTP Gateway 的事件記錄與錯誤處理機制。

所有 analyze、chat、stream 結果都應產生 event_id，並記錄 action、risk_score、attack_type、是否阻擋、是否呼叫 provider、是否洩漏。

## 2. 預期新增 / 修改檔案

```text
event_logger/
├── __init__.py
├── event_logger.py
└── tests/
    └── test_event_logger.py

app/
├── errors.py
└── tests/
    └── test_pipeline_error_handling.py

logs/
└── guard_events.jsonl
```

若專案已有 `event_logger` 或 `logs/guard_events.jsonl`，優先整合現有設計，不要重複造輪子。

## 3. Event JSONL 欄位

每一行為一筆 JSON：

```json
{
  "event_id": "evt_001",
  "timestamp": "2026-06-02T10:00:00+08:00",
  "session_id": "default",
  "route": "/v1/chat",
  "model": "qwen2.5-coder:7b",
  "action": "block",
  "allowed": false,
  "risk_score": 90,
  "attack_type": "direct_secret_request",
  "blocked_reason": "unauthorized protected asset request",
  "provider_called": false,
  "leakage_detected": false,
  "matched_assets": []
}
```

## 4. 錯誤格式

Provider error：

```json
{
  "allowed": false,
  "action": "error",
  "risk_score": 0,
  "attack_type": null,
  "response": "[SecretGuard] Provider error: Ollama is not available.",
  "error": "provider_error",
  "event_id": "evt_003"
}
```

Validation error 可交給 FastAPI 422。

## 5. TDD 測試要求

先建立：

```text
event_logger/tests/test_event_logger.py
app/tests/test_pipeline_error_handling.py
```

至少測試：

1. logger 會建立 JSONL 檔案。
2. 每次 log event 都是一行合法 JSON。
3. event 包含 event_id、timestamp、action、risk_score、attack_type。
4. chat 被 block 時會記錄 `provider_called=false`。
5. provider error 時會記錄 error event。
6. logger 寫入失敗時不應讓主要 chat API crash。
7. event_id 不重複。

## 6. 實作要求

建立：

```python
class EventLogger:
    def log(self, event: dict) -> str:
        ...
```

要求：

1. 預設寫入 `logs/guard_events.jsonl`。
2. 自動建立 logs 資料夾。
3. 使用 UTF-8。
4. 一次寫入一行 JSON。
5. event_id 若未提供，logger 自動補。
6. timestamp 使用 ISO 8601。
7. 不記錄完整 secret value；matched_assets 只記錄 asset_id、type、match_type，不寫原始機密值。

## 7. 驗收標準

執行：

```bash
pytest event_logger/tests app/tests -v
```

執行一次危險 prompt 後：

```bash
cat logs/guard_events.jsonl
```

應看到一筆 action 為 block 的事件。

## 8. 不在本任務範圍

- 不做報表生成。
- 不做 event dashboard。
- 不做資料庫儲存。
