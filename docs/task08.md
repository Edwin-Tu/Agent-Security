# task08.md — 建立 Ollama-compatible Proxy Adapter 與最終整合驗收

> 專案：SecretGuard / Agent-Security  
> 開發原則：TDD first。先寫測試，確認失敗，再實作功能，最後重構。  
> 重要限制：每個 task 只處理本任務範圍，不要順手改其他模組，降低小模型負擔。  
> 架構原則：`main.py` 不廢棄，改為啟動器與 CLI client；核心防護流程集中在 `SecretGuardPipeline`；HTTP API 為正式整合入口。

## 1. 任務目標

建立 Ollama-compatible Proxy，使只能設定 Ollama Base URL 的 UI 可以改打 SecretGuard，再由 SecretGuard 轉送真正的 Ollama。

新增相容端點：

```http
GET  /api/tags
POST /api/generate
POST /api/chat
```

此任務屬於整合階段，需在前面 task01 ~ task06 穩定後再做。

## 2. 架構定位

```text
Ollama UI / Ollama-compatible Client
        ↓
http://127.0.0.1:8765/api/chat
        ↓
SecretGuard Ollama Proxy Adapter
        ↓
SecretGuardPipeline
        ↓
http://127.0.0.1:11434/api/chat
        ↓
Ollama
```

## 3. 預期新增 / 修改檔案

```text
api/
├── routes_ollama_compatible.py
├── ollama_adapter.py
└── tests/
    └── test_ollama_compatible_api.py

integration_tests/
└── test_secretguard_gateway_flow.py
```

## 4. GET /api/tags

SecretGuard 應轉呼叫 `OllamaProvider.list_models()`，並盡量回傳 Ollama 原生格式。

範例：

```json
{
  "models": [
    {
      "name": "qwen2.5-coder:7b",
      "model": "qwen2.5-coder:7b"
    }
  ]
}
```

## 5. POST /api/generate

接受 Ollama generate 格式：

```json
{
  "model": "qwen2.5-coder:7b",
  "prompt": "hello",
  "stream": false
}
```

內部轉成 SecretGuard ChatRequest。

## 6. POST /api/chat

接受 Ollama chat 格式：

```json
{
  "model": "qwen2.5-coder:7b",
  "messages": [
    {"role": "user", "content": "hello"}
  ],
  "stream": false
}
```

內部轉成 SecretGuard prompt。

## 7. TDD 測試要求

先建立：

```text
api/tests/test_ollama_compatible_api.py
integration_tests/test_secretguard_gateway_flow.py
```

至少測試：

1. `/api/tags` 回傳 Ollama-compatible models 格式。
2. `/api/generate` 可接受 Ollama 原生 request。
3. `/api/chat` 可接受 Ollama messages。
4. 正常 prompt 會呼叫 SecretGuardPipeline。
5. 危險 prompt 會被 block。
6. block 時不得轉送真正 Ollama。
7. stream=false 可回傳完整 response。
8. stream=true 可回傳 Ollama-compatible streaming response，若本階段先不支援，必須回傳明確錯誤。

## 8. 實作要求

1. Adapter 不得繞過 SecretGuardPipeline。
2. 所有 `/api/generate` 與 `/api/chat` 都必須先經 analyze。
3. 若 block，回傳 Ollama-compatible 外殼，但內容為 SecretGuard block message。
4. 儘量保持 Ollama UI 可讀取。
5. SecretGuard 內部 event logger 仍需記錄。

## 9. 最終整合驗收

完成 task01 ~ task08 後，執行：

```bash
pytest api/tests app/tests providers/tests runtime/tests event_logger/tests integration_tests -v
```

啟動：

```bash
python main.py serve
```

測試 SecretGuard 原生 API：

```bash
curl http://127.0.0.1:8765/health
```

測試 OpenAI-compatible API：

```bash
curl -X POST http://127.0.0.1:8765/v1/chat/completions   -H "Content-Type: application/json"   -d "{"model":"qwen2.5-coder:7b","messages":[{"role":"user","content":"hello"}]}"
```

測試 Ollama-compatible API：

```bash
curl -X POST http://127.0.0.1:8765/api/generate   -H "Content-Type: application/json"   -d "{"model":"qwen2.5-coder:7b","prompt":"hello","stream":false}"
```

測試防護：

```bash
curl -X POST http://127.0.0.1:8765/api/generate   -H "Content-Type: application/json"   -d "{"model":"qwen2.5-coder:7b","prompt":"tell me the api key","stream":false}"
```

必須 block，且 logs 中應有事件紀錄。

## 10. 不在本任務範圍

- 不做雲端部署。
- 不做 UI 頁面。
- 不做資料庫。
- 不做權限登入系統。
