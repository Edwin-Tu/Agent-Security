# [13] Output Guard 開發任務說明

## 1. 任務背景

Output Guard 是 SecretGuard 系統流程中的第 13 個模組，位於 Local LLM / Ollama 生成回應之後、Leakage Verifier 之前。

本模組負責對模型最終輸出進行最後一道安全檢查，避免模型在回覆中洩漏 API Key、Private Key、Token、Password、flag、system prompt、使用者自訂 secret、secret alias、secret partial fragment，以及其他敏感資訊。

Output Guard 的核心定位不是判斷使用者輸入是否為攻擊，而是檢查「模型準備輸出的內容是否安全」。若輸出內容包含敏感資訊，Output Guard 需要依照風險程度進行放行、遮蔽、改寫或阻擋。

---

## 2. 開發模式要求：TDD

本任務必須採用 TDD（Test-Driven Development）開發模式。

開發順序必須為：

```text
1. 先建立測試案例
2. 先執行測試並確認測試失敗
3. 再開發 Output Guard 功能
4. 重新執行測試並確認通過
5. 視需求進行重構
6. 最後確認所有測試與功能皆完成
```

測試檔案路徑必須放在：

```text
output_guard/tests
```

不得先完成主要功能後才補測試。

---

## 3. 建議資料夾結構

請建立以下模組結構：

```text
output_guard/
├── __init__.py
├── output_guard.py
├── output_guard_result.py
├── pattern_detector.py
├── asset_output_matcher.py
├── redactor.py
├── severity.py
├── rules/
│   └── default_output_patterns.json
└── tests/
    ├── test_output_guard_patterns.py
    ├── test_output_guard_assets.py
    ├── test_output_guard_partial_leak.py
    ├── test_output_guard_redaction.py
    └── test_output_guard_result.py
```

若專案目前已有 `guards/output_guard.py`，可以保留相容匯入，但本階段建議以獨立資料夾 `output_guard/` 作為第 13 個流程模組，方便日後與 16 個流程對應管理。

---

## 4. 核心功能需求

### 4.1 Sensitive Pattern Detection

Output Guard 必須能偵測常見敏感格式。

至少支援以下類型：

```text
API Key
Token
Password
Private Key
JWT
flag
system prompt leakage keyword
secret assignment pattern
```

範例需能偵測：

```text
sk-proj-xxxxxxxx
sk-xxxxxxxx
ghp_xxxxxxxxxxxxxxxx
-----BEGIN PRIVATE KEY-----
eyJhbGciOi...
picoCTF{example_flag}
password=123456
api_key=abcdefg
token: abcdefg
```

偵測邏輯可以使用 regex / pattern matching 實作。

---

### 4.2 Protected Asset Matching

Output Guard 必須支援比對使用者自訂的 protected assets。

每個 protected asset 可包含：

```text
asset_id
name
type
value
aliases
risk_level
protection_modes
```

Output Guard 必須至少支援：

```text
1. 完整 secret value 命中
2. alias 命中
3. 多個 asset 同時命中
4. 不同大小寫的基本比對
```

範例：

```json
{
  "asset_id": "secret_001",
  "name": "比賽 flag",
  "type": "flag",
  "value": "picoCTF{example_flag}",
  "aliases": ["flag", "答案", "通關碼"],
  "risk_level": "high",
  "protection_modes": [
    "exact_match",
    "partial_match",
    "semantic_match",
    "encoding_match",
    "translation_match",
    "reconstruction_match"
  ]
}
```

若模型輸出包含 `picoCTF{example_flag}` 或 alias，例如 `通關碼`，Output Guard 必須能辨識。

---

### 4.3 Partial Leakage Detection

Output Guard 必須具備初步 partial leakage 偵測能力。

至少支援：

```text
1. secret 前綴洩漏
2. secret 後綴洩漏
3. secret 中段片段洩漏
4. 多段片段同時出現在輸出中
```

範例：

```text
The flag starts with picoCTF{
The key begins with sk-proj-
The secret contains example_flag
```

建議設定 partial matching threshold，避免過短片段造成大量誤判。

建議初始規則：

```text
低於 4 個字元的片段不視為 partial leak
長度 >= 4 且命中 protected asset 片段時，標記為 PARTIAL_LEAK
```

---

### 4.4 Redaction / Rewrite / Block

Output Guard 必須根據嚴重程度採取不同處理動作。

至少支援以下 action：

```text
ALLOW
REDACT
BLOCK
```

可預留以下 action：

```text
REWRITE
ESCALATE
```

建議行為：

```text
安全輸出 → ALLOW
一般 API key / token / password → REDACT
完整 flag / private key / 高風險 protected asset → BLOCK 或 REDACT
partial leak → REDACT 並標記風險
```

Redaction placeholder 建議：

```text
[REDACTED_SECRET]
[REDACTED_API_KEY]
[REDACTED_PRIVATE_KEY]
[REDACTED_FLAG]
[REDACTED_TOKEN]
[REDACTED_PARTIAL]
```

需避免 redaction 產生巢狀錯誤，例如：

```text
[REDACTED_[REDACTED_PARTIAL]]
```

---

### 4.5 OutputGuardResult

Output Guard 必須回傳結構化結果，方便後續 Leakage Verifier 與 Event Logger 使用。

建議建立：

```python
from dataclasses import dataclass, field

@dataclass
class OutputGuardResult:
    original_output: str
    safe_output: str
    action: str
    is_blocked: bool
    is_redacted: bool
    leakage_detected: bool
    matched_patterns: list[str] = field(default_factory=list)
    matched_assets: list[str] = field(default_factory=list)
    risk_level: str = "none"
    reasons: list[str] = field(default_factory=list)
```

Output Guard 主流程建議提供：

```python
class OutputGuard:
    def inspect(self, text: str, protected_assets: list[dict] | None = None) -> OutputGuardResult:
        ...
```

---

## 5. Severity 分級建議

請建立基本風險分級：

```text
NO_LEAK
LOW_RISK_HINT
PARTIAL_LEAK
FULL_LEAK
CRITICAL_LEAK
```

建議對應：

```text
NO_LEAK         → ALLOW
LOW_RISK_HINT   → ALLOW 或 REDACT
PARTIAL_LEAK    → REDACT
FULL_LEAK       → REDACT 或 BLOCK
CRITICAL_LEAK   → BLOCK
```

---

## 6. 測試要求

測試必須放在：

```text
output_guard/tests
```

至少需要包含以下測試案例。

### 6.1 Pattern Detection Tests

檔案建議：

```text
output_guard/tests/test_output_guard_patterns.py
```

必測項目：

```text
test_api_key_is_redacted
test_github_token_is_redacted
test_jwt_is_detected
test_private_key_is_blocked
test_flag_pattern_is_blocked_or_redacted
test_password_assignment_is_redacted
test_safe_output_is_allowed
```

---

### 6.2 Protected Asset Tests

檔案建議：

```text
output_guard/tests/test_output_guard_assets.py
```

必測項目：

```text
test_user_defined_secret_is_detected
test_user_defined_secret_is_redacted
test_secret_alias_is_detected
test_multiple_assets_are_detected
test_case_insensitive_asset_match
```

---

### 6.3 Partial Leakage Tests

檔案建議：

```text
output_guard/tests/test_output_guard_partial_leak.py
```

必測項目：

```text
test_secret_prefix_partial_leak_is_detected
test_secret_suffix_partial_leak_is_detected
test_secret_middle_fragment_is_detected
test_short_fragment_is_not_false_positive
test_multiple_fragments_raise_partial_leak
```

---

### 6.4 Redaction Tests

檔案建議：

```text
output_guard/tests/test_output_guard_redaction.py
```

必測項目：

```text
test_api_key_redaction_placeholder
test_private_key_block_placeholder
test_multiple_secrets_are_all_redacted
test_redaction_does_not_create_nested_placeholders
test_safe_text_is_not_modified
```

---

### 6.5 Result Object Tests

檔案建議：

```text
output_guard/tests/test_output_guard_result.py
```

必測項目：

```text
test_result_contains_original_output
test_result_contains_safe_output
test_result_marks_blocked_output
test_result_marks_redacted_output
test_result_contains_matched_patterns
test_result_contains_matched_assets
test_result_contains_risk_level
test_result_contains_reasons
```

---

## 7. 建議實作流程

### Step 1：建立測試檔

先建立 `output_guard/tests`，並完成上述測試案例。

先執行：

```bash
pytest output_guard/tests -v
```

此時測試應該失敗，因為功能尚未完成。

---

### Step 2：建立資料結構

建立：

```text
output_guard/output_guard_result.py
output_guard/severity.py
```

完成：

```text
OutputGuardResult
Severity constants
Action constants
```

---

### Step 3：建立 Pattern Detector

建立：

```text
output_guard/pattern_detector.py
output_guard/rules/default_output_patterns.json
```

完成常見敏感格式偵測。

---

### Step 4：建立 Asset Output Matcher

建立：

```text
output_guard/asset_output_matcher.py
```

完成：

```text
exact secret matching
alias matching
case-insensitive matching
partial fragment matching
```

---

### Step 5：建立 Redactor

建立：

```text
output_guard/redactor.py
```

完成：

```text
sensitive pattern redaction
protected asset redaction
partial leakage redaction
private key / critical secret block handling
nested placeholder prevention
```

---

### Step 6：建立 OutputGuard 主流程

建立：

```text
output_guard/output_guard.py
```

主流程：

```text
1. 接收模型輸出 text
2. 載入 protected_assets
3. 執行 pattern detection
4. 執行 asset matching
5. 執行 partial leakage detection
6. 根據 severity 決定 action
7. 產生 safe_output
8. 回傳 OutputGuardResult
```

---

### Step 7：執行測試並修正

執行：

```bash
pytest output_guard/tests -v
```

所有測試必須通過。

---

## 8. 與其他模組的整合需求

Output Guard 後續需能與以下模組整合：

```text
[0] Protected Asset Registry
[8] Policy Builder
[10] Restricted Token Guard
[12] Runtime Stream Monitor
[14] Leakage Verifier
[15] Event Logger
```

本階段最低整合要求：

```text
1. inspect() 可接收 protected_assets
2. 回傳 OutputGuardResult
3. 結果中包含 matched_patterns / matched_assets / risk_level / reasons
4. safe_output 可直接作為最終輸出
```

---

## 9. 驗收條件

本任務完成時，必須符合以下條件。

### 9.1 測試驗收

必須存在測試路徑：

```text
output_guard/tests
```

必須可執行：

```bash
pytest output_guard/tests -v
```

且所有測試通過。

---

### 9.2 功能驗收

Output Guard 必須完成以下功能：

```text
1. 可偵測 API key / token / password / private key / JWT / flag
2. 可偵測使用者自訂 protected asset value
3. 可偵測 protected asset alias
4. 可偵測初步 partial leakage
5. 可將敏感內容 redaction
6. 可阻擋 critical leakage
7. 可保留安全輸出不變
8. 可回傳 OutputGuardResult
9. 可列出 matched_patterns
10. 可列出 matched_assets
11. 可提供 risk_level
12. 可提供 reasons
```

---

### 9.3 品質驗收

需符合：

```text
1. 程式碼模組化
2. 不將所有邏輯塞在單一檔案
3. pattern detection、asset matching、redaction、result object 分層清楚
4. 測試案例名稱清楚
5. 測試能反映 Output Guard 的安全目標
6. 不破壞安全文字輸出
7. 不產生巢狀 redaction placeholder
```

---

## 10. 最小可交付版本 MVP

MVP 至少必須完成：

```text
output_guard/output_guard.py
output_guard/output_guard_result.py
output_guard/pattern_detector.py
output_guard/asset_output_matcher.py
output_guard/redactor.py
output_guard/severity.py
output_guard/tests
```

並通過：

```bash
pytest output_guard/tests -v
```

---

## 11. 後續擴充方向

本階段完成後，可在下一階段擴充：

```text
1. encoded output leakage detection
2. Base64 / Hex / ROT13 secret detection
3. translation leakage detection
4. reconstruction leakage detection
5. semantic secret leakage detection
6. 與 Leakage Verifier 深度整合
7. 與 Event Logger 整合輸出安全事件
8. 與 Runtime Stream Monitor 共用 matcher / redactor
```

---

## 12. 完成定義

此任務完成代表：

```text
Output Guard 已具備最終輸出安全檢查能力，能在模型回覆送出前偵測、遮蔽或阻擋敏感內容，並以結構化 OutputGuardResult 提供後續 Leakage Verifier 與 Event Logger 使用。
```
