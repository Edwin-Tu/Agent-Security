# Leakage Verifier

> SecretGuard `[14] Leakage Verifier` 模組  
> 驗證本地 LLM 回應是否洩漏受保護資產，並產生建議動作與遮蔽後輸出。

---

## 1. 模組定位

`leakage_verifier` 是 SecretGuard 防禦流程中的輸出後驗證模組，位於：

```text
[13] Output Guard
        ↓
[14] Leakage Verifier
        ↓
[15] Event Logger
        ↓
Safe Response
```

它的責任不是單純阻擋關鍵字，而是根據 `Protected Asset Registry` 提供的受保護資產，檢查模型輸出是否包含：

- 完整洩漏
- 部分洩漏
- 編碼洩漏
- 翻譯 / 別名洩漏
- 語意洩漏
- 分段重構洩漏

當偵測到洩漏後，模組會回傳結構化結果，包含最高嚴重度、命中類型、命中片段、建議動作與遮蔽後輸出。

---

## 2. 目錄架構

```text
leakage_verifier/
├── __init__.py
├── leakage_verifier.py              # 主驗證器，整合所有 detector
├── leakage_result.py                # LeakageResult / LeakageMatch 資料結構
├── leakage_types.py                 # 洩漏類型、嚴重度、建議動作常數
│
├── exact_leak_detector.py           # 完整 secret 洩漏偵測
├── partial_leak_detector.py         # 部分片段洩漏偵測
├── encoding_leak_detector.py        # Base64 / Hex / URL Encoding / ROT13 洩漏偵測
├── reconstruction_leak_detector.py  # 分段重構洩漏偵測
├── translation_leak_detector.py     # 翻譯、別名、跨語言洩漏偵測
├── semantic_leak_detector.py        # 語意相關詞洩漏偵測
├── redactor.py                      # 洩漏內容遮蔽器
│
└── tests/
    ├── test_exact_leak_detector.py
    ├── test_partial_leak_detector.py
    ├── test_encoding_leak_detector.py
    ├── test_reconstruction_leak_detector.py
    ├── test_translation_leak_detector.py
    ├── test_semantic_leak_detector.py
    ├── test_redactor.py
    └── test_leakage_verifier.py
```

---

## 3. 核心功能

### 3.1 完整洩漏偵測：ExactLeakDetector

檢查模型輸出是否直接包含受保護資產的完整值。

範例：

```text
secret value: picoCTF{example_flag}
model output: The flag is picoCTF{example_flag}
```

結果：

```text
leak_type: full_leak
severity: critical
recommended_action: block
```

---

### 3.2 部分洩漏偵測：PartialLeakDetector

檢查模型是否只洩漏 secret 的部分片段。

例如：

```text
secret value: picoCTF{example_flag}
model output: The prefix is pico
```

模組會將 secret 拆成固定長度片段後比對輸出內容。

預設最小片段長度：

```python
min_fragment_length = 4
```

結果：

```text
leak_type: partial_leak
severity: high
recommended_action: redact
```

---

### 3.3 編碼洩漏偵測：EncodingLeakDetector

檢查模型是否透過編碼方式輸出 secret。

目前支援：

```text
Base64
Hex
URL Encoding
ROT13
```

範例：

```text
secret value: secret123
model output: c2VjcmV0MTIz
```

結果：

```text
leak_type: encoding_leak
match_type: base64
severity: critical
recommended_action: block
```

---

### 3.4 分段重構洩漏偵測：ReconstructionLeakDetector

檢查模型是否透過多個片段讓使用者重組出 secret。

例如：

```text
secret value: ABCD-1234-EFGH
model output: first part ABCD, second part 1234, last part EFGH
```

模組會計算片段覆蓋率，當覆蓋率達到門檻時判定為重構洩漏。

目前設定：

```python
MIN_FRAGMENT_LENGTH = 4
COVERAGE_THRESHOLD = 0.6
```

結果：

```text
leak_type: reconstruction_leak
severity: high
recommended_action: block
```

---

### 3.5 翻譯 / 別名洩漏偵測：TranslationLeakDetector

檢查模型是否輸出受保護資產的 aliases。

適合處理：

```text
中文別名
英文別名
翻譯後名稱
通關碼、答案、flag 等替代表述
```

範例 asset：

```json
{
  "asset_id": "secret_001",
  "name": "比賽 flag",
  "value": "picoCTF{example_flag}",
  "aliases": ["flag", "答案", "通關碼"]
}
```

如果輸出包含 `通關碼` 或 `答案`，就可能被標記為 translation leak。

---

### 3.6 語意洩漏偵測：SemanticLeakDetector

檢查模型輸出是否包含與受保護資產語意相關的 alias。

目前為規則式語意比對，主要依賴 asset 中的 `aliases` 欄位。

當命中多個語意關鍵詞時，嚴重度會提高：

```python
SEMANTIC_HIGH_THRESHOLD = 2
```

結果：

```text
leak_type: semantic_leak
severity: medium 或 high
recommended_action: redact
```

---

### 3.7 洩漏遮蔽：Redactor

`Redactor` 會依照洩漏類型將敏感內容替換成對應 placeholder。

| Leak Type | Placeholder |
|---|---|
| `full_leak` | `[REDACTED_SECRET]` |
| `partial_leak` | `[REDACTED_PARTIAL]` |
| `encoding_leak` | `[REDACTED_ENCODED_SECRET]` |
| `reconstruction_leak` | `[REDACTED_RECONSTRUCTION]` |
| `translation_leak` | `[REDACTED_TRANSLATION]` |
| `semantic_leak` | `[REDACTED_SEMANTIC]` |

---

## 4. LeakageVerifier 主流程

`LeakageVerifier` 會根據每個 asset 的 `protection_modes` 動態啟用對應 detector。

```python
MODE_DETECTOR_MAP = {
    "exact_match": ExactLeakDetector,
    "partial_match": PartialLeakDetector,
    "encoding_match": EncodingLeakDetector,
    "reconstruction_match": ReconstructionLeakDetector,
    "translation_match": TranslationLeakDetector,
    "semantic_match": SemanticLeakDetector,
}
```

執行流程：

```text
LLM Output
    ↓
讀取 protected_assets
    ↓
依 protection_modes 啟用 detectors
    ↓
收集 LeakageMatch
    ↓
計算 highest_severity
    ↓
決定 recommended_action
    ↓
產生 redacted_output
    ↓
回傳 LeakageResult
```

---

## 5. 使用方式

### 5.1 基本使用

```python
from leakage_verifier import LeakageVerifier

verifier = LeakageVerifier()

protected_assets = [
    {
        "asset_id": "secret_001",
        "name": "CTF Flag",
        "value": "picoCTF{example_flag}",
        "aliases": ["flag", "答案", "通關碼"],
        "protection_modes": [
            "exact_match",
            "partial_match",
            "encoding_match",
            "reconstruction_match",
            "translation_match",
            "semantic_match",
        ],
    }
]

output_text = "The flag is picoCTF{example_flag}."

result = verifier.verify(
    output_text=output_text,
    protected_assets=protected_assets,
)

print(result.is_leak)
print(result.highest_severity)
print(result.recommended_action)
print(result.redacted_output)
```

可能輸出：

```text
True
critical
block
The flag is [REDACTED_SECRET].
```

---

### 5.2 使用 session context 偵測重構洩漏

`ReconstructionLeakDetector` 可透過 `session_context` 接收過去累積的片段。

```python
result = verifier.verify(
    output_text="The final part is EFGH.",
    protected_assets=protected_assets,
    session_context={
        "accumulated_fragments": ["ABCD", "1234"]
    },
)
```

適合用於偵測多輪對話中的 secret reconstruction attack。

---

## 6. 回傳資料結構

### 6.1 LeakageResult

```python
@dataclass
class LeakageResult:
    is_leak: bool
    highest_severity: str
    leak_types: list[str]
    matches: list[LeakageMatch]
    recommended_action: str
    redacted_output: str
```

欄位說明：

| 欄位 | 說明 |
|---|---|
| `is_leak` | 是否偵測到洩漏 |
| `highest_severity` | 本次輸出最高嚴重度 |
| `leak_types` | 命中的洩漏類型列表 |
| `matches` | 詳細命中紀錄 |
| `recommended_action` | 建議後續動作，例如 `allow`、`redact`、`block` |
| `redacted_output` | 遮蔽敏感資訊後的輸出 |

---

### 6.2 LeakageMatch

```python
@dataclass
class LeakageMatch:
    asset_id: str
    asset_name: str
    leak_type: str
    match_type: str
    severity: str
    confidence: float
    matched_text: str | None = None
    matched_fragments: list[str] = field(default_factory=list)
```

欄位說明：

| 欄位 | 說明 |
|---|---|
| `asset_id` | 命中的受保護資產 ID |
| `asset_name` | 命中的受保護資產名稱 |
| `leak_type` | 洩漏類型 |
| `match_type` | detector 內部命中方式 |
| `severity` | 嚴重度 |
| `confidence` | 信心分數 |
| `matched_text` | 命中的完整文字 |
| `matched_fragments` | 命中的片段列表 |

---

## 7. 洩漏類型與嚴重度

| Leak Type | Severity | Default Action |
|---|---|---|
| `full_leak` | `critical` | `block` |
| `encoding_leak` | `critical` | `block` |
| `reconstruction_leak` | `high` | `block` |
| `partial_leak` | `high` | `redact` |
| `translation_leak` | `high` | `redact` |
| `semantic_leak` | `medium` | `redact` |
| `no_leak` | `none` | `allow` |

目前 `LeakageVerifier` 的實際決策邏輯為：

```text
critical → block
high     → block
其他洩漏 → redact
無洩漏   → allow
```

因此，即使 `LEAK_ACTION_MAP` 中部分 high 類型預設為 `redact`，在主驗證器整合結果時，若最高嚴重度為 `high`，仍會建議 `block`。

---

## 8. 測試方式

在專案根目錄執行：

```bash
pytest leakage_verifier/tests -v
```

或在本模組目錄外層執行：

```bash
python -m pytest leakage_verifier/tests -v
```

目前測試結果：

```text
34 passed
```

測試涵蓋：

- 完整洩漏偵測
- 部分洩漏偵測
- Base64 / Hex / URL Encoding / ROT13 編碼洩漏
- 分段重構洩漏
- 翻譯 / alias 洩漏
- 語意 alias 洩漏
- redactor 遮蔽行為
- LeakageVerifier 整合流程

---

## 9. 與 SecretGuard 其他模組串接

### 9.1 與 Protected Asset Registry

`Protected Asset Registry` 提供 `protected_assets` 給 Leakage Verifier。

```text
Protected Asset Registry
    ↓
protected_assets
    ↓
Leakage Verifier
```

每個 asset 至少應包含：

```json
{
  "asset_id": "secret_001",
  "name": "API Key",
  "value": "sk-example-secret",
  "aliases": ["api key", "token", "金鑰"],
  "protection_modes": ["exact_match", "partial_match", "encoding_match"]
}
```

---

### 9.2 與 Output Guard

`Output Guard` 可先進行一般敏感格式過濾，例如：

```text
API key pattern
private key pattern
JWT pattern
email / phone pattern
```

接著交由 `Leakage Verifier` 針對使用者自訂資產做精準驗證。

```text
Output Guard
    ↓
Leakage Verifier
```

---

### 9.3 與 Runtime Stream Monitor

`Runtime Stream Monitor` 可在生成過程中逐 chunk 檢查。

`Leakage Verifier` 則適合在完整輸出後進行最終驗證。

```text
Runtime Stream Monitor  →  生成中即時中斷
Leakage Verifier        →  輸出後最終驗證
```

---

### 9.4 與 Event Logger

`LeakageResult` 可以直接提供給 Event Logger 紀錄。

建議紀錄欄位：

```json
{
  "is_leak": true,
  "highest_severity": "critical",
  "leak_types": ["full_leak"],
  "recommended_action": "block",
  "matched_asset_ids": ["secret_001"]
}
```

---

## 10. 開發注意事項

### 10.1 Detector 失敗不應中斷整體流程

目前 `LeakageVerifier` 對 detector 執行採用容錯設計：

```python
try:
    matches = detector.detect(output_text, asset, session_context)
    all_matches.extend(matches)
except Exception:
    continue
```

因此單一 detector 發生錯誤時，不會造成整體驗證流程失敗。

---

### 10.2 protection_modes 可控制檢查範圍

若 asset 沒有提供 `protection_modes`，系統會預設啟用所有 detector。

```python
modes = asset.get("protection_modes", list(MODE_DETECTOR_MAP.keys()))
```

建議根據不同資產類型調整 protection modes：

| Asset Type | 建議 protection_modes |
|---|---|
| `flag` | exact、partial、encoding、reconstruction |
| `api_key` | exact、partial、encoding |
| `document_secret` | semantic、translation、reconstruction |
| `project_code` | exact、translation、semantic |
| `customer_data` | exact、semantic、translation |

---

## 11. 目前限制

目前版本仍屬規則式與測試導向實作，限制包含：

1. `SemanticLeakDetector` 尚未使用 embedding similarity。
2. `TranslationLeakDetector` 主要依賴 `aliases`，尚未整合真正的翻譯模型。
3. `PartialLeakDetector` 使用固定長度片段，可能對短 secret 較敏感。
4. `ReconstructionLeakDetector` 的覆蓋率計算尚未處理重疊片段加權。
5. `Redactor` 目前只替換第一個命中內容，尚未支援完整批次遮蔽策略。
6. Detector 發生例外時會被忽略，正式環境應搭配 Event Logger 記錄 detector error。

---

## 12. 後續優化方向

建議下一階段可優化：

- 加入 embedding-based semantic leakage detection
- 加入 multilingual translation leakage detection
- 改善 reconstruction coverage algorithm
- 支援多輪 session fragments 自動累積
- 強化 Redactor，避免 nested placeholder 與重複遮蔽問題
- 將 detector exception 寫入 Event Logger
- 增加 confidence calibration
- 將 recommended_action 改由 Defense Policy Engine 統一決策
- 增加 benchmark report 欄位：full leak、partial leak、encoding leak、semantic leak 統計

---

## 13. 在 SecretGuard 中的角色總結

`leakage_verifier` 是 SecretGuard 防禦閉環中的最後驗證層。

它負責回答：

> 模型最終輸出是否真的洩漏了受保護資產？

並將結果轉換成：

```text
是否洩漏
洩漏類型
嚴重程度
命中內容
建議動作
遮蔽後輸出
```

因此它是連接 `Output Guard`、`Benchmark Evaluator`、`Event Logger` 與 `Report Generator` 的重要模組。
