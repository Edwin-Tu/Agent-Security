# task01.md — 建立 HTTP JSON API Server 骨架

> 專案：SecretGuard / Agent-Security  
> 開發原則：TDD first。先寫測試，確認失敗，再實作功能，最後重構。  
> 重要限制：每個 task 只處理本任務範圍，不要順手改其他模組，降低小模型負擔。  
> 架構原則：`main.py` 不廢棄，改為啟動器與 CLI client；核心防護流程集中在 `SecretGuardPipeline`；HTTP API 為正式整合入口。

## 1. 任務目標

建立 SecretGuard 的本地 HTTP JSON API Server 骨架，讓專案可以用 HTTP 方式啟動與檢查狀態。

此任務只做 API 基礎架構，不串接 Ollama，不實作完整防護流程。

## 2. 背景說明

SecretGuard 後續要支援 OpenCode、Ollama UI、自製 UI 與其他工具，因此不能只依賴 CLI 入口。新的定位是：

```text
UI / CLI / Agent Tool
        ↓ HTTP JSON
SecretGuard API Server
        ↓
SecretGuardPipeline
        ↓
Local LLM Provider
```

`main.py` 保留，但新增 `serve` 指令用來啟動 HTTP Server。

## 3. 預期新增 / 修改檔案

```text
api/
├── __init__.py
├── server.py
├── schemas.py
├── routes_health.py
└── tests/
    ├── __init__.py
    └── test_health_api.py

main.py
requirements.txt 或 pyproject.toml
```

## 4. API 規格

### GET /health

Response:

```json
{
  "status": "ok",
  "service": "secretguard",
  "version": "0.1.0"
}
```

## 5. TDD 測試要求

先建立測試檔：

```text
api/tests/test_health_api.py
```

至少包含：

1. `GET /health` 回傳 HTTP 200。
2. response JSON 包含 `status = ok`。
3. response JSON 包含 `service = secretguard`。
4. response JSON 包含 `version` 欄位。
5. 匯入 `api.server:app` 不會造成 side effect，例如自動連 Ollama。

範例測試方向：

```python
from fastapi.testclient import TestClient
from api.server import app

client = TestClient(app)


def test_health_api_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "secretguard"
    assert "version" in data
```

## 6. 實作要求

1. 使用 FastAPI 建立 `api/server.py`。
2. 在 `api/routes_health.py` 定義 health router。
3. `api/server.py` 只負責建立 app 與 include router。
4. 不要在 import 階段連接 Ollama。
5. `main.py` 新增 `serve` 指令。

建議啟動方式：

```bash
python main.py serve
```

也可以支援：

```bash
uvicorn api.server:app --host 127.0.0.1 --port 8765
```

## 7. 驗收標準

執行：

```bash
pytest api/tests -v
```

必須通過。

啟動：

```bash
python main.py serve
```

測試：

```bash
curl http://127.0.0.1:8765/health
```

應回傳：

```json
{
  "status": "ok",
  "service": "secretguard",
  "version": "0.1.0"
}
```

## 8. 不在本任務範圍

- 不做 `/v1/chat`。
- 不做 `/v1/analyze`。
- 不串接 Ollama。
- 不做 streaming。
- 不做 OpenAI-compatible API。
