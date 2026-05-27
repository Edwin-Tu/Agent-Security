# SecretGuard 專案完整說明書

> **文件日期：** 2026-05-27  
> **專案版本：** Attack-Aware Defensive Skill Framework for Local LLMs  
> **運行環境：** Python 3.10+ / Ollama (Local LLM)

---

## 目錄

1. [專案概覽](#1-專案概覽)
2. [系統架構](#2-系統架構)
3. [系統流程](#3-系統流程)
4. [資料目錄](#4-資料目錄)
5. [模組說明](#5-模組說明)
    - 5.1 [Core 核心模組](#51-core-核心模組)
    - 5.2 [Attacks 攻擊分類模組](#52-attacks-攻擊分類模組)
    - 5.3 [Skills 防禦技能模組](#53-skills-防禦技能模組)
    - 5.4 [Guards 防護器模組](#54-guards-防護器模組)
    - 5.5 [Runtime 執行時期模組](#55-runtime-執行時期模組)
    - 5.6 [Policies 政策規則模組](#56-policies-政策規則模組)
    - 5.7 [Benchmark 測試模組](#57-benchmark-測試模組)
    - 5.8 [Reports 報告模組](#58-reports-報告模組)
    - 5.9 [Logs 日誌模組](#59-logs-日誌模組)
6. [執行模式](#6-執行模式)
7. [20 種攻擊 vs 防禦技能對應表](#7-20-種攻擊-vs-防禦技能對應表)
8. [實作狀態矩陣](#8-實作狀態矩陣)
9. [Benchmark 測試結果](#9-benchmark-測試結果)
10. [未來研究方向](#10-未來研究方向)
11. [已知問題](#11-已知問題)

---

## 1. 專案概覽

SecretGuard 是一套針對**本地大型語言模型（Local LLM）**設計的攻擊感知、技能化、即時防禦框架。

### 核心概念

> 不再只是「阻擋敏感 token」，而是「理解攻擊意圖並動態啟用對應防禦技能」。

### 研究目標

- 建立 Prompt Injection 攻擊分類系統（20 種）
- 設計 20 種對應的 Defensive Skills
- 提供本地 LLM（Ollama）即時防護能力
- 防止機密資訊洩漏
- 阻擋多輪誘導與繞過攻擊
- 建立可擴充的 AI Security Framework

### 專案數據

| 項目 | 數值 |
|------|------|
| Python 原始檔 | 57 個 |
| JSON 政策檔 | 5 個 |
| 總程式碼行數 | ~3,100 行 |
| 攻擊分類 | 20 種 |
| 防禦技能 | 20 個 |
| Benchmark 通過率 | 100% (3/3) |

---

## 2. 系統架構

```
Agent-Security/
├── main.py                          # 入口：Ollama / Analyze / List / Benchmark
├── config.py                        # 設定載入（defense_rules.json）
│
├── attacks/                         # 攻擊分類
│   ├── attacks.json                 #   20 種攻擊定義
│   └── attack_taxonomy.py           #   攻擊查詢介面
│
├── core/                            # 核心邏輯
│   ├── attack_classifier.py         #   攻擊分類引擎
│   ├── skill_router.py              #   技能路由（20 條規則）
│   ├── defense_context.py           #   防禦上下文
│   ├── session_memory.py            #   多輪對話記憶
│   ├── token_expander.py            #   Token 同義詞展開
│   └── token_risk_classifier.py     #   Token 風險分類
│
├── skills/                          # 防禦技能（20 個）
│   ├── base_skill.py                #   抽象基底：detect() + defend()
│   ├── direct_request_skill.py      #   直接請求攻擊
│   ├── role_play_skill.py           #   角色扮演攻擊
│   ├── instruction_override_skill.py
│   ├── system_prompt_extraction_skill.py
│   ├── encoding_bypass_skill.py
│   ├── partial_disclosure_skill.py
│   ├── translation_bypass_skill.py
│   ├── structured_output_skill.py
│   ├── log_access_skill.py
│   ├── multi_turn_probe_skill.py
│   ├── policy_confusion_skill.py
│   ├── indirect_prompt_injection_skill.py
│   ├── format_smuggling_skill.py
│   ├── output_constraint_bypass_skill.py
│   ├── reasoning_trap_skill.py
│   ├── refusal_suppression_skill.py
│   ├── persona_override_skill.py
│   ├── data_reconstruction_skill.py
│   ├── cross_language_injection_skill.py
│   └── homoglyph_obfuscation_skill.py
│
├── guards/                          # 防護器
│   ├── input_guard.py               #   輸入層過濾
│   ├── output_guard.py              #   輸出層過濾
│   ├── restricted_token_guard.py    #   限制 Token 偵測
│   └── authorization_guard.py       #   授權檢查（預留）
│
├── runtime/                         # 執行時期
│   ├── ollama_client.py             #   Ollama API 客戶端
│   ├── stream_monitor.py            #   串流監控器
│   ├── interruption_handler.py      #   中斷處理
│   └── runtime_guard.py             #   即時防護整合
│
├── policies/                        # 政策規則
│   ├── defense_rules.json           #   防禦規則設定
│   ├── attack_patterns.json         #   攻擊模式（10 類）
│   ├── token_rules.json             #   Token 同義詞規則
│   ├── token_risk_map.json          #   Token 風險對照
│   └── secret_policy.json           #   機密政策（預留）
│
├── benchmark/                       # 基準測試
│   ├── run_benchmark.py
│   ├── evaluator.py
│   └── results/
│
├── reports/
│   └── report_generator.py          # 報告產生器
│
└── logs/
    └── guard_events.jsonl           # 事件日誌
```

---

## 3. 系統流程

### 3.1 完整防禦管線

```
User Input
   ↓
[1] Input Guard
    基礎檢查：<script> / javascript: / onerror= / data: 等 XSS 向量
   ↓
[2] Attack Classifier
    比對 attack_patterns.json（10 類攻擊模式）
    產出威脅列表：category + confidence + risk_level
   ↓
[3] Skill Router
    依 category 查找 CATEGORY_SKILL_MAP（20 條路由）
    路由至對應 Defensive Skill
   ↓
[4] Defensive Skill
    執行 detect() → 判定是否命中
    命中則執行 defend() → 產出安全化 prompt
   ↓
[5] Restricted Token Guard
    比對 token_rules.json 展開後的限制 Token 集合
    阻擋 API Key / Secret / Password 等敏感詞
   ↓
[6] LLM / Ollama
    模型執行生成
   ↓
[7] Runtime Stream Monitor
    逐 chunk 即時比對限制 Token
    命中立即中斷生成（拒絕訊息取代）
   ↓
[8] Output Guard
    檢查輸出是否含 sk- / -----BEGIN / AKIA / ghp_ 等模式
   ↓
Final Response
```

### 3.2 三層防護策略

| 層級 | 階段 | 元件 | 目的 |
|------|------|------|------|
| 輸入層 | LLM 之前 | InputGuard + AttackClassifier + SkillRouter + TokenGuard | 阻止惡意 prompt 進入模型 |
| 執行層 | 生成期間 | StreamMonitor | 即時攔截 token 洩漏 |
| 輸出層 | 生成之後 | OutputGuard | 最終輸出安全檢查 |

---

## 4. 資料目錄

### 4.1 `attacks/attacks.json` — 攻擊分類定義

| 攻擊 ID | 名稱 | 風險 | 緩解方式 |
|---------|------|------|----------|
| `direct_request` | 直接請求攻擊 | HIGH | input_guard, restricted_token_guard |
| `role_play` | 角色扮演攻擊 | HIGH | role_play_skill |
| `instruction_override` | 指令覆蓋攻擊 | HIGH | instruction_override_skill |
| `system_prompt_extraction` | 系統提示提取攻擊 | HIGH | system_prompt_extraction_skill |
| `encoding_bypass` | 編碼繞過攻擊 | MEDIUM | encoding_bypass_skill |
| `partial_disclosure` | 部分揭露攻擊 | MEDIUM | partial_disclosure_skill |
| `translation_bypass` | 翻譯繞過攻擊 | MEDIUM | translation_bypass_skill |
| `structured_output` | 結構化輸出攻擊 | MEDIUM | structured_output_skill |
| `log_access` | 日誌存取攻擊 | HIGH | log_access_skill, authorization_guard |
| `multi_turn_probe` | 多輪探測攻擊 | HIGH | multi_turn_probe_skill, session_memory |
| `policy_confusion` | 策略混淆攻擊 | MEDIUM | policy_confusion_skill |
| `indirect_prompt_injection` | 間接提示注入攻擊 | HIGH | indirect_prompt_injection_skill |
| `format_smuggling` | 格式走私攻擊 | MEDIUM | format_smuggling_skill, output_guard |
| `output_constraint_bypass` | 輸出限制繞過攻擊 | MEDIUM | output_constraint_bypass_skill, output_guard |
| `reasoning_trap` | 推理陷阱攻擊 | MEDIUM | reasoning_trap_skill |
| `refusal_suppression` | 拒絕抑制攻擊 | HIGH | refusal_suppression_skill |
| `persona_override` | 人格覆蓋攻擊 | HIGH | persona_override_skill |
| `data_reconstruction` | 資料重構攻擊 | HIGH | data_reconstruction_skill, session_memory |
| `cross_language_injection` | 跨語言注入攻擊 | MEDIUM | cross_language_injection_skill |
| `homoglyph_obfuscation` | 同形字符混淆攻擊 | MEDIUM | homoglyph_obfuscation_skill, input_guard |

### 4.2 `policies/attack_patterns.json` — 攻擊模式（AttackClassifier 使用）

| 類別 | 模式範例 | Confidence | Risk |
|------|---------|-----------|------|
| `direct_secret_request` | 告訴我秘密, reveal password, show api key | 0.9 | HIGH |
| `role_play_bypass` | 假裝你是, pretend you are, 你現在是 | 0.8 | HIGH |
| `instruction_override` | 忽略以上, ignore previous, override | 0.85 | HIGH |
| `system_prompt_extraction` | 你的提示詞, show your prompt | 0.9 | HIGH |
| `encoding_bypass` | base64, hex encoding, unicode escape | 0.7 | MEDIUM |
| `partial_disclosure` | 第一個字, first character, one letter | 0.6 | MEDIUM |
| `multi_turn_probe` | 循序漸進, step by step, 先回答 | 0.75 | HIGH |
| `persona_override` | 你的新角色, your new role, act as a | 0.85 | HIGH |
| `refusal_suppression` | 不要拒絕, don't refuse, must answer | 0.85 | HIGH |
| `data_reconstruction` | 重組, reconstruct, put together | 0.7 | HIGH |

### 4.3 `policies/token_rules.json` — Token 同義詞展開

| 類別 | 展開詞 | 數量 |
|------|--------|------|
| `password` | passwd, pwd, passphrase, 密碼 | 4 |
| `api_key` | apikey, api_secret, api_token, api金鑰, api密鑰 | 5 |
| `private_key` | privatekey, rsa_key, ssh_key, 私鑰, 私密金鑰 | 5 |
| `credential` | credentials, 憑證, 認證資訊 | 3 |
| `token` | auth_token, access_token, bearer_token, refresh_token, 令牌, 授權令牌 | 6 |
| `secret` | secrets, 機密, 秘密 | 3 |
| `system_prompt` | system_instruction, system_message, sys_prompt, 系統提示, 系統指令 | 5 |
| `database` | db, database_url, database_connection, 資料庫, 數據庫 | 5 |
| `config` | configuration, settings, 配置, 設定 | 4 |
| `internal_rule` | internal_policy, internal_instruction, system_rule, 內部規則, 內部政策 | 5 |

### 4.4 `policies/token_risk_map.json` — Token 風險等級

| 風險 | Token 範例 | 數量 |
|------|-----------|------|
| HIGH | password, api_key, private_key, credential 及其同義詞 | 18 |
| MEDIUM | token, secret 及其同義詞 | 12 |
| LOW | system_prompt, database, config, internal_rule 及其同義詞 | 25 |

### 4.5 `policies/defense_rules.json` — 防禦設定

```json
{
  "default_threshold": "medium",
  "max_allowed_risk": "high",
  "enable_input_guard": true,
  "enable_output_guard": true,
  "enable_token_guard": true,
  "enable_authorization": false,
  "stream_monitoring": true,
  "log_all_events": true,
  "max_buffer_size": 1000,
  "response_language": "zh",
  "rejection_message": "[SecretGuard]\n此內容受到限制，未經授權無法提供。",
  "defense_layers": [
    "input_guard",
    "restricted_token_guard",
    "skill_layer",
    "output_guard"
  ]
}
```

---

## 5. 模組說明

### 5.1 Core 核心模組

| 檔案 | 行數 | 類別 | 主要方法 | 說明 |
|------|------|------|----------|------|
| `attack_classifier.py` | 51 | `AttackClassifier` | `classify()`, `classify_with_context()`, `reload()` | 比對 `attack_patterns.json` 做關鍵字分類；支援歷史情境分析避免重複通報 |
| `skill_router.py` | 75 | `SkillRouter` | `route()`, `process_threats()`, `list_routes()` | 20 條 `CATEGORY_SKILL_MAP` 路由規則；載入所有 20 個 Skill 實例並依分類路由 |
| `defense_context.py` | 37 | `DefenseContext` | `record_intervention()`, `set_threshold()`, `summary()` | 記錄所有防禦干預事件、啟用中的防禦層級、阻擋 Token 列表 |
| `session_memory.py` | 61 | `SessionMemory` | `record()`, `add_alert()`, `recent()`, `stats()` | 多輪對話歷史記錄（上限 50 筆）；阻擋率統計、JSON 匯出 |
| `token_expander.py` | 62 | `TokenExpander` | `expand()`, `normalize()` | 讀取 `token_rules.json`，將類別詞展開為同義詞集合（如 password→{passwd, pwd, 密碼}） |
| `token_risk_classifier.py` | 57 | `TokenRiskClassifier` | `classify()`, `classify_tokens()`, `exceeds_threshold()` | Token 風險等級分類（HIGH/MEDIUM/LOW）；內建 10 類風險映射表 |

### 5.2 Attacks 攻擊分類模組

| 檔案 | 行數 | 類別/內容 | 說明 |
|------|------|-----------|------|
| `attack_taxonomy.py` | 57 | `AttackTaxonomy` | 攻擊分類查詢介面：依風險過濾、模式比對、緩解查詢 |
| `attacks.json` | 142 | 20 種攻擊定義 | 含 name / description / risk_level / patterns / mitigation |

### 5.3 Skills 防禦技能模組

**基底類別：** `base_skill.py` — 定義 `detect()` 與 `defend()` 抽象方法，提供 `process()` 整合流程

| 技能 | 行數 | 風險 | 偵測方式 | 防禦行為 |
|------|------|------|----------|----------|
| `DirectRequestSkill` | 19 | HIGH | 10 組關鍵字（告訴我秘密、reveal password...） | 直接阻擋 |
| `RolePlaySkill` | 18 | HIGH | 關鍵字（假裝你是、pretend you are...） | 直接阻擋 |
| `InstructionOverrideSkill` | 18 | HIGH | 關鍵字（忽略以上、override...） | 直接阻擋 |
| `SystemPromptExtractionSkill` | 19 | HIGH | 關鍵字（你的提示詞、show your prompt...） | 直接阻擋 |
| `EncodingBypassSkill` | 18 | MEDIUM | 關鍵字（base64、hex encoding...） | 阻擋 |
| `PartialDisclosureSkill` | 24 | MEDIUM | 關鍵字 + 歷史累積分析 | 阻擋 |
| `TranslationBypassSkill` | 18 | MEDIUM | 關鍵字（翻譯成、translate...） | 阻擋 |
| `StructuredOutputSkill` | 21 | MEDIUM | 關鍵字（json格式、output as JSON...） | 附加警告 |
| `LogAccessSkill` | 18 | HIGH | 關鍵字（log、guard_events...） | 直接阻擋 |
| `MultiTurnProbeSkill` | 22 | HIGH | 關鍵字 + 歷史累積分析 | 阻擋 |
| `PolicyConfusionSkill` | 18 | MEDIUM | 關鍵字（規則是、allow me...） | 附加警告 |
| `IndirectPromptInjectionSkill` | 18 | HIGH | 關鍵字（從網頁、in the context...） | 直接阻擋 |
| `FormatSmugglingSkill` | 18 | MEDIUM | 關鍵字（markdown、html tag...） | 附加警告 |
| `OutputConstraintBypassSkill` | 19 | MEDIUM | 關鍵字（不要限制、don't filter...） | 阻擋 |
| `ReasoningTrapSkill` | 19 | MEDIUM | 關鍵字（推理、think step by step...） | 附加警告 |
| `RefusalSuppressionSkill` | 19 | HIGH | 關鍵字（不要拒絕、must answer...） | 直接阻擋 |
| `PersonaOverrideSkill` | 19 | HIGH | 關鍵字（你現在是、act as...） | 直接阻擋 |
| `DataReconstructionSkill` | 24 | HIGH | 關鍵字 + 碎片累積分析 | 阻擋 |
| `CrossLanguageInjectionSkill` | 18 | MEDIUM | 關鍵字（混合語言、code-switch...） | 阻擋 |
| `HomoglyphObfuscationSkill` | 20 | MEDIUM | 關鍵字 + Unicode 同形字元偵測 | 阻擋 |

**防禦策略分布：**
- 直接阻擋 (Hard Block)：12 個 (60%)
- 附加警告 (Soft Warn)：4 個 (20%)
- 情境感知含累積分析 (Context)：4 個 (20%)

### 5.4 Guards 防護器模組

| 檔案 | 行數 | 類別 | 方法 | 說明 |
|------|------|------|------|------|
| `input_guard.py` | 23 | `InputGuard` | `check()`, `sanitize()` | 檢查 XSS 向量：`<script>`, `javascript:`, `onerror=`, `onload=`, `data:` |
| `output_guard.py` | 22 | `OutputGuard` | `check()`, `add_pattern()` | 阻擋敏感輸出模式：`sk-`, `-----BEGIN`, `AKIA`, `ghp_`, `gho_` |
| `restricted_token_guard.py` | 43 | `RestrictedTokenGuard` | `detect()`, `detect_in_stream()`, `update_restricted_tokens()` | Token 展開後子字串比對；不區分大小寫；支援串流檢測 |
| `authorization_guard.py` | 11 | `AuthorizationGuard` | `check()`, `require_permission()` | ⚠️ 預留模組：`check()` 始終回傳未阻擋，無實際授權邏輯 |

### 5.5 Runtime 執行時期模組

| 檔案 | 行數 | 類別 | 方法 | 說明 |
|------|------|------|------|------|
| `ollama_client.py` | 274 | `OllamaClient` | `is_available()`, `list_models()`, `generate_stream()`, `generate()`, `generate_text()`, `generate_json()` | Ollama HTTP API 封裝；串流生成含 StreamMonitor 監控；非串流生成供 AI Token 擴展使用；完整錯誤處理（連線逾時、HTTP 錯誤、JSON 解碼錯誤） |
| `stream_monitor.py` | 143 | `StreamMonitor` | `monitor()` | 逐 chunk 累積 buffer（上限 1000 字元）；即時呼叫 `guard.detect_in_stream()`；命中中斷串流並回傳拒絕訊息 |
| `interruption_handler.py` | 18 | `InterruptionHandler` | `interrupt()`, `clear()`, `is_interrupted()` | ⚠️ 簡易狀態旗標：記錄中斷狀態與原因，未實際中斷 HTTP 連線 |
| `runtime_guard.py` | 23 | `RuntimeGuard` | `check_output()`, `check_stream()`, `reset()` | 整合 TokenGuard + StreamMonitor + InterruptionHandler 的 Runtime 防護入口 |

### 5.6 Policies 政策規則模組

| 檔案 | 行數 | 狀態 | 說明 |
|------|------|------|------|
| `defense_rules.json` | 21 | ✅ 有效 | 13 項防禦設定：threshold、defense_layers、rejection_message |
| `attack_patterns.json` | 52 | ✅ 有效 | 10 類攻擊模式關鍵字定義（AttackClassifier 使用） |
| `token_rules.json` | 68 | ✅ 有效 | 10 類 Token、46 條中英文同義詞擴展規則 |
| `token_risk_map.json` | 57 | ✅ 有效 | 55 組 Token → 風險等級映射 |
| `secret_policy.json` | 1 | ⚠️ 空檔案 | 預留，尚無政策定義 |

### 5.7 Benchmark 測試模組

| 檔案 | 行數 | 類別/函式 | 說明 |
|------|------|-----------|------|
| `evaluator.py` | 60 | `Evaluator` | 測試執行器：計時、結果儲存、統計摘要 |
| `run_benchmark.py` | 54 | `run_benchmark()` | 3 項核心測試（AttackClassifier × 2、RestrictedTokenGuard） |

### 5.8 Reports 報告模組

| 檔案 | 行數 | 類別 | 方法 | 說明 |
|------|------|------|------|------|
| `report_generator.py` | 59 | `ReportGenerator` | `generate_from_log()`, `generate_summary()`, `save_report()` | 從 JSONL 日誌產生事件報告；支援 Session 摘要與 JSON 匯出 |

### 5.9 Logs 日誌模組

| 檔案 | 狀態 | 說明 |
|------|------|------|
| `guard_events.jsonl` | ⚠️ 空檔案 | 檔案已建立但尚未有事件寫入；未來可擴充各 Guard / SkillRouter 寫入事件 |

---

## 6. 執行模式

### 6.1 Ollama 即時防護模式 (`--ollama`)

```
使用者輸入 → InputGuard → AttackClassifier → SkillRouter → RuntimeGuard → Ollama → OutputGuard
```

**流程細節：**
1. 檢查 Ollama 服務是否可用
2. 輸入經 InputGuard 基礎過濾
3. AttackClassifier 分類攻擊類型
4. SkillRouter 依分類啟用對應 Defensive Skill（執行 detect + defend）
5. 安全化後的 prompt 送入 Ollama
6. RuntimeGuard 監控模型輸出串流
7. OutputGuard 最終輸出檢查

### 6.2 多層分析模式 (`--analyze`)

```
使用者輸入 → AttackClassifier → SkillRouter → Guards(Input+Output+Token) → 顯示結果
```

不需 Ollama 連線，純分析文字是否含攻擊意圖。

### 6.3 列出攻擊模式 (`--list-attacks`)

顯示 `attacks/attacks.json` 中所有 20 種攻擊的風險等級、描述與緩解方式。

### 6.4 Benchmark 模式 (`--benchmark`)

執行 3 項核心元件測試：AttackClassifier（一般 + 角色扮演）、RestrictedTokenGuard。

### 6.5 CLI 參數

| 參數 | 模式 |
|------|------|
| `--ollama` | Ollama 即時防護 |
| `--analyze` | 多層分析 |
| `--list-attacks` | 列出攻擊模式 |
| `--benchmark` | 執行基準測試 |

無參數時顯示互動選單。

---

## 7. 20 種攻擊 vs 防禦技能對應表

| # | 攻擊類型 | 風險 | 對應 Skill | 防禦方式 | 狀態 |
|---|---------|------|-----------|----------|------|
| 1 | 直接請求攻擊 | HIGH | `DirectRequestSkill` | 直接阻擋 | ✅ |
| 2 | 角色扮演攻擊 | HIGH | `RolePlaySkill` | 直接阻擋 | ✅ |
| 3 | 指令覆蓋攻擊 | HIGH | `InstructionOverrideSkill` | 直接阻擋 | ✅ |
| 4 | 系統提示提取攻擊 | HIGH | `SystemPromptExtractionSkill` | 直接阻擋 | ✅ |
| 5 | 編碼繞過攻擊 | MEDIUM | `EncodingBypassSkill` | 阻擋 | ✅ |
| 6 | 部分揭露攻擊 | MEDIUM | `PartialDisclosureSkill` | 阻擋 + 多輪累積 | ✅ |
| 7 | 翻譯繞過攻擊 | MEDIUM | `TranslationBypassSkill` | 阻擋 | ✅ |
| 8 | 結構化輸出攻擊 | MEDIUM | `StructuredOutputSkill` | 附加警告 | ✅ |
| 9 | 日誌存取攻擊 | HIGH | `LogAccessSkill` | 直接阻擋 | ✅ |
| 10 | 多輪探測攻擊 | HIGH | `MultiTurnProbeSkill` | 阻擋 + 累積偵測 | ✅ |
| 11 | 策略混淆攻擊 | MEDIUM | `PolicyConfusionSkill` | 附加警告 | ✅ |
| 12 | 間接提示注入攻擊 | HIGH | `IndirectPromptInjectionSkill` | 直接阻擋 | ✅ |
| 13 | 格式走私攻擊 | MEDIUM | `FormatSmugglingSkill` | 附加警告 | ✅ |
| 14 | 輸出限制繞過攻擊 | MEDIUM | `OutputConstraintBypassSkill` | 阻擋 | ✅ |
| 15 | 推理陷阱攻擊 | MEDIUM | `ReasoningTrapSkill` | 附加警告 | ✅ |
| 16 | 拒絕抑制攻擊 | HIGH | `RefusalSuppressionSkill` | 直接阻擋 | ✅ |
| 17 | 人格覆蓋攻擊 | HIGH | `PersonaOverrideSkill` | 直接阻擋 | ✅ |
| 18 | 資料重構攻擊 | HIGH | `DataReconstructionSkill` | 阻擋 + 碎片累積 | ✅ |
| 19 | 跨語言注入攻擊 | MEDIUM | `CrossLanguageInjectionSkill` | 阻擋 | ✅ |
| 20 | 同形字符混淆攻擊 | MEDIUM | `HomoglyphObfuscationSkill` | 阻擋 + Unicode 檢測 | ✅ |

**20/20 攻防對應完全覆蓋**

### SkillRouter 路由對應表（`CATEGORY_SKILL_MAP`）

`attack_patterns.json` 的類別名稱 → 對應 Skill 名稱：

| Attack Classifier 輸出類別 | 路由至 Skill |
|--------------------------|-------------|
| `direct_secret_request` | `direct_request` |
| `role_play_bypass` | `role_play` |
| `instruction_override` | `instruction_override` |
| `system_prompt_extraction` | `system_prompt_extraction` |
| `encoding_bypass` | `encoding_bypass` |
| `partial_disclosure` | `partial_disclosure` |
| `multi_turn_probe` | `multi_turn_probe` |
| `persona_override` | `persona_override` |
| `refusal_suppression` | `refusal_suppression` |
| `data_reconstruction` | `data_reconstruction` |

（另包含 10 條來自 `attacks.json` 的擴充路由，總計 20 條）

---

## 8. 實作狀態矩陣

### 8.1 模組完成度

| 模組 | 完成度 | 說明 |
|------|--------|------|
| **Core** | **100%** | 6 個檔案完整實作，類別層級清晰 |
| **Attacks** | **100%** | 攻擊分類法 + 20 種攻擊定義 JSON + 查詢介面 |
| **Skills** | **100%** | 20 個防禦技能 + 抽象基底 + SkillRouter |
| **Guards** | **75%** | 3/4 完整；AuthorizationGuard 為 stub |
| **Runtime** | **100%** | Ollama 整合、串流監控、中斷處理 |
| **Policies** | **80%** | 4/5 有內容；secret_policy.json 為空 |
| **Benchmark** | **70%** | 框架正常但測試覆蓋僅 3 項 |
| **Reports** | **100%** | 可從 JSONL 記錄產生報告 |
| **Logs** | **0%** | 檔案存在但無事件寫入 |

### 8.2 Pipeline 串接狀態

| 管線步驟 | analyze_mode | ollama_mode | 說明 |
|---------|:-----------:|:-----------:|------|
| InputGuard | ✅ | ✅ | 兩模式皆執行 |
| AttackClassifier | ✅ | ✅ | 兩模式皆執行 |
| SkillRouter | ✅ | ✅ | 兩模式皆執行 |
| RestrictedTokenGuard | ✅ | (透過 RuntimeGuard) | analyze 直接呼叫，ollama 由 RuntimeGuard 處理 |
| OutputGuard | ✅ | ✅ | ollama 在回覆後檢查 |

### 8.3 完整度總覽

```
Core      ████████████████████ 100%
Attacks   ████████████████████ 100%
Skills    ████████████████████ 100%
Guards    █████████████████░░░  75%  (AuthorizationGuard stub)
Runtime   ████████████████████ 100%
Policies  ██████████████████░░  80%  (secret_policy.json empty)
Benchmark ████████████████░░░░  70%  (僅 3 項測試)
Reports   ████████████████████ 100%
Logs      ░░░░░░░░░░░░░░░░░░░░   0%  (無事件寫入)
```

**整體專案完成度：~85%**

---

## 9. Benchmark 測試結果

### 最新執行結果

```
==================================================
SecretGuard Benchmark
==================================================

  [PASS] AttackClassifier              (0.0054s)
  [PASS] RestrictedTokenGuard          (0.0064s)
  [PASS] AttackClassifier - role play  (0.0050s)

Results: 3/3 passed (100.0%)
```

### 測試涵蓋缺口

| 未測試項目 | 影響 | 優先度 |
|-----------|------|--------|
| 20 個 Skills 個別測試 | 中等 — Skill 邏輯單純，但無回歸保護 | MEDIUM |
| InputGuard / OutputGuard | 低 — 邏輯簡單（關鍵字比對） | LOW |
| SkillRouter 路由正確性 | 中等 — 目前僅端到端驗證，無單元測試 | MEDIUM |
| StreamMonitor | 中等 — 串流監控為關鍵功能 | HIGH |
| RuntimeGuard 整合 | 中等 — 多元件協作需驗證 | MEDIUM |
| Ollama 真實連線測試 | 低 — 需 Ollama 服務環境 | LOW |
| SessionMemory | 低 — 邏輯單純（列表操作） | LOW |

---

## 10. 未來研究方向

| 研究方向 | 進度 | 說明 |
|----------|------|------|
| **Token-level Logits Intervention** | ❌ 未開始 | 直接干涉模型的下一個 token 預測機率 |
| **Embedding Similarity Detection** | ❌ 未開始 | 使用語意相似度偵測改寫 /  paraphrased 攻擊 |
| **Adaptive Defense** | 🔄 部分實作 | DefenseContext / SessionMemory 已建立，但防禦策略未自動化調整 |
| **Multi-model Runtime Guard** | ❌ 未開始 | 目前僅支援 Ollama；未來可擴充 OpenAI-compatible API、Local Quantized Models |
| **事件日誌串接** | ❌ 未開始 | Pipeline 各階段寫入 `guard_events.jsonl` |
| **AuthorizationGuard 實作** | ❌ 未開始 | 基於角色的存取控制（Role-Based Access Control） |

---

## 11. 已知問題

### 11.1 中等優先度

| 問題 | 位置 | 說明 |
|------|------|------|
| `AuthorizationGuard` 為 Stub | `guards/authorization_guard.py:6-7` | `check()` 始終回傳 `{"blocked": false}`，無實際授權邏輯 |
| `secret_policy.json` 為空 | `policies/secret_policy.json` | 內容僅 `{}`，需定義機密保護政策 |
| `guard_events.jsonl` 無寫入 | `logs/guard_events.jsonl` | Pipeline 各階段皆未寫入事件日誌 |

### 11.2 低優先度

| 問題 | 位置 | 說明 |
|------|------|------|
| Benchmark 覆蓋不足 | `benchmark/run_benchmark.py` | 僅 3 項測試，未覆蓋 20 個 Skills、Guards、StreamMonitor |
| InputGuard 模式有限 | `guards/input_guard.py:12` | 僅 5 種 XSS 可疑模式 |
| OutputGuard 模式有限 | `guards/output_guard.py:3-5` | 僅 5 種洩漏模式 |
| InterruptionHandler 未實際中斷 HTTP | `runtime/interruption_handler.py` | 狀態旗標僅供查詢，無 `requests.Session.close()` 等連線中斷 |
| 4 個 Skills 僅附加警告 | `skills/` | `StructuredOutputSkill`、`PolicyConfusionSkill`、`FormatSmugglingSkill`、`ReasoningTrapSkill` 不阻擋只警告 |
| `docs/SECRETGUARD_REPORT.md` | 舊架構描述 | 該文件描述已不存在的 `parser/`、`expansion/`、`prompts/` 目錄 |

### 11.3 資訊性

| 項目 | 說明 |
|------|------|
| Skills 回應不一致 | 16 個 skill 使用完整阻擋訊息替代輸入，4 個僅附加警告不影響原輸入 |
| `token_risk_classifier.py` 現為獨立查詢介面 | 原供 `RiskLevelGuard` 使用，`RiskLevelGuard` 移除後保留作為 Token 風險查詢工具 |
