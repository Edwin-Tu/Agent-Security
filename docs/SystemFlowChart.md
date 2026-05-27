# SecretGuard 系統流程圖

> 最新架構定位：掛載 Defensive Skills 增加本地 LLM 的防護能力，並支援使用者自訂受保護資產。

---

## 一、核心設計概念

SecretGuard 不只是阻擋固定關鍵字，而是建立一套：

```text
受保護資產定義
    ↓
攻擊意圖分析
    ↓
防禦策略決策
    ↓
Defensive Skill 掛載
    ↓
Runtime 生成監控
    ↓
輸出洩漏驗證
    ↓
事件記錄與規則更新
```

的完整防禦閉環。

---

## 二、完整系統流程

```text
使用者輸入 Prompt
        ↓
[0] Protected Asset Registry
讀取系統預設防護項目與使用者自訂防護項目
例如：flag、API Key、密碼、專案代號、客戶資料、內部文件、公司機密
        ↓
[1] Input Normalization
正規化輸入內容
處理大小寫、空白、Unicode 混淆字、跨語言與可疑格式
        ↓
[2] Input Guard
基礎檢查：是否包含明顯攻擊字詞、敏感要求、XSS、可疑格式
        ↓
[3] Attack Classifier
判斷屬於哪一種 attack pattern
比對 attack_patterns.json 與 attacks.json
        ↓
[4] Risk Scoring Engine
根據攻擊類型、受保護資產、歷史對話、命中規則計算風險分數
        ↓
[5] Defense Policy Engine
根據風險決定防禦動作：
放行 / 警告 / 改寫 / 阻擋 / 要求授權 / 啟用加強監控
        ↓
[6] Skill Router
根據 attack category 與 policy action 掛載對應 Defensive Skill
        ↓
[7] Defensive Skill
執行 detect() + defend()
可進行：阻擋、改寫、加入限制條件、標記風險、啟用特殊檢查
        ↓
[8] Policy Builder
整合系統預設規則、使用者自訂資產、角色權限、防禦策略
產生本次請求的防護政策
        ↓
[9] Protected Prompt Builder
產生安全化後的 Prompt
把「不可洩漏內容」與「允許回答範圍」明確注入防護上下文
        ↓
[10] Restricted Token Guard
阻擋敏感 token、使用者自訂 secret、別名、片段與變體
        ↓
[11] Local LLM / Ollama
模型生成回應
        ↓
[12] Runtime Stream Monitor
生成過程中即時檢查 token / secret / leakage
逐 chunk 監控，命中立即中斷
        ↓
[13] Output Guard
最後輸出檢查與過濾
檢查 API key、private key、flag、使用者自訂 secret 等敏感模式
        ↓
[14] Leakage Verifier
驗證是否出現完整洩漏、部分洩漏、編碼洩漏、翻譯洩漏、重構洩漏
        ↓
[15] Event Logger
記錄本次請求：
attack type、risk score、啟用 skill、policy action、是否阻擋、是否洩漏
        ↓
安全回應
```

---

## 三、簡化版流程

```text
User Prompt
   ↓
Protected Asset Registry
   ↓
Input Normalization
   ↓
Attack Detection
   ↓
Risk Scoring
   ↓
Defense Policy Decision
   ↓
Skill Mounting
   ↓
Protected Prompt Building
   ↓
Local LLM Generation
   ↓
Runtime Monitoring
   ↓
Leakage Verification
   ↓
Safe Response
```

---

## 四、受保護資產定義流程

SecretGuard 必須先知道「哪些東西需要被保護」，因此新增 Protected Asset Registry。

```text
系統預設防護項目
例如：password、api_key、token、private_key、system_prompt、flag
        ↓
使用者自訂防護項目
例如：公司名稱、專案代號、客戶資料、學生資料、內部規則、文件內容
        ↓
Protected Asset Registry
建立受保護資產清單
        ↓
Policy Builder
產生防護規則
        ↓
Secret Matcher / Leakage Verifier
於輸入、生成中、輸出後進行檢查
```

---

## 五、受保護資產類型

```text
1. Exact Secret
   明確值，例如 flag、API key、密碼、通關碼

2. Pattern Secret
   格式規則，例如身分證、Email、電話、JWT、sk- 開頭金鑰

3. Semantic Secret
   語意型機密，例如內部策略、未公開專案、客戶名單

4. Document Secret
   文件型機密，例如合約、報告、內部文件、上傳資料

5. Derived Secret
   可被推導出的機密，例如前 3 碼、Base64、分段提示、翻譯描述
```

---

## 六、Skill 掛載流程

```text
Attack Classifier
        ↓
判斷攻擊類型
        ↓
Skill Router
        ↓
掛載對應 Defensive Skill
        ↓
Skill.detect()
確認是否命中該類攻擊
        ↓
Skill.defend()
執行防禦策略
        ↓
Defense Policy Engine
決定最終 action
```

---

## 七、防禦動作分級

```text
ALLOW
允許回答，僅記錄事件

WARN
允許回答，但加入安全提醒與輸出檢查

REWRITE
改寫 Prompt，移除或隔離惡意指令

RESTRICT
限制模型只能回答非敏感部分

BLOCK
直接阻擋請求

AUTHORIZE
要求角色或權限驗證

ESCALATE
提高 session risk，啟用更嚴格的 runtime monitor
```

---

## 八、完整防禦閉環

```text
Define Assets
   ↓
Detect Attack
   ↓
Score Risk
   ↓
Decide Policy
   ↓
Mount Skill
   ↓
Build Protected Prompt
   ↓
Monitor Generation
   ↓
Verify Leakage
   ↓
Log Event
   ↓
Improve Policy
```

---

## 九、研究重點

新版 SecretGuard 的核心研究不只是「20 種攻擊對應 20 個 Skill」，而是：

> 使用者可以定義自己的受保護資產，系統再根據攻擊類型、風險分數與防護政策，動態掛載 Defensive Skills，防止模型在輸入、生成中與輸出後洩漏敏感資訊。

---

## 十、推薦新增模組

```text
core/
├── protected_asset_registry.py   # 受保護資產登錄表
├── policy_builder.py             # 根據資產與角色建立防護政策
├── defense_policy_engine.py      # 決定 allow / warn / rewrite / block
├── risk_scoring_engine.py        # 計算單輪與多輪風險分數
├── protected_prompt_builder.py   # 產生安全化 Prompt
├── secret_matcher.py             # 機密值、別名、片段、變體比對
└── leakage_verifier.py           # 驗證完整/部分/編碼/語意洩漏

policies/
├── default_secret_policy.json    # 系統預設保護項目
├── user_secret_policy.json       # 使用者自訂保護項目
├── protected_assets.json         # 受保護資產清單
└── role_policy.json              # 角色與授權政策
```
