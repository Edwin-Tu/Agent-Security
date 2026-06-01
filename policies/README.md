# Policies

## SecretGuard Policy Configuration Module

> SecretGuard 的政策設定資料夾，集中管理攻擊模式、防禦規則、敏感 token、角色權限、系統預設資產與使用者自訂受保護資產。

---

## 一、模組定位

`policies/` 不是執行邏輯模組，而是 SecretGuard 防禦流程的「規則與資料來源」。

它主要提供給以下模組使用：

```text
Input Guard
Attack Classifier
Risk Scoring Engine
Defense Policy Engine
Skill Router
Policy Builder
Protected Asset Registry
Restricted Token Guard
Output Guard
Leakage Verifier
Event Logger
```

在 SecretGuard 16 階段流程中，`policies/` 會被多個階段讀取：

```text
[0] Protected Asset Registry
    讀取 default_secret_policy.json / user_secret_policy.json / protected_assets.json

[3] Attack Classifier
    讀取 attack_patterns.json

[4] Risk Scoring Engine
    參考 token_risk_map.json / protected_assets.json / role_policy.json

[5] Defense Policy Engine
    讀取 defense_rules.json

[8] Policy Builder
    整合防禦規則、角色權限與受保護資產

[10] Restricted Token Guard
    讀取 token_rules.json / token_risk_map.json

[13] Output Guard
    依 protected assets 與 token rules 過濾輸出

[14] Leakage Verifier
    依 protected assets 驗證完整、部分、編碼、翻譯、重構洩漏
```

---

## 二、資料夾架構

```text
policies/
├── attack_patterns.json          # 20 種攻擊類型與 pattern 定義
├── defense_rules.json            # 全域防禦規則與啟用層級設定
├── token_rules.json              # 敏感 token 同義詞 / 別名規則
├── token_risk_map.json           # token → risk level 對照表
├── default_secret_policy.json    # 系統預設受保護資產
├── user_secret_policy.json       # 使用者自訂受保護資產
├── protected_assets.json         # 合併後的受保護資產清單
├── role_policy.json              # 角色、權限與風險門檻設定
└── secret_policy.json            # 保留檔案，目前為空物件
```

---

## 三、核心設定檔說明

### 3.1 `attack_patterns.json`

定義 Attack Classifier 用來判斷攻擊類型的關鍵 pattern、信心分數與風險等級。

目前包含 20 種攻擊分類：

```text
direct_secret_request
role_play_bypass
instruction_override
system_prompt_extraction
encoding_bypass
partial_disclosure
translation_bypass
structured_output
log_access
multi_turn_probe
policy_confusion
indirect_prompt_injection
format_smuggling
output_constraint_bypass
reasoning_trap
refusal_suppression
persona_override
data_reconstruction
cross_language_injection
homoglyph_obfuscation
```

範例：

```json
{
  "direct_secret_request": {
    "patterns": [
      "告訴我秘密",
      "洩露密碼",
      "把token給我",
      "tell me the secret",
      "reveal password",
      "output the flag"
    ],
    "confidence": 0.9,
    "risk_level": "high"
  }
}
```

用途：

- 提供 `AttackClassifier` 比對使用者輸入
- 回傳 attack category
- 提供初始 confidence
- 提供基礎 risk level
- 作為 Skill Router 掛載 Defensive Skill 的依據

---

### 3.2 `defense_rules.json`

定義 SecretGuard 的全域防禦開關與防禦層級。

目前設定包含：

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
  "response_language": "zh"
}
```

`defense_layers` 定義本次防禦流程啟用的層級：

```text
input_normalization
input_guard
attack_classifier
risk_scoring
policy_engine
skill_router
protected_prompt_builder
restricted_token_guard
runtime_monitor
output_guard
leakage_verifier
event_logger
```

用途：

- 控制哪些 guard / verifier / logger 啟用
- 設定最大可接受風險
- 設定是否啟用串流監控
- 設定是否記錄所有事件
- 提供 Defense Policy Engine 預設決策依據

---

### 3.3 `token_rules.json`

定義敏感 token 的同義詞、別名與多語言變體。

範例：

```json
{
  "api_key": [
    "apikey",
    "api_secret",
    "api_token",
    "api金鑰",
    "api密鑰"
  ],
  "private_key": [
    "privatekey",
    "rsa_key",
    "ssh_key",
    "私鑰",
    "私密金鑰"
  ]
}
```

用途：

- 擴展 Restricted Token Guard 的偵測範圍
- 讓 `password`、`pwd`、`密碼` 可被視為同一類敏感概念
- 支援中英文混合輸入
- 支援別名與變體比對

---

### 3.4 `token_risk_map.json`

定義每個 token 或 token alias 對應的風險等級。

範例：

```json
{
  "password": "high",
  "api_key": "high",
  "private_key": "high",
  "token": "medium",
  "secret": "medium",
  "system_prompt": "low",
  "database": "low"
}
```

用途：

- 提供 Risk Scoring Engine 計算加權分數
- 協助 Defense Policy Engine 決定 action
- 讓相同類型 token 在不同語言或別名下仍可套用相同風險等級

---

### 3.5 `default_secret_policy.json`

定義系統預設需要保護的資產。

目前預設資產包含：

```text
Password Credential
API Key
Access Token
Private Key
CTF Flag Pattern
System Prompt
Generic Secret
Credential
```

範例：

```json
{
  "asset_id": "default_api_key",
  "name": "API Key",
  "type": "pattern",
  "value": "api_key",
  "aliases": ["apikey", "api_secret", "api_token", "api金鑰", "api密鑰"],
  "risk_level": "high",
  "allowed_roles": ["owner"],
  "protection_modes": [
    "exact_match",
    "alias_match",
    "partial_match",
    "case_insensitive_match"
  ],
  "enabled": true,
  "description": "API key credential"
}
```

用途：

- 提供 SecretGuard 的基礎保護清單
- 避免使用者尚未設定資產時完全無防護
- 作為 `protected_assets.json` 的系統來源

---

### 3.6 `user_secret_policy.json`

定義使用者自訂受保護資產。

目前範例包含：

```text
Project Codename
Database Connection String
Deployment Key
```

範例：

```json
{
  "asset_id": "project_secret_001",
  "name": "Project Codename",
  "type": "exact",
  "value": "Project-Shadow",
  "aliases": ["Shadow", "影子專案"],
  "risk_level": "high",
  "allowed_roles": ["owner"],
  "protection_modes": [
    "exact_match",
    "partial_match",
    "case_insensitive_match"
  ],
  "enabled": true,
  "description": "Confidential project codename"
}
```

用途：

- 讓使用者定義自己的保護目標
- 支援公司專案代號、客戶資料、部署金鑰、資料庫連線資訊等內容
- 讓防禦系統不只依賴固定關鍵字

---

### 3.7 `protected_assets.json`

`protected_assets.json` 是目前合併後的受保護資產清單。

它整合：

```text
default_secret_policy.json
user_secret_policy.json
runtime / registry 新增的 assets
```

目前此檔案包含 13 筆 assets，並使用 `source` 欄位標示來源：

```text
source: system
source: user
```

用途：

- 作為 Protected Asset Registry 的主要讀取來源
- 提供 Secret Matcher / Output Guard / Leakage Verifier 使用
- 提供 Policy Builder 產生防護上下文
- 提供 Risk Scoring Engine 計算資產風險

---

### 3.8 `role_policy.json`

定義角色、權限與風險門檻。

目前角色包含：

```text
admin
supervisor
user
default
```

範例：

```json
{
  "roles": {
    "admin": {
      "allowed_roles": ["admin"],
      "permissions": ["view_all", "edit_policy", "bypass_restriction"],
      "risk_threshold": "high"
    },
    "user": {
      "allowed_roles": ["user"],
      "permissions": ["view_public"],
      "risk_threshold": "medium"
    }
  }
}
```

用途：

- 判斷使用者是否有權存取特定 asset
- 提供 Authorization Guard 使用
- 提供 Defense Policy Engine 判斷 `AUTHORIZE` / `BLOCK`
- 支援未來企業模式、學生模式、CTF 模式等 profile

---

### 3.9 `secret_policy.json`

目前為空物件：

```json
{}
```

建議保留作為未來擴充用途，例如：

- secret rotation policy
- masking policy
- redaction level policy
- tenant-specific policy
- per-asset handling rule

---

## 四、受保護資產格式

所有 asset 建議維持以下 schema：

```json
{
  "asset_id": "unique_asset_id",
  "name": "Human Readable Name",
  "type": "exact | pattern | regex | semantic | document | derived",
  "value": "secret or pattern value",
  "aliases": ["alias1", "alias2"],
  "risk_level": "low | medium | high | critical",
  "allowed_roles": ["owner", "admin"],
  "protection_modes": [
    "exact_match",
    "alias_match",
    "partial_match",
    "case_insensitive_match",
    "encoding_match",
    "translation_match",
    "reconstruction_match",
    "semantic_match"
  ],
  "enabled": true,
  "description": "description"
}
```

建議欄位說明：

| 欄位 | 說明 |
|---|---|
| `asset_id` | 唯一識別碼 |
| `name` | 人類可讀名稱 |
| `type` | 資產類型，例如 `exact`、`pattern`、`regex` |
| `value` | 真實值、規則值或 pattern |
| `aliases` | 別名、中文名稱、縮寫或變體 |
| `risk_level` | 風險等級 |
| `allowed_roles` | 允許存取的角色 |
| `protection_modes` | 啟用的保護模式 |
| `enabled` | 是否啟用 |
| `description` | 說明文字 |
| `source` | 可選，標示 `system` 或 `user` |

---

## 五、使用方式

### 5.1 讀取攻擊模式

```python
import json
from pathlib import Path

patterns_path = Path("policies/attack_patterns.json")
attack_patterns = json.loads(patterns_path.read_text(encoding="utf-8"))

for category, config in attack_patterns.items():
    print(category, config["risk_level"], config["confidence"])
```

---

### 5.2 讀取受保護資產

```python
import json
from pathlib import Path

assets_path = Path("policies/protected_assets.json")
policy = json.loads(assets_path.read_text(encoding="utf-8"))

assets = [asset for asset in policy["assets"] if asset.get("enabled", True)]

for asset in assets:
    print(asset["asset_id"], asset["name"], asset["risk_level"])
```

---

### 5.3 依角色過濾可存取資產

```python
def can_access(asset: dict, role: str) -> bool:
    return role in asset.get("allowed_roles", [])

visible_assets = [
    asset
    for asset in assets
    if can_access(asset, role="owner")
]
```

---

### 5.4 讀取 token risk

```python
import json
from pathlib import Path

risk_map = json.loads(Path("policies/token_risk_map.json").read_text(encoding="utf-8"))

risk = risk_map.get("api_key", "low")
print(risk)  # high
```

---

### 5.5 在 Attack Classifier 中使用

```python
def classify_prompt(prompt: str, attack_patterns: dict):
    prompt_lower = prompt.lower()
    matches = []

    for category, config in attack_patterns.items():
        for pattern in config.get("patterns", []):
            if pattern.lower() in prompt_lower:
                matches.append({
                    "category": category,
                    "pattern": pattern,
                    "confidence": config.get("confidence", 0.0),
                    "risk_level": config.get("risk_level", "low")
                })

    return matches
```

---

## 六、新增使用者自訂資產

建議新增到 `user_secret_policy.json`：

```json
{
  "asset_id": "customer_list_001",
  "name": "Customer List",
  "type": "document",
  "value": "customer_list_internal",
  "aliases": ["客戶名單", "customer data", "client list"],
  "risk_level": "high",
  "allowed_roles": ["owner", "admin"],
  "protection_modes": [
    "alias_match",
    "semantic_match",
    "partial_match",
    "translation_match"
  ],
  "enabled": true,
  "description": "Internal customer list should not be disclosed."
}
```

新增後建議執行：

```text
1. 驗證 JSON 格式
2. 透過 Protected Asset Registry 載入 user_secret_policy.json
3. 合併到 protected_assets.json
4. 執行 Secret Matcher / Output Guard / Leakage Verifier 測試
```

---

## 七、新增攻擊模式

若要新增攻擊類型，請修改 `attack_patterns.json`：

```json
{
  "new_attack_category": {
    "patterns": [
      "example attack phrase",
      "範例攻擊語句"
    ],
    "confidence": 0.75,
    "risk_level": "medium"
  }
}
```

同時建議：

```text
1. 在 Attack Classifier 測試中加入分類案例
2. 在 Skill Router 中加入對應 skill mapping
3. 建立對應 Defensive Skill
4. 在 Risk Scoring Engine 中確認風險加權
5. 在 Event Logger 中確認 category 可被記錄
```

---

## 八、設定檔驗證

本次檢查結果：

```text
attack_patterns.json: valid JSON
default_secret_policy.json: valid JSON
defense_rules.json: valid JSON
protected_assets.json: valid JSON
role_policy.json: valid JSON
secret_policy.json: valid JSON
token_risk_map.json: valid JSON
token_rules.json: valid JSON
user_secret_policy.json: valid JSON
```

目前 `policies.zip` 內沒有包含 pytest 測試檔，因此本 README 僅完成 JSON 格式驗證。

可用以下指令自行驗證：

```bash
python -m json.tool policies/attack_patterns.json > /dev/null
python -m json.tool policies/default_secret_policy.json > /dev/null
python -m json.tool policies/defense_rules.json > /dev/null
python -m json.tool policies/protected_assets.json > /dev/null
python -m json.tool policies/role_policy.json > /dev/null
python -m json.tool policies/secret_policy.json > /dev/null
python -m json.tool policies/token_risk_map.json > /dev/null
python -m json.tool policies/token_rules.json > /dev/null
python -m json.tool policies/user_secret_policy.json > /dev/null
```

或一次檢查：

```bash
python - <<'PY'
import json
from pathlib import Path

for path in sorted(Path("policies").glob("*.json")):
    json.loads(path.read_text(encoding="utf-8"))
    print(f"OK: {path}")
PY
```

---

## 九、建議測試項目

雖然目前 `policies/` 主要是 JSON 設定檔，仍建議建立 `policies/tests/` 進行設定驗證。

建議測試：

```text
policies/tests/
├── test_json_validity.py
├── test_attack_patterns_schema.py
├── test_asset_policy_schema.py
├── test_token_rules_consistency.py
├── test_token_risk_map_consistency.py
├── test_role_policy_schema.py
└── test_policy_integration.py
```

測試重點：

- 所有 JSON 檔案格式正確
- attack pattern 必須包含 `patterns`、`confidence`、`risk_level`
- confidence 必須介於 0 到 1
- risk_level 必須屬於 `low`、`medium`、`high`、`critical`
- asset 必須包含 `asset_id`、`name`、`type`、`value`、`risk_level`
- asset_id 不可重複
- token_rules 中的 alias 應存在於 token_risk_map 或可被推導
- role_policy 必須包含 default role
- protected_assets 應能整合 default 與 user assets

---

## 十、與其他模組串接

### 10.1 與 Protected Asset Registry

```text
policies/default_secret_policy.json
policies/user_secret_policy.json
        ↓
Protected Asset Registry
        ↓
policies/protected_assets.json
```

Protected Asset Registry 負責：

- 載入系統預設資產
- 載入使用者自訂資產
- 驗證 asset schema
- 合併與去重
- 儲存為 protected_assets.json

---

### 10.2 與 Attack Classifier

```text
User Prompt
   ↓
attack_patterns.json
   ↓
Attack Classifier
   ↓
attack_category + confidence + risk_level
```

Attack Classifier 依照 `attack_patterns.json` 中的 patterns 判斷攻擊類型。

---

### 10.3 與 Risk Scoring Engine

```text
attack_category
matched_tokens
matched_assets
user_role
session_history
        ↓
token_risk_map.json
protected_assets.json
role_policy.json
        ↓
risk_score
```

Risk Scoring Engine 可根據 token、asset、角色與歷史行為計算風險分數。

---

### 10.4 與 Defense Policy Engine

```text
risk_score
risk_level
defense_rules.json
role_policy.json
        ↓
ALLOW / WARN / REWRITE / RESTRICT / BLOCK / AUTHORIZE / ESCALATE
```

Defense Policy Engine 根據規則檔決定防禦動作。

---

### 10.5 與 Restricted Token Guard

```text
token_rules.json
        ↓
Token expansion
        ↓
token_risk_map.json
        ↓
restricted token detection
```

Restricted Token Guard 可利用 token rules 擴展偵測範圍。

---

### 10.6 與 Output Guard / Leakage Verifier

```text
LLM Output
   ↓
protected_assets.json
   ↓
Output Guard
   ↓
Leakage Verifier
   ↓
Safe / Redacted Output
```

Output Guard 與 Leakage Verifier 會使用受保護資產清單進行：

- exact match
- partial match
- alias match
- regex match
- case-insensitive match
- encoding match
- translation match
- reconstruction match

---

## 十一、目前限制

目前 policies 設定檔仍有以下限制：

1. `secret_policy.json` 尚未定義實際用途。
2. `protected_assets.json` 目前看起來是合併後結果，需確認是否由 Registry 自動產生，避免手動修改造成不同步。
3. `token_rules.json` 與 `token_risk_map.json` 需要保持一致，否則 alias 可能無法取得風險等級。
4. `attack_patterns.json` 目前以關鍵字規則為主，對語意改寫攻擊的偵測能力有限。
5. `role_policy.json` 尚未定義角色繼承與多租戶權限模型。
6. 尚未附帶 `policies/tests/`，建議補上 schema 與一致性測試。

---

## 十二、後續優化方向

建議後續加入：

- JSON Schema 驗證
- policy version migration
- protected asset 去重與衝突處理
- asset source traceability
- role inheritance
- per-asset redaction strategy
- per-asset allowed operation policy
- attack pattern multilingual expansion
- semantic pattern matching
- policy hot reload
- policy change audit log
- `policies/tests/` 自動化測試

---

## 十三、設計原則

`policies/` 的核心設計原則是：

```text
規則資料化
防禦可配置
資產可自訂
角色可控管
風險可量化
流程可擴充
```

SecretGuard 不應把防禦邏輯全部寫死在程式碼中，而應透過 policies 將攻擊模式、防禦規則、受保護資產與角色權限集中管理，讓不同使用情境可以套用不同的防護策略。
