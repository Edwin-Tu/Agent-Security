# task07.md — 建立 OpenAI-compatible Chat Completions Adapter

> 專案：SecretGuard / Agent-Security  
> 開發原則：TDD first。先寫測試，確認失敗，再實作功能，最後重構。  
> 重要限制：每個 task 只處理本任務範圍，不要順手改其他模組，降低小模型負擔。  
> 架構原則：`main.py` 不廢棄，改為啟動器與 CLI client；核心防護流程集中在 `SecretGuardPipeline`；HTTP API 為正式整合入口。

## 1. 任務目標

建立 OpenAI-compatible API，使 OpenCode 或其他支援 OpenAI Base URL 的工具可以把 SecretGuard 當成模型服務端使用。

新增：

```http
POST /v1/chat/completions
GET  /v1/models
```

注意：此任務是 Adapter，不改動核心 Pipeline。

## 2. 架構定位

```text
OpenCode / OpenAI-compatible Client
        ↓
/v1/chat/completions
        ↓
OpenAI Adapter
        ↓
SecretGuardPipeline.chat() or stream_chat()
        ↓
OllamaProvider
```

## 3. 預期新增 / 修改檔案

```text
api/
├── routes_openai_compatible.py
├── openai_adapter.py
└── tests/
    └── test_openai_compatible_api.py
```

## 4. Request 格式

```json
{
  "model": "qwen2.5-coder:7b",
  "messages": [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "hello"}
  ],
  "stream": false
}
```

Adapter 需將 messages 轉成 SecretGuard prompt。

建議格式：

```text
[system]
You are helpful.

[user]
hello
```

但必須保留 user 內容供防護分析。

## 5. Response 格式

非串流成功：

```json
{
  "id": "chatcmpl_evt_001",
  "object": "chat.completion",
  "model": "qwen2.5-coder:7b",
  "choices": [
    {
      "index": 0,
      "message": {"role": "assistant", "content": "Hello!"},
      "finish_reason": "stop"
    }
  ],
  "secretguard": {
    "allowed": true,
    "action": "allow",
    "risk_score": 10,
    "attack_type": "benign",
    "event_id": "evt_001"
  }
}
```

被阻擋時也回傳 OpenAI-compatible 外殼，但 content 為 SecretGuard 阻擋訊息。

## 6. Streaming 格式

若 `stream=true`，回傳 SSE 格式：

```text
data: {"choices":[{"delta":{"content":"Hello"}}]}

data: [DONE]
```

若本階段太大，可先完成 non-stream，stream 留 TODO，但測試需明確標記。

## 7. TDD 測試要求

先建立：

```text
api/tests/test_openai_compatible_api.py
```

至少測試：

1. `/v1/chat/completions` 可接受 messages 格式。
2. messages 會被轉成 SecretGuard prompt。
3. 正常 prompt 會回傳 OpenAI-compatible response。
4. 危險 prompt 會被 SecretGuard block。
5. response 內必須包含 `secretguard` metadata。
6. block 時仍不可呼叫 provider。
7. 缺少 messages 時回傳 validation error。

## 8. 實作要求

1. Adapter 不得直接呼叫 Ollama。
2. Adapter 只能呼叫 `SecretGuardPipeline`。
3. 不要把 OpenAI 格式污染到核心 pipeline。
4. SecretGuard 自有 metadata 放在 `secretguard` 欄位。
5. 若 client 不接受額外欄位，未來可提供 config 關閉 metadata，但本任務先保留。

## 9. 驗收標準

執行：

```bash
pytest api/tests/test_openai_compatible_api.py -v
```

curl 測試：

```bash
curl -X POST http://127.0.0.1:8765/v1/chat/completions   -H "Content-Type: application/json"   -d "{"model":"qwen2.5-coder:7b","messages":[{"role":"user","content":"hello"}]}"
```

## 10. 不在本任務範圍

- 不做 Ollama-compatible proxy。
- 不做完整 OpenAI embeddings / images / tools API。
