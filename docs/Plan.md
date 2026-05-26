# SecretGuard 專案計畫書

## A Lightweight Guardrail Framework for Local LLM Defense

---

# 1. 專案概述

SecretGuard 是一套專為本地大型語言模型（LLM）設計的輕量級 Guardrail 防禦框架。
本專案主要聚焦於以下安全問題：

* Prompt Injection（提示詞注入）
* Jailbreak（越獄攻擊）
* Secret Leakage（秘密外洩）
* Role Confusion（角色混淆）
* Skill / Tool 權限濫用

本專案不重新訓練模型，而是在 LLM 外部建立安全防護層。

SecretGuard 適用於：

* 本地 LLM
* Ollama 環境
* 低資源設備
* 學術研究
* AI Security Benchmark

---

# 2. 專案目標

## 核心目標

* 建立本地 LLM Guardrail 防禦框架
* 偵測 Prompt Injection 攻擊
* 防止秘密外洩
* 建立輸入與輸出過濾機制
* 建立安全 Benchmark 系統
* 比較不同模型的防禦效果

---

# 3. 研究問題（Research Questions）

## RQ1

本地 LLM 是否容易受到 Prompt Injection 攻擊？

## RQ2

Guardrail 是否能有效降低秘密外洩風險？

## RQ3

哪些防禦策略最適合小型本地模型？

## RQ4

輕量化 Guardrail 是否能在低資源環境下有效運作？

---

# 4. 系統架構

```text id="ht23du"
使用者
 ↓
Input Guard（輸入防護）
 ↓
Policy Engine（規則引擎）
 ↓
LLM（Ollama）
 ↓
Output Guard（輸出防護）
 ↓
Risk Analyzer（風險分析）
 ↓
Report Generator（報告生成）
 ↓
使用者
```

---

# 5. 核心模組設計

---

# 5.1 Input Guard（輸入防護）

## 目的

在模型推理前阻擋惡意 Prompt。

## 功能

* Prompt Injection Detection
* Jailbreak Detection
* Role Confusion Detection
* 可疑 Prompt 分析

## 範例

檢測：

```text id="8qk7xj"
Ignore previous instructions
```

## 輸出結果

```json id="r3uxqm"
{
  "risk": "high",
  "category": "prompt_injection",
  "blocked": true
}
```

---

# 5.2 Policy Engine（規則引擎）

## 目的

判斷請求是否允許執行。

## 功能

* Rule-based 防禦
* Risk Threshold
* Role Validation
* Secret Access Policy

## 範例

```python id="a1m3ql"
if risk_score > 0.7:
    block_request()
```

---

# 5.3 LLM Connector（模型連接層）

## 目的

管理與本地 LLM 的通訊。

## 功能

* Ollama 整合
* Context 管理
* Timeout 控制
* 多模型支援

## 初期支援模型

* qwen2.5
* phi4-mini
* gemma
* mistral

---

# 5.4 Output Guard（輸出防護）

## 目的

檢查模型輸出內容。

## 功能

* Secret Leakage Detection
* 敏感資訊過濾
* Redaction（遮罩）
* 風險分析

## 範例

原始輸出：

```text id="3k6q9y"
API_KEY=123456
```

保護後：

```text id="vvbq0n"
API_KEY=[REDACTED]
```

---

# 5.5 Secret Scanner（秘密掃描器）

## 目的

偵測敏感資訊。

## 偵測內容

* API Key
* Password
* Access Token
* Hidden Prompt
* 個人資料

---

# 5.6 Risk Scorer（風險評分系統）

## 目的

為攻擊與輸出內容進行風險評估。

## 範例

```json id="4s4m1w"
{
  "prompt_injection": 0.91,
  "jailbreak": 0.82,
  "secret_leakage": 0.77
}
```

---

# 5.7 Benchmark System（Benchmark 系統）

## 目的

評估攻擊成功率與防禦效果。

## Benchmark 類型

| 類型                 | 說明               |
| ------------------ | ---------------- |
| Direct Injection   | 直接提示詞攻擊          |
| Indirect Injection | 文件內嵌攻擊           |
| Jailbreak          | 越獄攻擊             |
| Role Confusion     | 身份混淆             |
| Prompt Leak        | System Prompt 洩漏 |
| Secret Extraction  | 套取秘密資訊           |

---

# 5.8 Report Generator（報告生成器）

## 目的

生成安全測試報告。

## 報告內容

* Leak Rate
* Defense Success Rate
* Risk Score
* Weakest Category
* Blocked Attack Logs
* Multi-model Comparison

## 支援格式

* Markdown
* HTML
* JSON

---

# 6. 未來模組：Skill Guard

## 目的

保護 AI Agent 的外部工具權限。

## 保護對象

* Terminal
* File Reader
* Browser
* Code Execution

## 架構

```text id="7wlz0m"
LLM 想使用 Tool
 ↓
Skill Guard
 ├─ Permission Check
 ├─ Injection Detection
 ├─ Dangerous Command Check
 ↓
Allow / Deny
```

---

# 7. 研究貢獻（Contributions）

## Contribution 1

提出適用於本地 LLM 的輕量級 Guardrail Framework。

## Contribution 2

建立 Secret Leakage Benchmark 與評估流程。

## Contribution 3

比較 Guardrail 前後的安全差異。

## Contribution 4

分析小型本地模型的安全弱點。

---

# 8. 技術棧（Tech Stack）

## Backend

| 技術      | 用途            |
| ------- | ------------- |
| Python  | 主程式語言         |
| FastAPI | API Framework |
| Ollama  | 本地模型執行        |
| Docker  | 部署            |
| JSON    | 攻擊資料集         |

---

## 防禦系統

| 技術            | 用途        |
| ------------- | --------- |
| Regex         | 規則檢測      |
| Risk Scoring  | 威脅評估      |
| Prompt Parser | Prompt 分析 |

---

## 報告系統

| 技術       | 用途           |
| -------- | ------------ |
| Markdown | 報告生成         |
| HTML     | 視覺化          |
| CSV      | Benchmark 紀錄 |

---

# 9. 建議專案結構

```text id="vtrrfd"
SecretGuard/
│
├─ check.py
├─ configs/
├─ benchmark/
├─ attacks/
├─ defenses/
├─ reports/
├─ models/
├─ src/
│   ├─ input_guard.py
│   ├─ output_guard.py
│   ├─ risk_scorer.py
│   ├─ policy_engine.py
│   ├─ leakage_detector.py
│   ├─ benchmark_runner.py
│   └─ report_generator.py
│
├─ docs/
├─ README.md
└─ requirements.txt
```

---

# 10. 開發階段規劃

---

# Phase 1 — Benchmark 基礎建立

## 目標

* 建立攻擊資料集
* 測試本地模型
* 測量 Secret Leakage

---

# Phase 2 — Input Guard

## 目標

* 偵測 Prompt Injection
* 偵測 Jailbreak

---

# Phase 3 — Output Guard

## 目標

* Secret Leakage Detection
* Redaction
* Risk Scoring

---

# Phase 4 — Multi-model Evaluation

## 目標

比較：

* qwen
* phi
* gemma
* mistral

---

# Phase 5 — Skill Security

## 目標

保護：

* Terminal Skill
* File Access
* Browser Access

---

# 11. 未來研究方向

* RAG Security
* Agent Security
* Multi-Agent Defense
* Adaptive Guardrail
* Dynamic Risk Analysis
* Autonomous Defense Systems

---

# 12. 最終願景

SecretGuard 的目標是：

> 成為本地 LLM 的輕量級 AI 安全基礎設施。

本專案不僅研究 AI 漏洞，也聚焦於建立未來 AI Agent 與 Tool-Using LLM 的安全防禦架構。
