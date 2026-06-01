# Event Logger

> SecretGuard event logging module for recording, redacting, querying, and summarizing security events.

`event_logger` 是 SecretGuard 流程中的第 **[15] Event Logger** 模組，負責在一次防禦流程結束後，記錄本次請求的攻擊類型、風險分數、防禦動作、啟用技能、是否阻擋、是否發生洩漏等資訊。

此模組的設計重點不是單純寫入 log，而是建立一套可供後續稽核、報告產生、風險分析與規則優化使用的安全事件紀錄格式。

---

## 1. 模組定位

在 SecretGuard 的完整防禦流程中，Event Logger 位於最後階段：

```text
User Prompt
   ↓
Protected Asset Registry
   ↓
Input Normalization
   ↓
Input Guard
   ↓
Attack Classifier
   ↓
Risk Scoring Engine
   ↓
Defense Policy Engine
   ↓
Skill Router / Defensive Skill
   ↓
Protected Prompt Builder
   ↓
Restricted Token Guard
   ↓
Local LLM / Ollama
   ↓
Runtime Stream Monitor
   ↓
Output Guard
   ↓
Leakage Verifier
   ↓
Event Logger
   ↓
Final Safe Response
```

Event Logger 會將前面模組產生的防禦結果整理成標準化事件，並以 JSONL 格式保存。

---

## 2. 核心功能

### 2.1 安全事件記錄

支援記錄以下資訊：

- event id
- timestamp
- session id
- request id
- conversation turn
- user role
- authorization status
- attack type
- attack category
- matched patterns
- risk score
- risk level
- risk factors
- session risk score
- policy action
- policy reason
- enabled skills
- skill results
- blocked status
- leakage detected status
- leakage type
- leakage level
- matched asset ids
- input summary
- output summary
- metadata

---

### 2.2 JSONL 寫入

每一筆事件會以一行 JSON 的形式寫入 `.jsonl` 檔案。

預設路徑：

```text
logs/guard_events.jsonl
```

此格式適合：

- 持續追加事件
- 日後查詢
- 報告產生
- benchmark 分析
- 外部 SIEM 或 log pipeline 串接

---

### 2.3 敏感資訊遮罩

事件寫入前會先經過 `EventRedactor` 遮罩，避免 log 本身變成洩漏來源。

目前支援遮罩：

- CTF flag
- API key，例如 `sk-...`
- Private key block
- password 欄位
- secret 欄位
- api_key 欄位
- private_key 欄位
- leakage_evidence 欄位
- 巢狀 dict / list 中的敏感內容

遮罩結果範例：

```text
[REDACTED_SECRET]
[REDACTED_API_KEY]
[REDACTED_PRIVATE_KEY]
[REDACTED_PASSWORD]
[REDACTED_PARTIAL]
```

---

### 2.4 事件查詢

`EventQuery` 支援：

- 讀取全部事件
- 讀取最新 N 筆事件
- 依欄位條件過濾事件
- 忽略損壞或無法解析的 JSONL 行
- log 檔不存在時回傳空清單

---

### 2.5 事件摘要統計

`EventSummary` 可將事件清單轉換成統計摘要，包含：

- total events
- allow count
- warn count
- rewrite count
- restrict count
- block count
- authorize count
- escalate count
- leakage count
- blocked count
- highest risk score
- average risk score
- most common attack type
- most common policy action
- most common enabled skill

---

## 3. 專案結構

```text
event_logger/
├── __init__.py
├── event_logger.py          # 對外主要介面，整合 schema、redactor、writer
├── event_schema.py          # GuardEvent 資料結構與序列化
├── event_writer.py          # JSONL 寫入器
├── event_redactor.py        # 敏感資訊遮罩
├── event_query.py           # log 查詢工具
├── event_summary.py         # 事件摘要統計
└── tests/
    ├── __init__.py
    ├── test_event_logger.py
    ├── test_event_schema.py
    ├── test_event_writer.py
    ├── test_event_redactor.py
    ├── test_event_query.py
    └── test_event_summary.py
```

---

## 4. 安裝與環境需求

此模組目前只依賴 Python 標準函式庫。

建議環境：

```text
Python 3.10+
pytest
```

安裝測試工具：

```bash
pip install pytest
```

---

## 5. 使用方式

### 5.1 建立 GuardEvent 並寫入 log

```python
from event_logger import EventLogger, GuardEvent

logger = EventLogger(log_path="logs/guard_events.jsonl")

event = GuardEvent(
    session_id="session_001",
    request_id="req_001",
    conversation_turn=1,
    user_role="guest",
    authorization_status="unauthorized",
    attack_type="direct_secret_request",
    attack_category="secret_extraction",
    matched_patterns=["tell me the api key"],
    risk_score=95,
    risk_level="critical",
    risk_factors=["direct_secret_request", "protected_asset_matched"],
    session_risk_score=95,
    policy_action="BLOCK",
    policy_reason="unauthorized asset request",
    enabled_skills=["DirectRequestSkill"],
    blocked=True,
    leakage_detected=False,
    matched_asset_ids=["asset_api_key_001"],
    input_summary="User requested API key",
    output_summary="Request blocked by SecretGuard",
    final_response_type="blocked_response",
)

logger.log_event(event)
```

---

### 5.2 直接使用 dict 寫入事件

```python
from event_logger import EventLogger

logger = EventLogger(log_path="logs/guard_events.jsonl")

logger.log_event({
    "attack_type": "encoding_bypass",
    "attack_category": "obfuscation",
    "risk_score": 80,
    "risk_level": "high",
    "policy_action": "BLOCK",
    "blocked": True,
    "input_summary": "User attempted Base64 extraction",
})
```

`EventLogger` 會自動將 dict 轉換成 `GuardEvent`。

---

### 5.3 查詢全部事件

```python
from event_logger import EventQuery

query = EventQuery("logs/guard_events.jsonl")

events = query.all()
print(events)
```

---

### 5.4 查詢最新 N 筆事件

```python
from event_logger import EventQuery

query = EventQuery("logs/guard_events.jsonl")

latest_events = query.latest(5)
print(latest_events)
```

---

### 5.5 依條件過濾事件

```python
from event_logger import EventQuery

query = EventQuery("logs/guard_events.jsonl")

blocked_events = query.filter(blocked=True)
critical_events = query.filter(risk_level="critical")
leakage_events = query.filter(leakage_detected=True)
```

---

### 5.6 建立事件摘要

```python
from event_logger import EventQuery, EventSummary

query = EventQuery("logs/guard_events.jsonl")
events = query.all()

summary = EventSummary(events).build()
print(summary)
```

輸出範例：

```python
{
    "total_events": 5,
    "allow_count": 1,
    "warn_count": 1,
    "rewrite_count": 0,
    "restrict_count": 0,
    "block_count": 2,
    "authorize_count": 0,
    "escalate_count": 0,
    "leakage_count": 1,
    "blocked_count": 2,
    "highest_risk_score": 95,
    "average_risk_score": 53.0,
    "most_common_attack_type": "direct_request",
    "most_common_policy_action": "BLOCK",
    "most_common_enabled_skill": "skill_a"
}
```

---

## 6. GuardEvent 欄位說明

| 欄位 | 說明 |
|---|---|
| `event_id` | 事件 ID，未提供時自動產生 |
| `timestamp` | UTC ISO timestamp，未提供時自動產生 |
| `session_id` | 對話 session id |
| `request_id` | 單次請求 id |
| `conversation_turn` | 第幾輪對話 |
| `user_role` | 使用者角色 |
| `authorization_status` | 授權狀態 |
| `attack_type` | 攻擊類型 |
| `attack_category` | 攻擊分類 |
| `matched_patterns` | 命中的攻擊模式 |
| `risk_score` | 單次風險分數，範圍 0–100 |
| `risk_level` | 風險等級，例如 low / medium / high / critical |
| `risk_factors` | 風險來源 |
| `session_risk_score` | 多輪對話累積風險 |
| `policy_action` | 防禦動作，例如 ALLOW / WARN / BLOCK |
| `policy_reason` | 防禦原因 |
| `policy_rule_id` | 命中的政策規則 ID |
| `enabled_skills` | 啟用的 Defensive Skills |
| `skill_results` | Skill detect / defend 結果 |
| `blocked` | 是否阻擋 |
| `leakage_detected` | 是否偵測到洩漏 |
| `leakage_type` | 洩漏類型 |
| `leakage_level` | 洩漏等級 |
| `matched_asset_ids` | 命中的受保護資產 ID |
| `input_summary` | 使用者輸入摘要 |
| `output_summary` | 模型輸出摘要 |
| `final_response_type` | 最終回應類型 |
| `metadata` | 額外資訊 |

---

## 7. 測試方式

在專案根目錄執行：

```bash
pytest event_logger/tests -v
```

目前測試結果：

```text
44 passed
```

測試涵蓋：

- `GuardEvent` 自動產生 event id
- `GuardEvent` 自動產生 timestamp
- `risk_score` 自動限制在 0–100
- dict 轉換為 `GuardEvent`
- JSONL 寫入與追加
- UTF-8 中文寫入
- 敏感資訊遮罩
- 巢狀 dict / list 遮罩
- 避免 nested placeholder，例如 `[REDACTED_[REDACTED...]]`
- 查詢全部事件
- 查詢最新事件
- 依條件過濾事件
- 空 log 處理
- 事件摘要統計

---

## 8. 與 SecretGuard 其他模組串接

Event Logger 通常會在完整防禦流程的最後被呼叫。

範例：

```python
from event_logger import EventLogger

logger = EventLogger("logs/guard_events.jsonl")

logger.log_event({
    "session_id": defense_context.session_id,
    "request_id": defense_context.request_id,
    "conversation_turn": defense_context.turn,
    "user_role": defense_context.user_role,
    "authorization_status": defense_context.authorization_status,
    "attack_type": classifier_result.attack_type,
    "attack_category": classifier_result.category,
    "matched_patterns": classifier_result.matched_patterns,
    "risk_score": risk_result.score,
    "risk_level": risk_result.level,
    "risk_factors": risk_result.factors,
    "session_risk_score": session_memory.risk_score,
    "policy_action": policy_result.action,
    "policy_reason": policy_result.reason,
    "policy_rule_id": policy_result.rule_id,
    "enabled_skills": skill_router.enabled_skill_names,
    "skill_results": skill_router.results,
    "blocked": policy_result.blocked,
    "leakage_detected": leakage_result.detected,
    "leakage_type": leakage_result.type,
    "leakage_level": leakage_result.level,
    "matched_asset_ids": leakage_result.asset_ids,
    "input_summary": input_summary,
    "output_summary": output_summary,
    "final_response_type": final_response.type,
    "metadata": {
        "model": "ollama/qwen2.5-coder:7b",
        "runtime": "ollama",
    },
})
```

---

## 9. 設計原則

### 9.1 Log 不應保存原始機密

Event Logger 會在寫入前遮罩敏感資訊，避免 log 檔成為新的攻擊目標。

### 9.2 事件格式需穩定

`GuardEvent` 提供固定欄位，方便後續報告產生、benchmark 分析與跨模組串接。

### 9.3 JSONL 優先於單一 JSON

JSONL 適合長期追加，不需要每次讀取整份檔案後再重寫。

### 9.4 查詢與摘要獨立於寫入流程

`EventWriter` 只負責寫入；`EventQuery` 與 `EventSummary` 負責讀取與分析，讓模組職責清楚。

---

## 10. 後續可優化方向

建議下一階段可加入：

1. CLI 查詢工具
   - `python -m event_logger latest 10`
   - `python -m event_logger summary`
   - `python -m event_logger filter --policy-action BLOCK`

2. 更完整的欄位驗證
   - 驗證 `policy_action` 是否為合法值
   - 驗證 `risk_level` 是否為合法值
   - 驗證 `leakage_level` 範圍

3. Log rotation
   - 依日期切分 log
   - 避免單一檔案過大

4. 匯出報告格式
   - Markdown
   - CSV
   - HTML
   - JSON summary

5. 與 Report Generator 串接
   - 自動產生每日防禦摘要
   - 產生 benchmark 結果報告
   - 統計最常見攻擊類型與最常觸發的 Skill

6. Session-level analysis
   - 偵測多輪 probing
   - 分析 session risk trend
   - 計算連續攻擊行為

7. 更嚴格的 redaction policy
   - 支援自訂 protected assets 遮罩
   - 支援 encoded secret 遮罩
   - 支援 partial fragment 遮罩

---

## 11. 目前狀態

| 項目 | 狀態 |
|---|---|
| GuardEvent schema | 已完成 |
| JSONL writer | 已完成 |
| Event logger facade | 已完成 |
| Sensitive redactor | 已完成 |
| Event query | 已完成 |
| Event summary | 已完成 |
| Unit tests | 已完成 |
| 測試結果 | 44 passed |

---

## 12. 專案價值

Event Logger 是 SecretGuard 防禦閉環中的最後一環。

它讓系統不只是在當下阻擋攻擊，也能累積事件資料，用於：

- 防禦效果驗證
- 攻擊趨勢分析
- 報告產生
- 規則調整
- Defensive Skill 優化
- 多輪攻擊研究

透過標準化事件紀錄與敏感資訊遮罩，SecretGuard 可以在保護機密的同時，保留足夠的安全分析資料。
