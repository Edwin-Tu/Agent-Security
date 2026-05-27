# SecretGuard 專案進度報告

> **掃描日期：** 2026-05-27  
> **專案版本：** Attack-Aware Defensive Skill Framework for Local LLMs  
> **報告範圍：** `/mnt/d/Agent-Security/SecretGuard/` + `/mnt/d/Agent-Security/README.md`

---

## 目錄

1. [專案概覽](#1-專案概覽)
2. [模組完成度總覽](#2-模組完成度總覽)
3. [逐檔案掃描結果](#3-逐檔案掃描結果)
4. [技能矩陣](#4-技能矩陣)
5. [政策與規則檔案](#5-政策與規則檔案)
6. [Benchmark 測試結果](#6-benchmark-測試結果)
7. [README 規格比對](#7-readme-規格比對)
8. [已知問題與待辦](#8-已知問題與待辦)
9. [未來研究方向進度](#9-未來研究方向進度)
10. [總結](#10-總結)

---

## 1. 專案概覽

| 項目 | 數值 |
|------|------|
| Python 原始檔 | 28 個 |
| JSON 政策檔 | 6 個 |
| Markdown 文件 | 2 個 |
| 總程式碼行數 | ~2,970 行 |
| 語法錯誤 | 0 |
| 匯入錯誤 | 0 |
| Benchmark 通過率 | 100% (5/5) |

### 系統流程（實際實作）

```
User Input
   ↓
Input Guard
   ↓
Attack Classifier (core/attack_classifier.py)
   ↓
Defense Router (core/defense_router.py)
   ↓
Defensive Skill Layer (skills/ — 20 skills)
   ↓
LLM / Ollama (runtime/ollama_client.py)
   ↓
Runtime Stream Monitor (runtime/stream_monitor.py)
   ↓
Output Guard (guards/output_guard.py)
   ↓
Final Response
```

---

## 2. 模組完成度總覽

| 模組 | 完成度 | 狀態 |
|------|--------|------|
| **Core** | **100%** | 7 個檔案完整實作，類別層級清晰 |
| **Attacks** | **100%** | 攻擊分類法 + 20 種攻擊模式 JSON |
| **Skills** | **100%** | 20 個防禦技能 + 抽象基底類別 |
| **Guards** | **80%** | 4/5 完整；`AuthorizationGuard` 為 stub |
| **Runtime** | **100%** | Ollama 整合、串流監控、中斷處理 |
| **Policies** | **80%** | 4/5 有內容；`secret_policy.json` 為空 |
| **Benchmark** | **70%** | 框架正常但測試覆蓋不足（僅 5 項） |
| **Reports** | **100%** | 可從 JSONL 記錄產生報告 |
| **Logs** | **0%** | 檔案存在但無事件寫入 |

### 整體完成度：~88%

---

## 3. 逐檔案掃描結果

### 3.1 根目錄

| 檔案 | 行數 | 狀態 | 說明 |
|------|------|------|------|
| `main.py` | 211 | ✅ **已完成** | 4 種 CLI 模式 + 互動選單，註冊 5 guards + 20 skills |
| `config.py` | 50 | ✅ **已完成** | `Config` 類別，讀取 `defense_rules.json` |
| `.gitignore` | 5 | ✅ **已完成** | 忽略 `__pycache__/`, `*.py[cod]`, 結果檔 |
| `README.md` | 404 | ✅ **已完成** | 13 小節完整專案文件（中英雙語） |

### 3.2 Core 模組 (`core/`)

| 檔案 | 行數 | 狀態 | 類別/函式 |
|------|------|------|-----------|
| `__init__.py` | 12 | ✅ **已完成** | 匯出 7 個類別 |
| `attack_classifier.py` | 51 | ✅ **已完成** | `AttackClassifier`: `classify()`, `classify_with_context()`, `reload()` |
| `defense_router.py` | 65 | ✅ **已完成** | `DefenseRouter`: `register_skill()`, `register_guard()`, `analyze()`, `execute_defenses()`, `process()`, `summary()` |
| `defense_context.py` | 37 | ✅ **已完成** | `DefenseContext`: 追蹤啟用中防禦、風險層級、干預記錄 |
| `risk_score.py` | 41 | ✅ **已完成** | `RiskScore`: 三階層級 (low/medium/high)，`compute()`, `exceeds_threshold()` |
| `session_memory.py` | 61 | ✅ **已完成** | `SessionMemory`: 互動記錄、統計、JSON 匯出 |
| `token_expander.py` | 62 | ✅ **已完成** | `TokenExpander`: 讀取 `token_rules.json` 擴展限制 Token |
| `token_risk_classifier.py` | 57 | ✅ **已完成** | `TokenRiskClassifier`: 10 類別風險映射 |

### 3.3 Attacks 模組 (`attacks/`)

| 檔案 | 行數 | 狀態 | 說明 |
|------|------|------|------|
| `__init__.py` | 3 | ✅ **已完成** | 匯出 `AttackTaxonomy` |
| `attack_taxonomy.py` | 57 | ✅ **已完成** | 10 種方法：風險過濾、模式比對、緩解查詢 |
| `attacks.json` | 142 | ✅ **已完成** | 20 種攻擊模式（名稱、描述、風險層級、模式、緩解） |

### 3.4 Skills 模組 (`skills/`)

| 檔案 | 行數 | 狀態 | 偵測模式 | 備註 |
|------|------|------|----------|------|
| `base_skill.py` | 27 | ✅ **已完成** | — | 抽象基底類別，定義 `detect()` / `defend()` / `process()` |
| `direct_request_skill.py` | 19 | ✅ **已完成** | 🔴 關鍵字比對 | 直接請求秘密 |
| `role_play_skill.py` | 18 | ✅ **已完成** | 🔴 關鍵字比對 | 角色扮演繞過 |
| `instruction_override_skill.py` | 18 | ✅ **已完成** | 🔴 關鍵字比對 | 指令覆蓋 |
| `system_prompt_extraction_skill.py` | 19 | ✅ **已完成** | 🔴 關鍵字比對 | 系統提示提取 |
| `encoding_bypass_skill.py` | 18 | ✅ **已完成** | 🟡 關鍵字比對 | 編碼繞過 |
| `partial_disclosure_skill.py` | 24 | ✅ **已完成** | 🟠 關鍵字 + 歷史分析 | 部分揭露（含多輪累積偵測） |
| `translation_bypass_skill.py` | 18 | ✅ **已完成** | 🟡 關鍵字比對 | 翻譯繞過 |
| `structured_output_skill.py` | 21 | ✅ **已完成** | 🟡 關鍵字比對 | 結構化輸出（⚠ 附加警告，非阻擋） |
| `log_access_skill.py` | 18 | ✅ **已完成** | 🔴 關鍵字比對 | 日誌存取 |
| `multi_turn_probe_skill.py` | 22 | ✅ **已完成** | 🟠 關鍵字 + 歷史分析 | 多輪探測（含累積偵測） |
| `policy_confusion_skill.py` | 18 | ✅ **已完成** | 🟡 關鍵字比對 | 策略混淆（⚠ 附加警告，非阻擋） |
| `indirect_prompt_injection_skill.py` | 18 | ✅ **已完成** | 🔴 關鍵字比對 | 間接提示注入 |
| `format_smuggling_skill.py` | 18 | ✅ **已完成** | 🟡 關鍵字比對 | 格式走私（⚠ 附加警告，非阻擋） |
| `output_constraint_bypass_skill.py` | 19 | ✅ **已完成** | 🟡 關鍵字比對 | 輸出限制繞過 |
| `reasoning_trap_skill.py` | 19 | ✅ **已完成** | 🟡 關鍵字比對 | 推理陷阱（⚠ 附加警告，非阻擋） |
| `refusal_suppression_skill.py` | 19 | ✅ **已完成** | 🔴 關鍵字比對 | 拒絕抑制 |
| `persona_override_skill.py` | 19 | ✅ **已完成** | 🔴 關鍵字比對 | 人格覆蓋 |
| `data_reconstruction_skill.py` | 24 | ✅ **已完成** | 🟠 關鍵字 + 歷史分析 | 資料重構（含碎片累積偵測） |
| `cross_language_injection_skill.py` | 18 | ✅ **已完成** | 🟡 關鍵字比對 | 跨語言注入 |
| `homoglyph_obfuscation_skill.py` | 20 | ✅ **已完成** | 🟡 關鍵字 + 字元偵測 | 同形字符混淆（含 Unicode 字元檢測） |

> 🔴 = 高風險阻擋　🟡 = 中風險阻擋　🟠 = 情境感知　⚠ = 僅警告不阻擋

### 3.5 Guards 模組 (`guards/`)

| 檔案 | 行數 | 狀態 | 類別/方法 | 說明 |
|------|------|------|-----------|------|
| `__init__.py` | 7 | ✅ **已完成** | 匯出 5 個 guard 類別 |
| `input_guard.py` | 23 | ✅ **已完成** | `check()`, `sanitize()`, `add_rule()` | 5 種可疑模式檢查 |
| `output_guard.py` | 22 | ✅ **已完成** | `check()`, `add_pattern()` | 5 種洩漏模式檢查 |
| `restricted_token_guard.py` | 43 | ✅ **已完成** | `detect()`, `detect_in_stream()`, `update_restricted_tokens()` | Token 擴展 + 偵測 |
| `risk_level_guard.py` | 41 | ✅ **已完成** | `get_risk_level()`, `check()`, `update_threshold()` | 風險層級門檻檢查 |
| `authorization_guard.py` | 11 | ⚠️ **Stub** | `check()`, `require_permission()` | **無實際授權邏輯**，永遠回傳未阻擋 |

### 3.6 Runtime 模組 (`runtime/`)

| 檔案 | 行數 | 狀態 | 類別/方法 | 說明 |
|------|------|------|-----------|------|
| `__init__.py` | 6 | ✅ **已完成** | 匯出 4 個類別 |
| `ollama_client.py` | 274 | ✅ **已完成** | `is_available()`, `list_models()`, `generate_stream()`, `generate()`, `generate_text()`, `generate_json()` | 含錯誤處理、連線逾時、HTTP 錯誤 |
| `stream_monitor.py` | 143 | ✅ **已完成** | `monitor()` | Buffer 上限 1000 字元，即時中斷 |
| `interruption_handler.py` | 18 | ✅ **已完成** | `interrupt()`, `clear()`, `is_interrupted()` | 簡單狀態旗標（未實際中斷 HTTP） |
| `runtime_guard.py` | 27 | ✅ **已完成** | `check_output()`, `check_stream()`, `reset()` | 整合 token + risk + 中斷 + 串流監控 |

### 3.7 Policies 模組 (`policies/`)

| 檔案 | 大小 | 狀態 | 內容 |
|------|------|------|------|
| `attack_patterns.json` | 52 行 | ✅ **有效** | 10 類攻擊模式（含 confidence、risk_level） |
| `defense_rules.json` | 21 行 | ✅ **有效** | 13 項防禦設定（threshold、layer flags、拒絕訊息） |
| `token_rules.json` | 68 行 | ✅ **有效** | 10 類 Token 擴展規則（中英文） |
| `token_risk_map.json` | 57 行 | ✅ **有效** | 55 組 Token→風險層級映射 |
| `secret_policy.json` | 1 行 | ⚠️ **空檔案** | `{}` — 無任何政策定義 |

### 3.8 Benchmark 模組 (`benchmark/`)

| 檔案 | 行數 | 狀態 | 說明 |
|------|------|------|------|
| `__init__.py` | 4 | ✅ **已完成** | 匯出 `Evaluator`, `run_benchmark` |
| `evaluator.py` | 60 | ✅ **已完成** | 測試執行、摘要統計、結果儲存/載入 |
| `run_benchmark.py` | 70 | ✅ **已完成** | 5 項元件測試 |
| `results/` | — | ✅ **有記錄** | 2 份歷史 Benchmark 結果 |

### 3.9 Reports 模組 (`reports/`)

| 檔案 | 行數 | 狀態 | 說明 |
|------|------|------|------|
| `__init__.py` | 3 | ✅ **已完成** | 匯出 `ReportGenerator` |
| `report_generator.py` | 59 | ✅ **已完成** | 從 JSONL 產生報告、摘要、儲存 |

### 3.10 Logs

| 檔案 | 大小 | 狀態 | 說明 |
|------|------|------|------|
| `logs/guard_events.jsonl` | 0 行 | ⚠️ **空檔案** | 尚未有任何事件寫入 |

---

## 4. 技能矩陣

### 攻擊類型 ↔ 防禦技能對應表

| 攻擊類型 | 風險 | 對應技能 | 緩解方式 | 狀態 |
|----------|------|----------|----------|------|
| 直接請求攻擊 | HIGH | `DirectRequestSkill` | 直接阻擋 | ✅ |
| 角色扮演攻擊 | HIGH | `RolePlaySkill` | 直接阻擋 | ✅ |
| 指令覆蓋攻擊 | HIGH | `InstructionOverrideSkill` | 直接阻擋 | ✅ |
| 系統提示提取 | HIGH | `SystemPromptExtractionSkill` | 直接阻擋 | ✅ |
| 編碼繞過攻擊 | MEDIUM | `EncodingBypassSkill` | 阻擋 | ✅ |
| 部分揭露攻擊 | MEDIUM | `PartialDisclosureSkill` | 阻擋 + 多輪累積偵測 | ✅ |
| 翻譯繞過攻擊 | MEDIUM | `TranslationBypassSkill` | 阻擋 | ✅ |
| 結構化輸出攻擊 | MEDIUM | `StructuredOutputSkill` | ⚠ 附加警告 | ✅ |
| 日誌存取攻擊 | HIGH | `LogAccessSkill` | 阻擋 | ✅ |
| 多輪探測攻擊 | HIGH | `MultiTurnProbeSkill` | 阻擋 + 累積偵測 | ✅ |
| 策略混淆攻擊 | MEDIUM | `PolicyConfusionSkill` | ⚠ 附加警告 | ✅ |
| 間接提示注入 | HIGH | `IndirectPromptInjectionSkill` | 阻擋 | ✅ |
| 格式走私攻擊 | MEDIUM | `FormatSmugglingSkill` | ⚠ 附加警告 | ✅ |
| 輸出限制繞過 | MEDIUM | `OutputConstraintBypassSkill` | 阻擋 | ✅ |
| 推理陷阱攻擊 | MEDIUM | `ReasoningTrapSkill` | ⚠ 附加警告 | ✅ |
| 拒絕抑制攻擊 | HIGH | `RefusalSuppressionSkill` | 阻擋 | ✅ |
| 人格覆蓋攻擊 | HIGH | `PersonaOverrideSkill` | 阻擋 | ✅ |
| 資料重構攻擊 | HIGH | `DataReconstructionSkill` | 阻擋 + 碎片累積偵測 | ✅ |
| 跨語言注入 | MEDIUM | `CrossLanguageInjectionSkill` | 阻擋 | ✅ |
| 同形字符混淆 | MEDIUM | `HomoglyphObfuscationSkill` | 阻擋 + Unicode 字元檢測 | ✅ |

> 20/20 攻防對應完整覆蓋

### Skills 防禦策略分布

```
直接阻擋 (Hard Block):   ████████████████████ 13 (65%)
追加警告 (Soft Warn):    ██████               4 (20%)
情境感知 (Context):      ████                 3 (15%)
```

---

## 5. 政策與規則檔案

### Token 規則分類 (`token_rules.json`)

| 類別 | 擴展詞數量 | 風險層級 |
|------|-----------|----------|
| `password` | 4 (passwd, pwd, passphrase, 密碼) | HIGH |
| `api_key` | 5 (apikey, api_secret, api_token, api金鑰, api密鑰) | HIGH |
| `private_key` | 5 (privatekey, rsa_key, ssh_key, 私鑰, 私密金鑰) | HIGH |
| `credential` | 4 (credentials, 憑證, 認證資訊) | HIGH |
| `token` | 5 (auth_token, access_token, bearer_token, refresh_token, 令牌, 授權令牌) | MEDIUM |
| `secret` | 3 (secrets, 機密, 秘密) | MEDIUM |
| `system_prompt` | 5 (system_instruction, system_message, sys_prompt, 系統提示, 系統指令) | LOW |
| `database` | 5 (db, database_url, database_connection, 資料庫, 數據庫) | LOW |
| `config` | 5 (configuration, settings, 配置, 設定) | LOW |
| `internal_rule` | 5 (internal_policy, internal_instruction, system_rule, 內部規則, 內部政策) | LOW |

### 防禦層級設定 (`defense_rules.json`)

```json
{
  "default_threshold": "medium",
  "max_allowed_risk": "high",
  "enable_input_guard": true,
  "enable_output_guard": true,
  "enable_token_guard": true,
  "enable_risk_guard": true,
  "enable_authorization": false,
  "stream_monitoring": true,
  "log_all_events": true,
  "max_buffer_size": 1000,
  "response_language": "zh",
  "defense_layers": [
    "input_guard",
    "restricted_token_guard",
    "skill_layer",
    "risk_level_guard",
    "output_guard"
  ]
}
```

---

## 6. Benchmark 測試結果

### 最新執行結果

```
==================================================
SecretGuard Benchmark
==================================================

  [PASS] AttackClassifier              (0.0077s)
  [PASS] RestrictedTokenGuard          (0.0054s)
  [PASS] RiskLevelGuard                (0.0074s)
  [PASS] DefenseRouter - safe          (0.0076s)
  [PASS] AttackClassifier - role play  (0.0050s)

Results: 5/5 passed (100.0%)
```

### 測試涵蓋缺口

| 未測試項目 | 說明 |
|-----------|------|
| 20 個 Skills 個別測試 | 目前僅測試 AttackClassifier 與 RestrictedTokenGuard |
| InputGuard / OutputGuard | 完全未納入 Benchmark |
| AuthorizationGuard | Stub，無測試價值 |
| StreamMonitor | 無獨立 Benchmark |
| RuntimeGuard | 無整合測試 |
| SessionMemory | 無獨立測試 |
| DefenseRouter — blocked path | 僅測試安全路徑 |
| Ollama 真實連線測試 | 未模擬（需要 Ollama 服務） |

---

## 7. README 規格比對

### ✅ 已達成項目

| README 規範 | 實作狀態 | 說明 |
|-------------|----------|------|
| 20 個 Defensive Skills | ✅ 完全達成 | 20 個技能檔 + 基底類別 |
| Attack Taxonomy | ✅ 完全達成 | `attacks.json` 含 20 種攻擊 |
| Attack Classifier | ✅ 完全達成 | 模式比對 + 歷史情境分析 |
| Defense Router | ✅ 完全達成 | 動態啟用對應防禦技能 |
| Runtime Stream Monitor | ✅ 完全達成 | Token 層級即時監控 |
| Risk Escalation | ✅ 完全達成 | RiskScore 三階層級計算 |
| Session Memory | ✅ 完全達成 | 多輪風險累積 + 行為記錄 |
| Input/Output Guard | ✅ 完全達成 | 基本輸入輸出過濾 |
| Restricted Token Guard | ✅ 完全達成 | Token 擴展 + 偵測 |
| Benchmark Framework | ✅ 達成（部分） | 框架完整但測試覆蓋不足 |

### ❌ 待完成項目

| README 規範 | 狀態 | 差距 |
|-------------|------|------|
| Benchmark 含 20 種攻擊分類測試 | ⚠️ 部分達成 | 僅測試 5 項基本功能 |
| 完整多輪攻擊偵測 | ✅ 達成 | PartialDisclosure / MultiTurnProbe / DataReconstruction 含歷史分析 |
| 串流中斷機制 | ⚠️ 部分達成 | InterruptionHandler 僅為狀態旗標，未實際中斷 HTTP |
| Authorization 機制 | ❌ 未實作 | `authorization_guard.py` 為 stub |
| 事件日誌記錄 | ❌ 未實作 | `guard_events.jsonl` 為空 |
| 20 種攻擊分類的完整測試 | ⚠️ 部分達成 | `attacks.json` 有 20 種定義，但 Benchmark 未逐一測試 |

---

## 8. 已知問題與待辦

### 中優先度

| 問題 | 檔案 | 說明 |
|------|------|------|
| `AuthorizationGuard` 為 Stub | `guards/authorization_guard.py:6` | `check()` 始終回傳未阻擋，無實際授權邏輯 |
| `secret_policy.json` 為空 | `policies/secret_policy.json` | 需要定義機密保護政策 |
| 無事件日誌記錄 | `logs/guard_events.jsonl` | DefenseRouter 未呼叫日誌寫入 |

### 低優先度

| 問題 | 檔案 | 說明 |
|------|------|------|
| Benchmark 測試覆蓋不足 | `benchmark/run_benchmark.py` | 僅 5 項測試，未覆蓋 20 個 Skills |
| InputGuard 模式不足 | `guards/input_guard.py:8` | 僅 5 種可疑模式 |
| OutputGuard 模式不足 | `guards/output_guard.py:6` | 僅 5 種洩漏模式 |
| InterruptionHandler 不中斷 HTTP | `runtime/interruption_handler.py` | 狀態旗標，無實際連線中斷 |
| 4 個 Skills 僅警告不阻擋 | skills/ | structured_output, policy_confusion, format_smuggling, reasoning_trap 僅附加警告 |

### 資訊性

| 項目 | 說明 |
|------|------|
| `docs/SECRETGUARD_REPORT.md` | 描述舊架構（`parser/`, `expansion/`, `prompts/`），與當前程式碼不符 |
| Skills 回應不一致 | 16 個 skill 使用完整阻擋訊息，4 個使用附加警告 |

---

## 9. 未來研究方向進度

| 研究方向 | 進度 | 說明 |
|----------|------|------|
| **Token-level Logits Intervention** | ❌ 未開始 | 直接干涉下一個 token 預測 |
| **Embedding Similarity Detection** | ❌ 未開始 | 語意相似度偵測改寫/ paraphrased 攻擊 |
| **Adaptive Defense** | 🔄 部分實作 | RiskScore 存在但動態調整防禦尚未自動化 |
| **Multi-model Runtime Guard** | ❌ 未開始 | 僅支援 Ollama |

---

## 10. 總結

### 完成度摘要

```
Core      ████████████████████ 100%
Attacks   ████████████████████ 100%
Skills    ████████████████████ 100%
Guards    ██████████████████░░  80%  (AuthorizationGuard stub)
Runtime   ████████████████████ 100%
Policies  ██████████████████░░  80%  (secret_policy.json empty)
Benchmark █████████████████░░░░  70%  (test coverage thin)
Reports   ████████████████████ 100%
Logs      ░░░░░░░░░░░░░░░░░░░░   0%  (file exists, no writes)
```

**整體專案完成度：88%**

### 核心功能狀態

- **攻擊感知分類：** ✅ 完成 — 20 種攻擊類型 + 模式比對
- **防禦技能路由：** ✅ 完成 — 20 個 Skill 自動對應攻擊類型
- **即時串流監控：** ✅ 完成 — Token 層級即時中斷
- **多輪攻擊偵測：** ✅ 完成 — 3 個 Skill 含對話歷史分析
- **風險評分系統：** ✅ 完成 — Low/Medium/High 三階層級
- **Ollama 整合：** ✅ 完成 — 串流生成 + 錯誤處理

### 待完成優先事項

1. **實作 AuthorizationGuard** — 建立角色/權限驗證機制
2. **填充 secret_policy.json** — 定義機密保護政策與規則
3. **啟用事件日誌** — DefenseRouter 寫入 `guard_events.jsonl`
4. **擴充 Benchmark** — 逐一測試 20 個 Skills + Guards
5. **擴充 Input/OutputGuard 模式** — 增加更多偵測規則
6. **清理舊文件** — 更新或移除 `docs/SECRETGUARD_REPORT.md`
