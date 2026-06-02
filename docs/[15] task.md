# [15] Event Logger 開發任務

## 1. 任務目標

本任務要完成 SecretGuard 第 15 個流程模組：`Event Logger`。

`Event Logger` 是 SecretGuard 防禦流程中的安全事件紀錄與稽核模組，負責在一次請求完成後，將前面模組產生的防禦結果統一整理、遮蔽敏感資訊，並寫入 JSONL log，供後續除錯、統計、Benchmark Report、Policy Improvement 使用。

本模組不得重新判斷攻擊、不得重新計算風險分數、不得改寫 Prompt、不得直接做輸出過濾。它的職責是：

```text
收集防禦流程結果
↓
整理成標準事件格式
↓
遮蔽敏感資料
↓
寫入 logs/guard_events.jsonl
↓
提供查詢與摘要統計
```

---

## 2. 開發模式要求：TDD

本任務必須採用 TDD 開發模式。

開發順序必須為：

```text
1. 先在 event_logger/tests 撰寫測試
2. 執行測試，確認測試失敗
3. 再開始實作 event_logger 功能
4. 讓測試通過
5. 重構程式碼
6. 再次執行完整測試
```

禁止先完成主要功能後才補測試。

測試路徑固定為：

```text
event_logger/tests
```

驗收時必須能執行：

```bash
pytest event_logger/tests -v
```

並且所有測試必須通過。

---

## 3. 建議資料夾結構

請建立以下模組結構：

```text
event_logger/
├── __init__.py
├── event_schema.py
├── event_logger.py
├── event_writer.py
├── event_redactor.py
├── event_query.py
├── event_summary.py
└── tests/
    ├── test_event_schema.py
    ├── test_event_logger.py
    ├── test_event_writer.py
    ├── test_event_redactor.py
    ├── test_event_query.py
    └── test_event_summary.py
```

若專案已有共用 `core/defense_context.py` 或類似物件，可以讓 `EventLogger` 支援從 context 建立事件，但 Event Logger 本身不得強依賴大型外部流程，測試應可獨立執行。

---

## 4. 核心功能需求

### 4.1 GuardEvent Schema

建立 `GuardEvent` 資料結構，用於描述一次防禦流程事件。

必要欄位：

```text
event_id
timestamp
session_id
request_id
conversation_turn
user_role
authorization_status
attack_type
attack_category
matched_patterns
risk_score
risk_level
risk_factors
session_risk_score
policy_action
policy_reason
policy_rule_id
enabled_skills
skill_results
blocked
leakage_detected
leakage_type
leakage_level
matched_asset_ids
input_summary
output_summary
final_response_type
metadata
```

欄位要求：

- `event_id` 若未提供，需自動產生。
- `timestamp` 若未提供，需自動產生 ISO 8601 格式時間。
- `risk_score` 必須限制在 `0 ~ 100`。
- `risk_level` 建議支援：`low`、`medium`、`high`、`critical`。
- `policy_action` 建議支援：`ALLOW`、`WARN`、`REWRITE`、`RESTRICT`、`BLOCK`、`AUTHORIZE`、`ESCALATE`。
- `enabled_skills` 預設為空 list。
- `metadata` 預設為空 dict。

---

### 4.2 EventLogger 主入口

建立 `EventLogger` 類別，提供主要方法：

```python
logger = EventLogger(log_path="logs/guard_events.jsonl")
logger.log_event(event)
```

也需支援從 dict 建立 event：

```python
logger.log_event({
    "attack_type": "direct_secret_request",
    "risk_score": 95,
    "policy_action": "BLOCK",
    "blocked": True,
    "leakage_detected": False
})
```

功能要求：

- 可接收 `GuardEvent` 物件。
- 可接收 `dict` 並轉成 `GuardEvent`。
- 寫入前必須先經過 `EventRedactor`。
- 寫入結果必須是一行一筆 JSON。
- 不得因缺少非必要欄位而崩潰。

---

### 4.3 JSONL 寫入功能

建立 `EventWriter`，負責寫入 JSONL。

功能要求：

- 自動建立 `logs/` 資料夾。
- 使用 UTF-8 編碼。
- append 寫入，不覆蓋舊資料。
- 每筆事件佔一行。
- 寫入內容必須是合法 JSON。
- 支援自訂 log path，方便測試使用 temporary directory。

預設輸出位置：

```text
logs/guard_events.jsonl
```

---

### 4.4 敏感資訊遮蔽功能

建立 `EventRedactor`，負責遮蔽 log 中可能造成二次洩漏的敏感內容。

必須遮蔽：

```text
flag 格式，例如 picoCTF{...}
OpenAI / API Key 類型，例如 sk-...
private key 區塊
password 欄位
secret 欄位
完整 protected asset value
部分洩漏 evidence
```

遮蔽原則：

```text
完整機密 → [REDACTED_SECRET]
API Key → [REDACTED_API_KEY]
Private Key → [REDACTED_PRIVATE_KEY]
Password → [REDACTED_PASSWORD]
Partial evidence → [REDACTED_PARTIAL]
```

重要要求：

- Log 中不得保存完整 secret 原文。
- Redaction 不得破壞 JSON 結構。
- Redaction 不得產生巢狀錯誤字串，例如 `[REDACTED_[REDACTED_PARTIAL]]`。
- 若欄位名稱為 `secret`、`password`、`api_key`、`private_key`，即使值不符合 regex，也應遮蔽。

---

### 4.5 Event Query 查詢功能

建立 `EventQuery`，支援讀取 JSONL log 並查詢事件。

至少支援：

```text
讀取全部事件
讀取最近 N 筆事件
依 attack_type 過濾
依 policy_action 過濾
依 leakage_detected 過濾
依 blocked 過濾
依 risk_level 過濾
```

範例：

```python
query = EventQuery("logs/guard_events.jsonl")
blocked_events = query.filter(blocked=True)
high_risk_events = query.filter(risk_level="high")
recent_events = query.latest(10)
```

---

### 4.6 Event Summary 統計功能

建立 `EventSummary`，支援基礎統計。

至少支援輸出：

```text
total_events
allow_count
warn_count
rewrite_count
restrict_count
block_count
authorize_count
escalate_count
leakage_count
blocked_count
highest_risk_score
average_risk_score
most_common_attack_type
most_common_policy_action
most_common_enabled_skill
```

範例：

```python
summary = EventSummary(events).build()
```

輸出格式建議為 dict：

```json
{
  "total_events": 3,
  "block_count": 2,
  "leakage_count": 1,
  "highest_risk_score": 95,
  "most_common_attack_type": "direct_secret_request"
}
```

---

## 5. 測試要求

所有測試需放在：

```text
event_logger/tests
```

---

### 5.1 Schema 測試

檔案：

```text
event_logger/tests/test_event_schema.py
```

必測項目：

- 建立 `GuardEvent` 時會自動產生 `event_id`。
- 建立 `GuardEvent` 時會自動產生 `timestamp`。
- `risk_score` 小於 0 時應被修正或拒絕。
- `risk_score` 大於 100 時應被修正或拒絕。
- `enabled_skills` 預設為空 list。
- `metadata` 預設為空 dict。
- `GuardEvent.to_dict()` 可輸出合法 dict。
- `GuardEvent.from_dict()` 可由 dict 建立事件。

---

### 5.2 Logger 測試

檔案：

```text
event_logger/tests/test_event_logger.py
```

必測項目：

- `EventLogger.log_event()` 可以接收 `GuardEvent`。
- `EventLogger.log_event()` 可以接收 dict。
- 寫入前會呼叫 redaction。
- 缺少非必要欄位時不會崩潰。
- 寫入後 log 檔案存在。
- 寫入後可讀回同一筆事件。

---

### 5.3 Writer 測試

檔案：

```text
event_logger/tests/test_event_writer.py
```

必測項目：

- 自動建立 log 目錄。
- 每次 append 一行 JSON。
- 多次寫入不覆蓋舊事件。
- 寫入內容是 UTF-8。
- 寫入內容可以被 `json.loads()` 正確解析。

---

### 5.4 Redactor 測試

檔案：

```text
event_logger/tests/test_event_redactor.py
```

必測項目：

- `picoCTF{example_flag}` 會變成 `[REDACTED_SECRET]`。
- `sk-...` 類 API key 會變成 `[REDACTED_API_KEY]`。
- private key 區塊會變成 `[REDACTED_PRIVATE_KEY]`。
- password 欄位會變成 `[REDACTED_PASSWORD]`。
- secret 欄位會變成 `[REDACTED_SECRET]`。
- leakage evidence 可遮蔽成 `[REDACTED_PARTIAL]`。
- redaction 不會破壞巢狀 dict / list。
- redaction 不會產生巢狀錯誤 placeholder。

---

### 5.5 Query 測試

檔案：

```text
event_logger/tests/test_event_query.py
```

必測項目：

- 可以讀取全部事件。
- 可以讀取最近 N 筆事件。
- 可以依 `attack_type` 過濾。
- 可以依 `policy_action` 過濾。
- 可以依 `blocked` 過濾。
- 可以依 `leakage_detected` 過濾。
- 可以依 `risk_level` 過濾。
- 空 log 檔案時回傳空 list，不應崩潰。

---

### 5.6 Summary 測試

檔案：

```text
event_logger/tests/test_event_summary.py
```

必測項目：

- 可計算總事件數。
- 可計算各 policy action 次數。
- 可計算 block 次數。
- 可計算 leakage 次數。
- 可計算最高 risk score。
- 可計算平均 risk score。
- 可找出最常見 attack type。
- 可找出最常見 policy action。
- 可找出最常啟用 skill。
- 空事件 list 時應回傳合理預設值。

---

## 6. 建議實作介面

### 6.1 GuardEvent

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class GuardEvent:
    event_id: str | None = None
    timestamp: str | None = None
    session_id: str = "default"
    request_id: str | None = None
    conversation_turn: int = 1
    user_role: str = "guest"
    authorization_status: str = "unknown"
    attack_type: str = "unknown"
    attack_category: str = "unknown"
    matched_patterns: list[str] = field(default_factory=list)
    risk_score: int = 0
    risk_level: str = "low"
    risk_factors: list[str] = field(default_factory=list)
    session_risk_score: int = 0
    policy_action: str = "ALLOW"
    policy_reason: str = ""
    policy_rule_id: str | None = None
    enabled_skills: list[str] = field(default_factory=list)
    skill_results: list[dict[str, Any]] = field(default_factory=list)
    blocked: bool = False
    leakage_detected: bool = False
    leakage_type: str | None = None
    leakage_level: int = 0
    matched_asset_ids: list[str] = field(default_factory=list)
    input_summary: str = ""
    output_summary: str = ""
    final_response_type: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)
```

---

### 6.2 EventLogger

```python
class EventLogger:
    def __init__(self, log_path: str = "logs/guard_events.jsonl"):
        ...

    def log_event(self, event: GuardEvent | dict) -> GuardEvent:
        ...
```

---

### 6.3 EventWriter

```python
class EventWriter:
    def __init__(self, log_path: str):
        ...

    def write(self, event: dict) -> None:
        ...
```

---

### 6.4 EventRedactor

```python
class EventRedactor:
    def redact_event(self, event: dict) -> dict:
        ...

    def redact_text(self, text: str) -> str:
        ...
```

---

### 6.5 EventQuery

```python
class EventQuery:
    def __init__(self, log_path: str):
        ...

    def all(self) -> list[dict]:
        ...

    def latest(self, n: int) -> list[dict]:
        ...

    def filter(self, **criteria) -> list[dict]:
        ...
```

---

### 6.6 EventSummary

```python
class EventSummary:
    def __init__(self, events: list[dict]):
        ...

    def build(self) -> dict:
        ...
```

---

## 7. 範例事件格式

Event Logger 寫入 JSONL 的單筆事件格式如下：

```json
{
  "event_id": "evt_20260529_001",
  "timestamp": "2026-05-29T14:30:00+08:00",
  "session_id": "session_abc123",
  "request_id": "req_001",
  "conversation_turn": 1,
  "user_role": "guest",
  "authorization_status": "unauthorized",
  "attack_type": "direct_secret_request",
  "attack_category": "prompt_injection",
  "matched_patterns": ["flag", "show", "secret"],
  "risk_score": 95,
  "risk_level": "critical",
  "risk_factors": [
    "protected_asset_mentioned",
    "direct_secret_request",
    "unauthorized_role"
  ],
  "session_risk_score": 95,
  "policy_action": "BLOCK",
  "policy_reason": "User directly requested protected asset without authorization.",
  "policy_rule_id": "rule_block_direct_secret_request",
  "enabled_skills": [
    "direct_request_skill",
    "partial_disclosure_skill"
  ],
  "skill_results": [
    {
      "skill": "direct_request_skill",
      "detected": true,
      "action": "block",
      "reason": "Direct request for protected secret."
    }
  ],
  "blocked": true,
  "leakage_detected": false,
  "leakage_type": null,
  "leakage_level": 0,
  "matched_asset_ids": ["secret_001"],
  "input_summary": "User requested a protected flag directly.",
  "output_summary": "Request blocked before model output.",
  "final_response_type": "safe_refusal",
  "metadata": {
    "model": "llama3",
    "runtime": "ollama"
  }
}
```

---

## 8. 安全要求

Event Logger 本身必須符合安全設計。

### 8.1 不得記錄完整機密

以下內容不得原文寫入 log：

```text
flag
API key
password
token
private key
protected asset value
可重構 secret 的完整片段
```

### 8.2 僅允許記錄安全摘要

可記錄：

```text
asset_id
asset_type
risk_level
leakage_type
policy_action
redacted evidence
```

不可記錄：

```text
secret 原文
完整 prompt 中的機密
完整 output 中的機密
private key 原文
API key 原文
```

### 8.3 Log 不可成為新的攻擊面

需要避免：

```text
log_access_skill 被繞過後讀出 secret
測試報告包含 secret 原文
debug print 輸出 secret
錯誤訊息吐出 secret
```

---

## 9. 驗收標準

完成本任務時，必須符合以下條件：

```text
1. 已建立 event_logger 模組
2. 已建立 event_logger/tests 測試資料夾
3. 已先撰寫測試，再依測試完成開發
4. pytest event_logger/tests -v 全部通過
5. EventLogger 可寫入 logs/guard_events.jsonl
6. JSONL 每行都是合法 JSON
7. EventLogger 可記錄 attack_type、risk_score、policy_action、enabled_skills、blocked、leakage_detected
8. EventRedactor 可遮蔽 flag、API key、password、private key、secret 欄位
9. EventQuery 可讀取與過濾事件
10. EventSummary 可產生基本統計
11. Log 中不得出現完整 protected secret 原文
12. 程式碼需具備合理命名、型別提示與基本註解
```

驗收指令：

```bash
pytest event_logger/tests -v
```

建議額外執行：

```bash
python -m pytest event_logger/tests -v
```

---

## 10. 開發完成後需回報內容

開發完成後，請回報以下內容：

```text
1. 新增或修改了哪些檔案
2. Event Logger 目前支援哪些功能
3. 測試總數與通過數
4. pytest event_logger/tests -v 的執行結果
5. 是否確認 log 不會保存 secret 原文
6. 後續可優化項目
```

---

## 11. 後續可優化方向

本次任務先完成 MVP。後續可再加入：

```text
1. 支援依 session_id 輸出攻擊鏈紀錄
2. 支援匯出 CSV 報表
3. 支援與 ReportGenerator 整合
4. 支援與 Session Memory 整合
5. 支援事件嚴重度排序
6. 支援 policy improvement 建議
7. 支援 event replay，用於重現一次攻擊流程
8. 支援 benchmark run_id / model_name / attack_case_id 對照
```

---

## 12. 本任務完成定義

當以下條件全部滿足，即視為完成：

```text
event_logger 功能已完成
測試已完成
pytest event_logger/tests -v 全部通過
logs/guard_events.jsonl 可正常產生
事件內容完整且安全遮蔽
可查詢事件
可產生摘要統計
```
