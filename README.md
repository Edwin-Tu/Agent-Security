# SecretGuard

## Local LLM Runtime Defense Framework

SecretGuard 是一套針對本地大型語言模型（Local LLM）設計的攻擊感知防禦框架。
它透過受保護資產定義、攻擊分類、風險評估、策略決策、技能路由、Prompt 綁定、Runtime 監控、輸出檢查與洩漏驗證，構成一個完整的防禦閉環。

---

# 一、專案介紹

SecretGuard 的核心目標是：

- 讓使用者自定義受保護資產
- 將攻擊分類與風險分數納入防禦決策
- 在輸入、生成、輸出三個階段提供防護
- 以結構化事件日誌記錄安全分析結果

這不只是單純的關鍵字封鎖，而是結合策略與技能的動態防禦系統。

---

# 二、核心特性

- **Protected Asset Registry**：可自訂資產、別名與保護模式
- **Attack Classification**：辨識 prompt injection、社交工程、敏感請求等攻擊類型
- **Risk Scoring**：根據攻擊類型、資產風險、歷史狀態計算風險分數
- **Defense Policy Engine**：動態決定 ALLOW / WARN / REWRITE / RESTRICT / BLOCK / AUTHORIZE / ESCALATE
- **Defensive Skill Router**：依攻擊類型啟動對應防禦技能
- **Protected Prompt Builder**：將安全策略嵌入 prompt，降低 LLM 風險
- **Runtime Monitor**：串流生成時即時截斷可疑輸出
- **Output Guard**：輸出層過濾敏感模式並產生安全版本
- **Leakage Verifier**：驗證完整、部分、編碼、翻譯、重構洩漏
- **Event Logger**：記錄 risk、policy、asset、skill、leakage、blocked 等結果

---

# 三、系統流程

SecretGuard 的防禦流程大致如下：

1. 輸入正規化
2. 受保護資產匹配
3. 輸入層檢查
4. 攻擊分類
5. 風險計算
6. 防禦政策決策
7. 技能路由
8. Prompt 安全化
9. LLM 呼叫
10. Runtime 監控
11. 輸出防護
12. 洩漏驗證
13. 事件記錄

這個流程可視為「攻擊感知 → 風險評估 → 策略決策 → 防禦執行 → 日誌追蹤」的完整循環。

---

# 四、專案結構

```text
Agent-Security/
├── entry/                # 系統入口與 CLI
├── asset_registry/       # 受保護資產管理
├── input_normalization/  # 輸入正規化
├── input_guard/          # 輸入防護
├── attack_classifier/    # 攻擊分類
├── risk_scoring/         # 風險評估
├── policy_engine/        # 防禦策略
├── skill_router/         # 技能路由
├── defensive_skills/     # Defensive Skill 實作
├── prompt_builder/       # 安全 Prompt 建置
├── llm_gateway/          # LLM 連接層
├── runtime_monitor/      # Runtime 監控
├── output_guard/         # 輸出防護
├── leakage_verifier/     # 洩漏驗證
├── event_logger/         # 事件紀錄
├── benchmark/            # 基準測試與評估
├── reports/              # 報告生成
├── policies/             # 規則設定
├── logs/                 # 日誌輸出
├── config.py             # 全域設定
└── main.py               # 程式入口（呼叫 entry/main.py）
```

---

# 五、快速開始

## 安裝依賴

```bash
pip install requests
```

## 執行方式

```bash
# 互動式啟動
python3 main.py

# 多層分析模式（不需 Ollama）
python3 main.py --analyze

# 列出攻擊類型
python3 main.py --list-attacks

# 列出受保護資產
python3 main.py --list-assets

# 執行基準測試
python3 main.py --benchmark

# Ollama 即時防護（須先啟動 ollama serve）
python3 main.py --ollama
```

## 開發測試

```bash
pytest entry/tests -q
pytest output_guard/tests -q
pytest event_logger/tests -q
pytest -q
```

---

# 六、配置說明

## 受保護資產

使用者可透過 `policies/user_secret_policy.json` 定義自訂資產，包含：

- `asset_id`
- `name`
- `type`
- `value`
- `aliases`
- `risk_level`
- `allowed_roles`
- `protection_modes`

## 防禦策略

在 `policies/defense_rules.json` 中調整：

- `default_threshold`：風險分數門檻
- `model`：Ollama 模型名稱
- `rejection_message`：阻擋回應訊息

---

# 七、事件紀錄

SecretGuard 會將防禦決策與偵測結果記錄為結構化事件，包含：

- `attack_type`
- `risk_score`
- `risk_level`
- `risk_factors`
- `policy_action`
- `blocked`
- `matched_asset_ids`
- `final_response_type`
- `output_summary`
- `metadata`

這些事件可用於審計、報告與後續分析。

---

# 八、適用場景

- 本地測試或研發環境的 LLM 防護
- 企業內部敏感資料防洩漏
- CTF / 比賽環境的 flag 防護
- 具有自訂資產需求的語言模型防禦

---

# 九、未來方向

1. **Token-level Logits Intervention** — 直接干涉下一個 token 預測
2. **Embedding Similarity Detection** — 語意相似度偵測改寫攻擊
3. **Adaptive Defense** — 根據風險與歷史動態調整策略
4. **Multi-model Runtime Guard** — 支援 Ollama / OpenAI / vLLM / llama.cpp
5. **User-defined Defense Profile** — 學生/企業/CTF/研究等模式
6. **Web UI** — Chat Session Viewer、Live Risk Dashboard
7. **Dynamic Skill Marketplace** — 使用者自訂技能動態載入

---

# 十、專案定位

SecretGuard 不是單純的 Blocklist，而是一套：

> User-defined Protected Asset + Attack-aware Defensive Skill Framework

它結合資產管理、攻擊分類、風險評估、策略路由、Runtime 監控與輸出檢查，打造可擴充的 Local LLM 防禦架構。
