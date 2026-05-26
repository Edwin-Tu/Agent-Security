# SecretGuard — Project Report

> Runtime Token Interruption Guard for Local LLMs
> 本地大型語言模型即時限制 Token 防護系統

---

## 一、專案目標

在 Ollama 本地 LLM 外層建立 Runtime Guardrail，核心機制是**在模型生成過程中即時監控串流輸出 Token**，一旦命中限制 Token 立即中斷生成，而非等完整輸出後才過濾。

---

## 二、專案架構

```
SecretGuard/
├── main.py                          # Mock 整合測試入口
├── config.py                        # [STUB] 系統設定
│
├── parser/
│   ├── __init__.py
│   └── command_parser.py            # 解析 [限制token: ...] 語法
│
├── expansion/
│   ├── __init__.py
│   ├── token_expander.py            # Token 擴展引擎 (token_rules.json)
│   ├── token_risk_classifier.py     # 風險等級分類器 (high/medium/low)
│   ├── risk_map_writer.py           # 風險地圖 JSON 讀寫 + Pending 審核
│   └── ai_token_expander.py         # AI 語意分析 → 自動收錄新 Token
│
├── guards/
│   ├── __init__.py
│   ├── restricted_token_guard.py    # 限制 Token 字串比對防護器
│   ├── risk_level_guard.py          # 風險等級閾值防護器
│   ├── input_guard.py               # [STUB] 輸入層護欄
│   ├── output_guard.py              # [STUB] 輸出層護欄
│   └── authorization_guard.py       # [STUB] 授權護欄
│
├── runtime/
│   ├── __init__.py
│   ├── ollama_client.py             # Ollama HTTP API 客戶端
│   ├── stream_monitor.py            # 串流輸出即時監控器
│   └── interruption_handler.py      # [STUB] 生成中斷處理
│
├── prompts/
│   ├── __init__.py
│   └── guard_prompt.py              # AI Token 分析 System Prompt 模板
│
├── skills/
│   ├── __init__.py
│   └── secret_guard_skill.py        # [STUB] Agent Skill 介面
│
├── policies/
│   ├── token_rules.json             # 10 分類、46 條擴展規則
│   ├── token_risk_map.json          # 40 筆 Token → 風險等級對照
│   ├── pending_token_risk_map.json  # [STUB] 待審核風險地圖
│   └── secret_policy.json           # [STUB] 機密政策定義
│
├── logs/
│   └── guard_events.jsonl           # [STUB] 事件日誌
│
└── README.md                        # 專案說明文件
```

---

## 三、完成階段

### ✅ Phase 1 — 核心防護邏輯 (已實作)

| 元件 | 狀態 | 說明 |
|------|------|------|
| `command_parser.py` | ✅ 完成 | 支援中英文 `[限制token: ...]` / `[restricted_token: ...]`，回傳 normalized tokens + raw_tokens |
| `token_expander.py` | ✅ 完成 | 載入 `token_rules.json`，將分類擴展為相關詞集合 |
| `restricted_token_guard.py` | ✅ 完成 | 不區分大小寫子字串比對，支援 streaming detection |
| `stream_monitor.py` | ✅ 完成 | 逐 chunk 累積 buffer 即時檢測，命中即中斷 |
| `risk_level_guard.py` | ✅ 完成 | 比對 `token_risk_map.json`，max_level ≥ threshold 則攔截 |
| `token_risk_classifier.py` | ✅ 完成 | 內建 10 分類三級風險對照表 (高:4, 中:2, 低:4) |
| `risk_map_writer.py` | ✅ 完成 | 正式 + Pending 雙層 JSON 讀寫，支援 `approve_pending()` |
| `main.py` | ✅ 完成 | Mock 測試入口，展示完整管線 |

### 🔄 Phase 1.5 — AI 輔助擴展 (已實作)

| 元件 | 狀態 | 說明 |
|------|------|------|
| `ollama_client.py` | ✅ 完成 | 支援 `generate()` + `generate_json()` (自動清理 Markdown)，無連線時安全降級 |
| `guard_prompt.py` | ✅ 完成 | System Prompt 定義 AI 為 Token 風險分析引擎，要求回傳結構化 JSON |
| `ai_token_expander.py` | ✅ 完成 | 未知 Token 送 Ollama 語意分析 + 自動收錄到 `token_rules.json` / `token_risk_map.json` |

### ⬜ Phase 2 — 進階防護 (未開始)

| 元件 | 狀態 | 說明 |
|------|------|------|
| `input_guard.py` | ⬜ STUB | 輸入端過濾/驗證 |
| `output_guard.py` | ⬜ STUB | 輸出端後處理 |
| `authorization_guard.py` | ⬜ STUB | 授權與權限控管 |
| `interruption_handler.py` | ⬜ STUB | 實際中斷 Ollama 串流連線 |
| `secret_guard_skill.py` | ⬜ STUB | Agent 框架整合層 |

### ⬜ Phase 3 — 基礎建設 (未開始)

| 元件 | 狀態 | 說明 |
|------|------|------|
| `config.py` | ⬜ STUB | 集中設定管理 |
| `guard_events.jsonl` | ⬜ STUB | 事件日誌寫入 |
| `secret_policy.json` | ⬜ STUB | 政策定義 |
| `pending_token_risk_map.json` | ⬜ STUB | 待審核風險項目容器 |

---

## 四、功能說明

### 4.1 核心資料流

```
使用者輸入 [限制token: xxx] [限制token: yyy] ...
  ↓ command_parser.py
      取出 token 清單 + 清理後的使用者問題（不含指令區塊）
  ↓ load_known_categories()
      比對 token_rules.json 的已知分類
      已知 → 直接擴展（跳過 AI）
      未知 → 送 Ollama AI 分析 → 自動收錄到 policies → 加入防護
  ↓ RestrictedTokenGuard
      將 tokens 擴展成完整的 restricted_set
  ↓ 模型輸出（目前為 Mock）
      檢測是否命中 restricted_set 中的任何詞
  ↓ RiskLevelGuard（僅在有命中時）
      查 token_risk_map.json 比對風險等級與閾值
  ↓ 最終輸出
      安全拒答 / 正常輸出
```

### 4.2 AI Token 擴展流程

```
使用者輸入含有未知 Token（如「身分證號碼:A123456789」）
  ↓ parser 不阻擋任何格式
  ↓ 查 token_rules.json 無此分類
  ↓ AITokenExpander.analyze_and_learn()
    → ollama_client.generate_json(SYSTEM_PROMPT + raw_token)
    → AI 回傳 JSON:
      {
        "category": "身分證號碼",
        "risk_level": "high",
        "expanded_tokens": ["身分證字號", "id_number", ...],
        "specific_values": ["a123456789"],
        "related_categories": ["credential", "private_info"]
      }
    → 自動寫入 token_rules.json（新分類 + 擴展詞）
    → 自動寫入 token_risk_map.json（所有詞彙的風險等級）
  ↓ category 加入 valid_tokens，specific_values 直接加入 restricted_set
  ↓ 後續流程與已知 token 相同
```

### 4.3 Token 風險分級

| 等級 | 包含分類 | 說明 |
|------|----------|------|
| **high** | password, api_key, private_key, credential | 直接憑證/金鑰，可用於身分冒充 |
| **medium** | token, secret | 存取權杖，可間接取得系統權限 |
| **low** | database, config, internal_rule, system_prompt | 配置類資訊 |

### 4.4 串流監控

```
StreamMonitor:
  模型 chunk 輸出
  ↓ 累積到 buffer
  ↓ 每次新 chunk 都檢測完整 buffer
  ↓ 命中 → 中斷 → 回傳安全拒答
  ↓ 無命中 → 繼續累積
```

---

## 五、代辦事項

### P0 — 核心缺口

- [ ] **`interruption_handler.py`**: 實作實際中斷 Ollama streaming request 的邏輯（如中斷 HTTP 連線、關閉 SSE）
- [ ] **`ollama_client.py`**: 補上 streaming generate 支援 (`generate_stream()`)，回傳 Generator 供 `StreamMonitor` 使用
- [ ] **整合測試**: 將 `StreamMonitor` + `OllamaClient` + `InterruptionHandler` 串接，實現真正的端到端防護

### P1 — 防護強化

- [ ] **`input_guard.py`**: 輸入端過濾，防止 prompt injection 繞過 guard
- [ ] **`output_guard.py`**: 輸出端後處理，作為最後一道防線
- [ ] **`authorization_guard.py`**: 角色/權限控管，不同使用者有不同限制等級

### P2 — 基礎建設

- [ ] **`config.py`**: Ollama endpoint、模型名稱、預設 threshold、log 設定
- [ ] **`guard_events.jsonl`**: 串接 logging，記錄每次檢測結果（時間、token、blocked 與否）
- [ ] **`secret_guard_skill.py`**: Agent 框架整合（LangChain / CrewAI tool）

### P3 — 進階功能

- [ ] Embedding Similarity Detection（語意相似度偵測）
- [ ] Token-level Logits Intervention（解碼層直接干預）
- [ ] Multi-model Runtime Guard（多模型同時防護）
- [ ] Dynamic Generation Control（動態調整生成策略）

---

## 六、技術規格

| 項目 | 內容 |
|------|------|
| Python 版本 | 3.10+ |
| 外部依賴 | `requests`（Ollama API） |
| LLM 平台 | Ollama（預設 `http://localhost:11434`） |
| 預設模型 | llama3 |
| 偵測方式 | 大小寫不敏感子字串比對 |
| 擴展機制 | `token_rules.json` 分類 → 擴展詞清單 |
| AI 輔助 | Ollama API → 結構化 JSON 解析 → 自動收錄 |
| 風險閾值 | 預設 `medium`，可動態調整 |
| 日誌儲存 | JSONL 格式（待實作寫入） |

---

## 七、執行方式

```bash
cd SecretGuard

# 互動模式
python3 main.py

# 執行元件自我測試
python3 -m parser.command_parser
python3 -m guards.restricted_token_guard
python3 -m runtime.stream_monitor

# 整合驗證
python3 -c "
from expansion.token_expander import TokenExpander
from expansion.token_risk_classifier import TokenRiskClassifier
from expansion.risk_map_writer import RiskMapWriter
from guards.restricted_token_guard import RestrictedTokenGuard
from guards.risk_level_guard import RiskLevelGuard
# 全元件匯入測試
print('All imports OK')
"
```

---

*Generated: 2026-05-26*
