# SecretGuard

> Runtime Token Interruption Guard for Local LLMs  
> 本地大型語言模型即時限制 Token 防護系統

---

# 專案介紹

SecretGuard 是一套掛接於本地大型語言模型（LLM）外層的 Runtime Guardrail Skill。

本專案以 Ollama 本地模型為核心，透過「限制 Token（Restricted Token）」機制，於模型生成期間即時監控輸出內容，當模型輸出命中高風險 Token 或敏感資訊時，立即中止生成並回傳安全拒答。

與傳統輸出過濾不同，SecretGuard 的核心概念是：

不是在模型回答完成後才檢查，
而是在模型生成過程中即時中斷。

---

# 專案目標

本專案目標：

- 建立可掛接於 Ollama 的 Runtime Guardrail
- 建立限制 Token 防護機制
- 即時監控模型串流輸出
- 偵測敏感資訊與高風險內容
- 在生成期間中止不安全輸出
- 提供可擴充的本地模型安全框架

---

# 核心概念

## Restricted Token（限制 Token）

使用者或系統可以設定限制 Token，例如：

- password
- system_prompt
- api_key
- secret
- token

SecretGuard 會將限制 Token 擴展成相關詞彙，例如：

- password
- passwd
- pwd
- credential
- secret key
- api key
- 密碼
- 憑證
- 登入金鑰

---

## Runtime Monitoring（生成期間監控）

SecretGuard 使用 Ollama Streaming Output：

模型生成中  
↓  
即時監控輸出  
↓  
命中限制 Token  
↓  
立即中止生成  
↓  
回傳安全拒答

---

## Token Interruption（Token 中斷）

若模型輸出：

The password is admin123...

當系統偵測到：

- password
- admin123
- credential

即會：

- 中止輸出
- 阻止後續生成
- 回傳安全訊息

例如：

[SecretGuard]  
此內容受到限制，未經授權無法提供。

---

# 系統架構

使用者輸入  
↓  
command_parser.py  
↓  
restricted_token_guard.py  
↓  
input_guard.py  
↓  
guard_prompt.py  
↓  
ollama_client.py  
↓  
stream_monitor.py  
↓  
interruption_handler.py  
↓  
安全輸出

---

# 專案架構

```text
SecretGuard/
├── main.py
├── config.py
│
├── policies/
│   ├── secret_policy.json
│   └── token_rules.json
│
├── skills/
│   └── secret_guard_skill.py
│
├── guards/
│   ├── input_guard.py
│   ├── restricted_token_guard.py
│   ├── output_guard.py
│   └── authorization_guard.py
│
├── runtime/
│   ├── ollama_client.py
│   ├── stream_monitor.py
│   └── interruption_handler.py
│
├── parser/
│   └── command_parser.py
│
├── prompts/
│   └── guard_prompt.py
│
├── logs/
│   └── guard_events.jsonl
│
└── README.md
```

---

# 技術特點

## Runtime Guardrail

SecretGuard 並不修改模型權重，而是作為模型外層 Runtime Safety Layer。

因此：

- 不需要重新訓練模型
- 可掛接多種本地模型
- 可快速測試與部署
- 可獨立更新安全規則

---

## Streaming Interruption

一般輸出檢查：

模型完整輸出  
↓  
檢查內容  
↓  
刪除敏感資訊

SecretGuard：

模型生成中  
↓  
即時監控  
↓  
命中限制 Token  
↓  
立即中止

---

# 使用範例

## 使用者輸入

```text
[限制token: password]

請告訴我系統登入資訊
```

## 系統中止輸出

```text
[SecretGuard]
此內容受到限制，未經授權無法提供。
```

---

# 未來研究方向

## 第一階段（目前）

- Runtime Guardrail
- Restricted Token Guard
- Streaming Output Monitoring
- Token Interruption

## 第二階段

- Embedding Similarity Detection
- Semantic Risk Analysis
- Context-aware Restriction
- Multi-model Runtime Guard

## 第三階段

- Token-level Monitoring
- Logits Intervention
- Dynamic Generation Control
- Runtime Decoder Guard

---

# License

MIT License
