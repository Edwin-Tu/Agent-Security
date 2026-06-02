# SecretGuard

## Attack-Aware Defensive Skill Framework for Local LLMs

> 本地大型語言模型攻擊感知防禦技能框架  
> Local LLM Runtime Defense Framework with Attack-aware Defensive Skills

---

# 一、專案簡介

SecretGuard 是一套針對本地大型語言模型（Local LLM）設計的攻擊感知防禦框架。

核心概念不只是「阻擋敏感 token」，而是：

> 讓使用者定義自己的受保護資產，系統再根據攻擊類型、風險分數與防護政策，動態掛載 Defensive Skills，防止模型在輸入、生成中與輸出後洩漏敏感資訊。

---

# 二、核心問題

單純依靠系統內建關鍵字並不足夠，因為每個使用者要保護的內容不同：

- 比賽環境 → 保護 `flag`
- 公司環境 → 保護客戶資料、報價、內部專案代號
- 學校環境 → 保護學生資料、成績、內部文件
- 開發環境 → 保護 API Key、Token、Private Key、系統提示詞

SecretGuard 透過 **Protected Asset Registry（受保護資產登錄表）** 讓使用者定義「什麼東西需要被防護」。

---

# 三、研究目標

- 建立 Prompt Injection 攻擊分類系統
- 設計 20 種對應 Defensive Skills
- 支援使用者自訂受保護資產
- 根據資產、攻擊類型與風險分數進行防禦決策
- 提供本地 LLM 即時防護能力
- 防止完整洩漏、部分洩漏、編碼洩漏、翻譯洩漏與重構洩漏
- 建立可擴充的 AI Security Framework

---

# 四、核心概念

```text
User Defined Protected Assets
    ↓
Attack Classification
    ↓
Risk Scoring
    ↓
Defense Policy Decision
    ↓
Defensive Skill Mounting
    ↓
Protected Prompt Building
    ↓
Runtime Monitoring
    ↓
Leakage Verification
    ↓
Safe Response
```

---

# 五、系統架構（流程節點式）

```text
Agent-Security/
│
├── entry/                    # Stage 00: 系統入口與啟動流程
│   └── main.py               # CLI 入口（Ollama / Analyze / List / Benchmark）
│
├── asset_registry/           # Stage 01: 受保護資產管理
│   ├── protected_asset_registry.py  # 資產登錄與查詢
│   ├── secret_matcher.py            # 機密值比對（完整/部分/編碼/別名）
│   └── asset_loader.py              # JSON 資產載入與驗證
│
├── input_normalization/      # Stage 02: 輸入正規化
│   ├── token_expander.py           # Token 同義詞擴展
│   ├── token_risk_classifier.py    # Token 風險等級分類
│   ├── unicode_normalizer.py       # Unicode 正規化（NFKC/全半形）
│   └── homoglyph_normalizer.py     # 同形字符偵測與正規化
│
├── input_guard/              # Stage 03: 輸入層防護
│   ├── input_guard.py              # XSS/可疑格式檢查
│   ├── authorization_guard.py      # 角色與授權檢查
│   └── defense_context.py          # 防禦上下文記錄
│
├── attack_classifier/        # Stage 04: 攻擊分類
│   ├── attack_classifier.py        # 攻擊分類引擎
│   ├── attack_taxonomy.py          # 攻擊分類查詢介面
│   ├── attacks.json                # 20 種攻擊分類定義
│   └── attack_patterns.json        # 攻擊模式比對規則
│
├── risk_scoring/             # Stage 05: 風險計算
│   ├── risk_scoring_engine.py      # 單輪/多輪風險分數計算
│   ├── session_memory.py           # 多輪對話記憶與統計
│   └── token_risk_map.json         # Token 風險等級對照表
│
├── policy_engine/            # Stage 06: 防禦策略決策
│   ├── defense_policy_engine.py    # 決定 allow/warn/restrict/block/escalate
│   └── policy_builder.py           # 整合資產、角色與防禦策略
│
├── skill_router/             # Stage 07: 技能路由
│   └── skill_router.py             # category → Defensive Skill 路由
│
├── defensive_skills/         # Stage 08: 20 種防禦技能
│   ├── base_skill.py               # 抽象基底：detect() + defend() + process()
│   ├── direct_request_skill.py
│   ├── role_play_skill.py
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
├── prompt_builder/           # Stage 09: 安全 Prompt 建立
│   ├── protected_prompt_builder.py # 產生安全化 Prompt
│   └── restricted_token_guard.py   # 限制 Token 偵測
│
├── llm_gateway/              # Stage 10: LLM 連接層
│   ├── base_llm.py                 # 統一 LLM 抽象介面
│   └── ollama_client.py            # Ollama API 客戶端
│
├── runtime_monitor/          # Stage 11: Runtime 即時監控
│   ├── stream_monitor.py           # 串流即時監控器
│   ├── interruption_handler.py     # 中斷處理器
│   └── runtime_guard.py            # Runtime 防護整合
│
├── output_guard/             # Stage 12: 輸出層防護
│   └── output_guard.py             # 敏感模式過濾（secret/regex/semantic）
│
├── leakage_verifier/         # Stage 13: 洩漏驗證
│   └── leakage_verifier.py         # 完整/部分/編碼/翻譯/重構/語意洩漏驗證
│
├── event_logger/             # Stage 14: 事件紀錄
│   └── event_logger.py             # 結構化日誌、攻擊時間線、統計
│
├── benchmark/                # Stage 15: 基準測試
│   ├── run_benchmark.py            # 測試執行器
│   ├── evaluator.py                # 測試評估器
│   ├── pipeline.py                 # 自動化測試管線
│   └── results/                    # 測試結果
│
├── reports/                  # Stage 16: 報告產生
│   └── report_generator.py         # JSON/HTML/Markdown 報告
│
├── policies/                 # 政策設定檔（JSON）
├── data/                     # 資料目錄
├── logs/                     # 日誌目錄
├── config.py                 # 設定載入
└── main.py                   # 相容性入口（委派至 entry/main.py）
```

---

# 六、完整系統流程

```text
User Prompt
   ↓
[Stage 01] Protected Asset Registry
讀取系統預設與使用者自訂防護項目
   ↓
[Stage 02] Input Normalization
大小寫、空白、Unicode 混淆字、同形字符、跨語言正規化
   ↓
[Stage 03] Input Guard
XSS / 可疑格式 / 明顯敏感要求檢查
   ↓
[Stage 04] Attack Classifier
比對攻擊模式，分類攻擊類型
   ↓
[Stage 05] Risk Scoring
根據攻擊類型、資產風險、歷史對話計算風險分數
   ↓
[Stage 06] Policy Engine
決定 allow / warn / rewrite / restrict / block / authorize / escalate
   ↓
[Stage 07] Skill Router
依 category 路由至對應 Defensive Skill
   ↓
[Stage 08] Defensive Skill
執行 detect() + defend()
   ↓
[Stage 09] Prompt Builder
整合政策，產生安全化 Prompt + Token Guard
   ↓
[Stage 10] LLM Gateway
發送請求至 Ollama 或其他 LLM
   ↓
[Stage 11] Runtime Monitor
逐 chunk 即時監控，命中立即中斷
   ↓
[Stage 12] Output Guard
輸出層過濾敏感模式
   ↓
[Stage 13] Leakage Verifier
驗證完整/部分/編碼/翻譯/重構洩漏
   ↓
[Stage 14] Event Logger
記錄攻擊類型、風險分數、啟用技能、政策動作、阻擋/洩漏狀態
   ↓
Final Safe Response
```

---

# 七、受保護資產登錄表

## 7.1 系統預設防護項目

```
password, api_key, token, private_key, credential
system_prompt, internal_rule, config, database, flag
```

## 7.2 使用者自訂範例

```json
{
  "asset_id": "secret_001",
  "name": "比賽 flag",
  "type": "flag",
  "value": "picoCTF{example_flag}",
  "aliases": ["flag", "答案", "通關碼"],
  "risk_level": "high",
  "allowed_roles": ["owner"],
  "protection_modes": [
    "exact_match", "partial_match", "semantic_match",
    "encoding_match", "translation_match", "reconstruction_match"
  ]
}
```

## 7.3 資產類型

| 類型 | 說明 | 範例 |
|------|------|------|
| Exact Secret | 明確值 | flag、API key、密碼 |
| Pattern Secret | 格式規則 | 身分證、Email、JWT |
| Semantic Secret | 語意型機密 | 內部策略、客戶名單 |
| Document Secret | 文件型機密 | 合約、報告 |
| Derived Secret | 可推導出機密 | Base64、分段提示 |

---

# 八、防禦動作分級

```text
ALLOW     允許回答，僅記錄事件
WARN      允許回答，加入安全提醒與輸出檢查
REWRITE   改寫 Prompt，移除或隔離惡意指令
RESTRICT  限制模型只能回答非敏感部分
BLOCK     直接阻擋請求
AUTHORIZE 要求角色或權限驗證
ESCALATE  提高 session risk，啟用更嚴格的 runtime monitor
```

---

# 九、快速開始

## 安裝

```bash
pip install requests
```

## 執行

```bash
# 互動選單
python3 main.py

# 多層分析模式（不需 Ollama）
python3 main.py --analyze

# 列出攻擊類型
python3 main.py --list-attacks

# 列出受保護資產
python3 main.py --list-assets

# 執行基準測試
python3 main.py --benchmark

# Ollama 即時防護（需先啟動 ollama serve）
python3 main.py --ollama
```

## 自訂受保護資產

編輯 `policies/user_secret_policy.json`，加入你想保護的資料。

## 調整防禦規則

編輯 `policies/defense_rules.json`，可設定：
- `default_threshold`: 風險門檻（low / medium / high）
- `model`: Ollama 模型名稱
- `rejection_message`: 阻擋時的回覆訊息

---

# 十、技術規格

| 項目 | 內容 |
|---|---|
| Language | Python 3.10+ |
| Runtime | Ollama |
| Detection | Attack-aware Pattern Matching |
| Routing | SkillRouter — category → 20 Defensive Skills |
| Protected Assets | System Default + User-defined Registry |
| Input Guard | XSS / Suspicious Format Check |
| Output Guard | Sensitive Pattern Filter |
| Input Normalization | Unicode / Homoglyph / Full-width |
| Token Guard | Restricted Token Detection |
| Runtime Protection | Streaming Token Monitoring |
| Defense Strategy | Policy-driven Skill-based Defense |
| Leakage Verification | Exact / Partial / Encoding / Translation / Semantic |
| Logging | JSONL with structured EventLogger |
| Reporting | JSON / HTML / Markdown |
| Architecture | Flow-node (16 stages) |

---

# 十一、未來研究方向

1. **Token-level Logits Intervention** — 直接干涉下一個 token 預測
2. **Embedding Similarity Detection** — 語意相似度偵測改寫攻擊
3. **Adaptive Defense** — 根據風險與歷史動態調整策略
4. **Multi-model Runtime Guard** — 支援 Ollama / OpenAI / vLLM / llama.cpp
5. **User-defined Defense Profile** — 學生/企業/CTF/研究等模式
6. **Web UI** — Chat Session Viewer、Live Risk Dashboard
7. **Dynamic Skill Marketplace** — 使用者自訂技能動態載入

---

# 十二、專案定位

SecretGuard 並非單純的 Keyword Blocklist，而是：

> User-defined Protected Asset + Attack-aware Defensive Skill Framework

一套完整 Local LLM Runtime Security Architecture，涵蓋資產定義、攻擊分類、風險決策、技能掛載、Runtime 監控與洩漏驗證的完整防禦閉環。
