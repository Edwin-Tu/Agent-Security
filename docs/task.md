# task.md

# SecretGuard 專案重構任務清單

> 目標：
> 將 SecretGuard 從「功能模組混合式架構」重構為「流程節點式架構」，使每個流程節點對應一個資料夾（子系統），方便維護、擴充與研究展示。

---

# 一、重構核心理念

新版架構：

```text
一個流程
= 一個資料夾
= 一個子系統
= 一個責任範圍
```

目的：

* 提高可維護性
* 提高模組化程度
* 降低耦合
* 方便擴充 Defensive Skills
* 方便未來增加新 Runtime
* 方便論文與簡報展示
* 方便多人協作

---

# 二、目標架構

```text
Agent-Security/
│
├── 00_entry/
├── 01_asset_registry/
├── 02_input_normalization/
├── 03_input_guard/
├── 04_attack_classifier/
├── 05_risk_scoring/
├── 06_policy_engine/
├── 07_skill_router/
├── 08_defensive_skills/
├── 09_prompt_builder/
├── 10_llm_gateway/
├── 11_runtime_monitor/
├── 12_output_guard/
├── 13_leakage_verifier/
├── 14_event_logger/
├── 15_benchmark/
├── 16_reports/
│
├── policies/
├── logs/
├── data/
├── README.md
└── config.py
```

---

# 三、流程架構對應

## 00_entry

### 功能

系統入口與啟動流程。

### 任務

* [ ] 建立 `00_entry/`
* [ ] 移動 `main.py`
* [ ] 建立系統初始化流程
* [ ] 建立模組載入順序

---

## 01_asset_registry

### 功能

管理受保護資產。

### 包含

* Protected Asset Registry
* Secret Matcher
* User-defined Assets

### 任務

* [ ] 建立 `01_asset_registry/`
* [ ] 移動：

  * `protected_asset_registry.py`
  * `secret_matcher.py`
* [ ] 建立 asset loader
* [ ] 支援 JSON 資產格式
* [ ] 支援 alias / partial / semantic matching

---

## 02_input_normalization

### 功能

輸入正規化。

### 任務

* [ ] 建立 `02_input_normalization/`
* [ ] 移動：

  * `token_expander.py`
  * `token_risk_classifier.py`
* [ ] 建立 Unicode normalization
* [ ] 建立 homoglyph normalization
* [ ] 建立 cross-language normalization

---

## 03_input_guard

### 功能

輸入層基礎防護。

### 任務

* [ ] 建立 `03_input_guard/`
* [ ] 移動：

  * `input_guard.py`
  * `authorization_guard.py`
  * `defense_context.py`
* [ ] 建立 suspicious pattern detection
* [ ] 建立 XSS / prompt injection quick check

---

## 04_attack_classifier

### 功能

攻擊分類。

### 任務

* [ ] 建立 `04_attack_classifier/`
* [ ] 移動：

  * `attack_classifier.py`
  * `attack_taxonomy.py`
  * `attacks.json`
  * `attack_patterns.json`
* [ ] 建立 category scoring
* [ ] 建立 multi-label attack support

---

## 05_risk_scoring

### 功能

風險計算。

### 任務

* [ ] 建立 `05_risk_scoring/`
* [ ] 移動：

  * `risk_scoring_engine.py`
  * `session_memory.py`
  * `token_risk_map.json`
* [ ] 建立 session risk escalation
* [ ] 建立 multi-turn attack scoring

---

## 06_policy_engine

### 功能

防禦策略決策。

### 任務

* [ ] 建立 `06_policy_engine/`
* [ ] 移動：

  * `defense_policy_engine.py`
  * `policy_builder.py`
* [ ] 移動所有 policy json
* [ ] 建立：

  * allow
  * warn
  * rewrite
  * restrict
  * block
  * authorize
  * escalate

---

## 07_skill_router

### 功能

技能路由。

### 任務

* [ ] 建立 `07_skill_router/`
* [ ] 移動：

  * `skill_router.py`
* [ ] 建立：

  * category → skill mapping
  * multi-skill mounting
  * priority handling

---

## 08_defensive_skills

### 功能

防禦技能。

### 任務

* [ ] 建立 `08_defensive_skills/`
* [ ] 移動全部 defensive skills
* [ ] 建立：

  * `BaseSkill`
  * `detect()`
  * `defend()`
* [ ] 建立 skill metadata system
* [ ] 建立 dynamic skill loading

---

## 09_prompt_builder

### 功能

建立安全 Prompt。

### 任務

* [ ] 建立 `09_prompt_builder/`
* [ ] 移動：

  * `protected_prompt_builder.py`
  * `restricted_token_guard.py`
* [ ] 建立 protected system prompt
* [ ] 建立 response restriction layer

---

## 10_llm_gateway

### 功能

模型連接層。

### 任務

* [ ] 建立 `10_llm_gateway/`
* [ ] 移動：

  * `ollama_client.py`
* [ ] 建立：

  * unified llm interface
  * model abstraction layer
  * future API adapter

---

## 11_runtime_monitor

### 功能

Runtime 即時監控。

### 任務

* [ ] 建立 `11_runtime_monitor/`
* [ ] 移動：

  * `stream_monitor.py`
  * `interruption_handler.py`
  * `runtime_guard.py`
* [ ] 建立 streaming detection
* [ ] 建立 token-level interruption
* [ ] 建立 runtime escalation

---

## 12_output_guard

### 功能

輸出層防護。

### 任務

* [ ] 建立 `12_output_guard/`
* [ ] 移動：

  * `output_guard.py`
* [ ] 建立：

  * secret filtering
  * regex filtering
  * semantic filtering

---

## 13_leakage_verifier

### 功能

洩漏驗證。

### 任務

* [ ] 建立 `13_leakage_verifier/`
* [ ] 移動：

  * `leakage_verifier.py`
* [ ] 支援：

  * exact leakage
  * partial leakage
  * encoded leakage
  * translation leakage
  * reconstruction leakage

---

## 14_event_logger

### 功能

事件紀錄。

### 任務

* [ ] 建立 `14_event_logger/`
* [ ] 移動：

  * `guard_events.jsonl`
* [ ] 建立：

  * structured logging
  * attack timeline
  * session history

---

## 15_benchmark

### 功能

Benchmark 系統。

### 任務

* [ ] 建立 `15_benchmark/`
* [ ] 移動：

  * `run_benchmark.py`
  * `evaluator.py`
  * `results/`
* [ ] 建立 benchmark pipeline
* [ ] 建立 attack coverage report

---

## 16_reports

### 功能

報告產生器。

### 任務

* [ ] 建立 `16_reports/`
* [ ] 移動：

  * `report_generator.py`
* [ ] 建立：

  * html report
  * markdown report
  * benchmark summary
  * leakage statistics

---

# 四、後續擴充方向

## Runtime Layer

* [ ] OpenAI-compatible API
* [ ] vLLM support
* [ ] llama.cpp support

## Detection Layer

* [ ] Embedding similarity detection
* [ ] Semantic leakage detection
* [ ] Logits intervention

## Skill System

* [ ] Dynamic skill marketplace
* [ ] User-defined skill loading

## UI Layer

* [ ] Web UI Interceptor
* [ ] Chat Session Viewer
* [ ] Live Risk Dashboard

---

# 五、最終目標

建立：

```text
Attack-aware
Runtime-intervenable
User-defined Asset Protection Framework
```

使 SecretGuard 不只是：

```text
Keyword Blocklist
```

而是：

```text
完整 Local LLM Runtime Security Architecture
```
