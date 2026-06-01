# Output Guard

> SecretGuard 輸出層敏感資訊檢查與遮蔽模組  
> Output-layer Sensitive Information Detection, Redaction, and Blocking Module

---

## 1. 模組定位

`output_guard` 是 SecretGuard 流程中的第 **[13] Output Guard**，負責在模型產生回應後、交給使用者之前，進行最後一層輸出安全檢查。

它的主要任務是：

- 偵測 LLM 輸出中是否包含敏感資訊
- 比對內建敏感格式，例如 API Key、Token、JWT、Private Key、Flag、Password
- 比對使用者自訂的 protected assets
- 偵測完整洩漏與部分洩漏
- 依照嚴重度決定 `ALLOW`、`REDACT` 或 `BLOCK`
- 回傳可安全顯示的 `safe_output`

在完整 SecretGuard 流程中，Output Guard 位於：

```text
LLM / Ollama
   ↓
Runtime Stream Monitor
   ↓
[13] Output Guard
   ↓
[14] Leakage Verifier
   ↓
[15] Event Logger
   ↓
Final Safe Response
```

---

## 2. 專案架構

目前模組結構如下：

```text
output_guard/
├── __init__.py
├── output_guard.py
├── output_guard_result.py
├── pattern_detector.py
├── asset_output_matcher.py
├── redactor.py
├── severity.py
│
├── rules/
│   └── default_output_patterns.json
│
└── tests/
    ├── __init__.py
    ├── test_output_guard_assets.py
    ├── test_output_guard_partial_leak.py
    ├── test_output_guard_patterns.py
    ├── test_output_guard_redaction.py
    └── test_output_guard_result.py
```

---

## 3. 核心功能

### 3.1 Pattern Detection

由 `PatternDetector` 負責。

它會讀取：

```text
output_guard/rules/default_output_patterns.json
```

目前內建規則包含：

| Pattern | 說明 | 預設處理 |
|---|---|---|
| `api_key_sk` | `sk-` 開頭 API Key | `REDACT` |
| `api_key_generic` | `sk-proj-` 類型 API Key | `REDACT` |
| `github_token` | GitHub token | `REDACT` |
| `jwt` | JWT token | `REDACT` |
| `private_key` | RSA / EC / Private Key 區塊 | `BLOCK` |
| `flag_pattern` | CTF flag 格式 | `BLOCK` |
| `password_assignment` | `password=...` / `pwd=...` | `REDACT` |
| `api_key_assignment` | `api_key=...` / `secret_key=...` | `REDACT` |
| `token_assignment` | `token=...` / `access_token=...` | `REDACT` |
| `aws_key` | AWS Access Key ID | `REDACT` |

---

### 3.2 Protected Asset Matching

由 `AssetOutputMatcher` 負責。

它會根據外部傳入的 `protected_assets` 檢查模型輸出是否洩漏使用者自訂機密。

支援模式：

```text
exact_match
partial_match
```

範例 protected asset：

```python
protected_assets = [
    {
        "asset_id": "secret_001",
        "name": "test flag",
        "type": "flag",
        "value": "picoCTF{example_flag}",
        "aliases": ["flag", "通關碼"],
        "risk_level": "high",
        "protection_modes": ["exact_match", "partial_match"],
    }
]
```

可偵測：

```text
picoCTF{example_flag}
PICOCTF{EXAMPLE_FLAG}
flag
通關碼
picoCTF{
example_flag
```

---

### 3.3 Partial Leak Detection

`AssetOutputMatcher` 支援部分洩漏偵測。

目前邏輯會將 secret value 拆成長度至少 4 的片段，檢查輸出中是否包含 secret 的局部片段。

例如 protected value：

```text
picoCTF{example_flag}
```

以下輸出會被視為 partial leak：

```text
The flag starts with picoCTF{
The secret ends with example_flag}
The secret contains example_flag in the middle
```

---

### 3.4 Redaction

由 `Redactor` 負責。

它會將敏感內容替換為安全 placeholder。

常見 placeholder：

| 類型 | Placeholder |
|---|---|
| API Key | `[REDACTED_API_KEY]` |
| Token / JWT | `[REDACTED_TOKEN]` |
| Private Key | `[REDACTED_PRIVATE_KEY]` |
| Flag | `[REDACTED_FLAG]` |
| Generic Secret | `[REDACTED_SECRET]` |
| Partial Leak | `[REDACTED_PARTIAL]` |

目前也有避免產生巢狀 placeholder 的保護，例如避免出現：

```text
[REDACTED_[REDACTED_SECRET]]
```

---

### 3.5 Action Decision

Output Guard 會根據偵測結果決定最終動作。

| Action | 說明 |
|---|---|
| `ALLOW` | 無洩漏，允許原文輸出 |
| `REDACT` | 偵測到敏感內容，遮蔽後輸出 |
| `BLOCK` | 偵測到高風險或 critical 洩漏，標記為阻擋 |

目前 severity 與 action 對應如下：

| Severity | Action |
|---|---|
| `NO_LEAK` | `ALLOW` |
| `LOW_RISK_HINT` | `ALLOW` |
| `PARTIAL_LEAK` | `REDACT` |
| `FULL_LEAK` | `REDACT` |
| `CRITICAL_LEAK` | `BLOCK` |

---

## 4. 主要類別說明

### 4.1 `OutputGuard`

檔案：

```text
output_guard/output_guard.py
```

主要入口類別。

```python
from output_guard.output_guard import OutputGuard

output_guard = OutputGuard()
result = output_guard.inspect("password=123456")
```

主要方法：

```python
inspect(text: str, protected_assets: list[dict] | None = None) -> OutputGuardResult
```

負責整合：

- `PatternDetector`
- `AssetOutputMatcher`
- `Redactor`
- severity / action decision
- `OutputGuardResult`

---

### 4.2 `PatternDetector`

檔案：

```text
output_guard/pattern_detector.py
```

功能：

- 載入 JSON pattern rules
- 使用 regular expression 偵測敏感格式
- 支援新增自訂 pattern

範例：

```python
from output_guard.pattern_detector import PatternDetector

scanner = PatternDetector()
scanner.add_pattern(
    name="custom_secret",
    pattern=r"SECRET-[A-Z0-9]{8}",
    severity="FULL_LEAK",
    action="REDACT",
    placeholder="[REDACTED_SECRET]",
)

findings = scanner.detect("token is SECRET-ABCDEFGH")
```

---

### 4.3 `AssetOutputMatcher`

檔案：

```text
output_guard/asset_output_matcher.py
```

功能：

- 比對使用者自訂 protected assets
- 支援 `exact_match`
- 支援 `partial_match`
- 支援 aliases
- 回傳 matched asset id、matched pattern、severity 與 action

---

### 4.4 `Redactor`

檔案：

```text
output_guard/redactor.py
```

功能：

- 根據 pattern finding 遮蔽敏感內容
- 根據 asset value 遮蔽完整 secret
- 根據 asset fragment 遮蔽 partial leak
- 避免重複遮蔽造成巢狀 placeholder

---

### 4.5 `OutputGuardResult`

檔案：

```text
output_guard/output_guard_result.py
```

回傳資料結構：

```python
@dataclass
class OutputGuardResult:
    original_output: str
    safe_output: str
    action: str
    is_blocked: bool
    is_redacted: bool
    leakage_detected: bool
    matched_patterns: list[str]
    matched_assets: list[str]
    risk_level: str
    reasons: list[str]
```

欄位說明：

| 欄位 | 說明 |
|---|---|
| `original_output` | 原始模型輸出 |
| `safe_output` | 經過遮蔽後可安全顯示的輸出 |
| `action` | `ALLOW` / `REDACT` / `BLOCK` |
| `is_blocked` | 是否阻擋 |
| `is_redacted` | 是否有遮蔽 |
| `leakage_detected` | 是否偵測到洩漏 |
| `matched_patterns` | 命中的內建 pattern 或 asset pattern |
| `matched_assets` | 命中的 protected asset id |
| `risk_level` | 洩漏嚴重度 |
| `reasons` | 命中原因說明 |

---

## 5. 使用方式

### 5.1 基本使用

```python
from output_guard.output_guard import OutputGuard

output_guard = OutputGuard()

result = output_guard.inspect("Hello, this is a normal response.")

print(result.action)
print(result.safe_output)
```

輸出：

```text
ALLOW
Hello, this is a normal response.
```

---

### 5.2 偵測並遮蔽 API Key

```python
from output_guard.output_guard import OutputGuard

output_guard = OutputGuard()

text = "My API key is sk-proj-AbCdEfGhIjKlMnOpQrStUvWxYz123456"
result = output_guard.inspect(text)

print(result.leakage_detected)
print(result.action)
print(result.safe_output)
```

可能輸出：

```text
True
REDACT
My API key is [REDACTED_API_KEY]
```

---

### 5.3 偵測 Private Key

```python
from output_guard.output_guard import OutputGuard

output_guard = OutputGuard()

text = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQ
-----END PRIVATE KEY-----"""

result = output_guard.inspect(text)

print(result.action)
print(result.is_blocked)
print(result.safe_output)
```

Private Key 屬於 critical leak，預設 action 為：

```text
BLOCK
```

---

### 5.4 搭配 Protected Assets 使用

```python
from output_guard.output_guard import OutputGuard

output_guard = OutputGuard()

protected_assets = [
    {
        "asset_id": "secret_001",
        "name": "比賽 flag",
        "type": "flag",
        "value": "picoCTF{example_flag}",
        "aliases": ["flag", "通關碼"],
        "risk_level": "high",
        "protection_modes": ["exact_match", "partial_match"],
    }
]

text = "The secret value is picoCTF{example_flag}"
result = output_guard.inspect(text, protected_assets=protected_assets)

print(result.leakage_detected)
print(result.matched_assets)
print(result.safe_output)
```

可能輸出：

```text
True
['secret_001']
The secret value is [REDACTED_SECRET]
```

---

### 5.5 偵測 Partial Leak

```python
from output_guard.output_guard import OutputGuard

output_guard = OutputGuard()

assets = [
    {
        "asset_id": "secret_001",
        "name": "test flag",
        "type": "flag",
        "value": "picoCTF{example_flag}",
        "aliases": ["flag", "通關碼"],
        "risk_level": "high",
        "protection_modes": ["exact_match", "partial_match"],
    }
]

text = "The flag starts with picoCTF{"
result = output_guard.inspect(text, protected_assets=assets)

print(result.leakage_detected)
print(result.risk_level)
print(result.safe_output)
```

可能輸出：

```text
True
PARTIAL_LEAK
The flag starts with [REDACTED_PARTIAL]
```

---

## 6. 測試方式

在專案根目錄執行：

```bash
pytest output_guard/tests -v
```

本次檢查結果：

```text
30 passed
```

測試涵蓋範圍：

| 測試檔案 | 內容 |
|---|---|
| `test_output_guard_patterns.py` | API Key、GitHub Token、JWT、Private Key、Flag、Password pattern 偵測 |
| `test_output_guard_assets.py` | 使用者自訂 protected assets、alias、大小寫比對 |
| `test_output_guard_partial_leak.py` | secret 前綴、後綴、中段片段與多片段洩漏 |
| `test_output_guard_redaction.py` | 遮蔽 placeholder、多 secret 遮蔽、避免巢狀 placeholder |
| `test_output_guard_result.py` | `OutputGuardResult` 欄位完整性 |

---

## 7. 與其他 SecretGuard 模組的串接

### 7.1 與 Runtime Stream Monitor

`Runtime Stream Monitor` 可在生成過程中逐 chunk 呼叫 Output Guard。

```python
from output_guard.output_guard import OutputGuard

output_guard = OutputGuard()

for chunk in llm_stream:
    result = output_guard.inspect(chunk, protected_assets=protected_assets)

    if result.is_blocked:
        stop_generation()
        break

    emit(result.safe_output)
```

---

### 7.2 與 Leakage Verifier

Output Guard 偏向「即時遮蔽與阻擋」，Leakage Verifier 則負責更完整的洩漏驗證。

建議流程：

```text
LLM output
   ↓
OutputGuard.inspect()
   ↓
LeakageVerifier.verify()
   ↓
EventLogger.log()
```

Output Guard 可先產生：

```python
result.safe_output
result.action
result.risk_level
result.matched_patterns
result.matched_assets
```

再交給 Leakage Verifier 做更完整的：

- full leak verification
- partial leak verification
- encoded leak verification
- translated leak verification
- reconstruction leak verification

---

### 7.3 與 Event Logger

Output Guard 的結果可直接轉成事件記錄。

```python
event_logger.log({
    "stage": "output_guard",
    "action": result.action,
    "risk_level": result.risk_level,
    "leakage_detected": result.leakage_detected,
    "matched_patterns": result.matched_patterns,
    "matched_assets": result.matched_assets,
    "reasons": result.reasons,
})
```

---

### 7.4 與 Protected Asset Registry

`Protected Asset Registry` 負責提供受保護資產清單，Output Guard 負責在輸出階段檢查是否洩漏這些資產。

```python
assets = protected_asset_registry.list_assets()
result = output_guard.inspect(model_output, protected_assets=assets)
```

---

## 8. 設計重點

### 8.1 Output Guard 不是單純 Keyword Blocklist

它同時結合：

```text
Regex Pattern Detection
User-defined Protected Asset Matching
Partial Leak Detection
Severity-based Action Decision
Safe Output Redaction
```

因此可以保護：

- 系統內建敏感格式
- 使用者自訂 secret
- secret alias
- secret fragment
- critical credential block

---

### 8.2 與 Leakage Verifier 的差異

| 模組 | 主要目的 |
|---|---|
| `Output Guard` | 輸出前即時檢查、遮蔽、阻擋 |
| `Leakage Verifier` | 更完整驗證是否發生洩漏，包含語意、翻譯、重構等型態 |

建議不要只依賴其中一個模組，而是串接使用：

```text
Output Guard 先阻擋明顯洩漏
Leakage Verifier 再驗證進階洩漏
Event Logger 記錄防禦結果
```

---

## 9. 目前限制

目前版本主要限制如下：

1. Partial leak 採固定長度片段比對，可能需要進一步控制 false positive。
2. Pattern detection 主要依賴 regular expression，尚未加入語意相似度。
3. `AssetOutputMatcher` 目前支援 `exact_match` 與 `partial_match`，尚未完整支援 encoding / translation / reconstruction matching。
4. `BLOCK` 目前仍會產生 redacted `safe_output`，後續可加上更明確的 block message。
5. 尚未加入多輪輸出累積檢查，需要搭配 Session Memory 或 Leakage Verifier 擴充。

---

## 10. 後續優化方向

建議下一階段可加入：

- Encoding leak detection，例如 Base64、Hex、ROT13
- Translation leak detection，例如中文描述英文 secret
- Reconstruction leak detection，例如分段輸出 secret
- Semantic leak detection，例如改寫後仍透露內部資訊
- 更細緻的 false positive 控制
- 可設定 partial fragment 長度與命中數門檻
- 支援 custom rule loading from project config
- 支援 block message template
- 與 Event Logger 整合成標準事件格式
- 與 Runtime Stream Monitor 整合 chunk-level interruption

---

## 11. 開發狀態

目前測試狀態：

```text
30 passed
```

已完成能力：

- 內建敏感 pattern 偵測
- API Key / Token / JWT / Private Key / Flag / Password 偵測
- 使用者自訂 protected assets 偵測
- Alias 偵測
- Partial leak 偵測
- Redaction placeholder
- Critical leak block action
- OutputGuardResult 標準回傳結構
- 單元測試覆蓋主要功能

---

## 12. 簡易範例

```python
from output_guard.output_guard import OutputGuard

output_guard = OutputGuard()

protected_assets = [
    {
        "asset_id": "secret_001",
        "name": "API key",
        "type": "api_key",
        "value": "sk-proj-my-secret-key-12345",
        "aliases": ["mykey", "my-api-key"],
        "risk_level": "high",
        "protection_modes": ["exact_match", "partial_match"],
    }
]

model_output = "Here is your key: sk-proj-my-secret-key-12345"

result = output_guard.inspect(model_output, protected_assets=protected_assets)

if result.is_blocked:
    print("[BLOCKED]")
elif result.is_redacted:
    print(result.safe_output)
else:
    print(model_output)
```

---

## 13. 模組總結

`output_guard` 是 SecretGuard 的最後輸出防線之一。

它負責確認模型回覆在交給使用者前，不會直接暴露：

```text
API Key
Token
JWT
Private Key
Password
Flag
User-defined Secret
Partial Secret Fragment
```

此模組適合接在：

```text
LLM Gateway / Runtime Stream Monitor
```

之後，並接續：

```text
Leakage Verifier / Event Logger
```

形成完整的輸出防護鏈。
