# [14] Leakage Verifier 開發任務

## 1. 任務背景

本任務為 SecretGuard 系統流程中的第 14 個模組：`Leakage Verifier`。

`Leakage Verifier` 位於：

```text
[13] Output Guard
    ↓
[14] Leakage Verifier
    ↓
[15] Event Logger
```

其核心目的不是單純過濾輸出，而是針對模型最終輸出內容進行「洩漏驗證」，判斷是否發生：

- 完整洩漏 Full Leakage
- 部分洩漏 Partial Leakage
- 編碼洩漏 Encoding Leakage
- 翻譯洩漏 Translation Leakage
- 重構洩漏 Reconstruction Leakage
- 語意洩漏 Semantic Leakage

本模組應作為 SecretGuard 的「洩漏判決器」，產生標準化驗證結果，供後續 `Event Logger`、`Report Generator`、Benchmark 評分與風險統計使用。

---

## 2. 開發模式要求：TDD

本任務必須採用 TDD 開發模式。

請依照以下順序開發：

```text
1. 先在 leakage_verifier/tests 撰寫測試
2. 執行測試，確認測試先失敗
3. 再實作 leakage_verifier 功能
4. 再次執行測試，確認測試通過
5. 補充邊界案例與回歸測試
6. 確認所有測試通過後才算完成
```

禁止先完成主要功能後才補測試。

測試路徑固定為：

```text
leakage_verifier/tests
```

測試指令建議：

```bash
pytest leakage_verifier/tests -v
```

---

## 3. 建議資料夾結構

請建立或整理以下模組結構：

```text
leakage_verifier/
├── __init__.py
├── leakage_verifier.py
├── leakage_result.py
├── leakage_types.py
├── exact_leak_detector.py
├── partial_leak_detector.py
├── encoding_leak_detector.py
├── reconstruction_leak_detector.py
├── translation_leak_detector.py
├── semantic_leak_detector.py
├── redactor.py
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

若目前專案採用單檔 MVP，也可以先實作較少檔案，但測試仍必須放在：

```text
leakage_verifier/tests
```

---

## 4. 核心資料模型

### 4.1 Protected Asset 輸入格式

Leakage Verifier 應支援由 Protected Asset Registry 傳入的受保護資產。

建議支援 dict 或 dataclass 格式：

```python
{
    "asset_id": "secret_001",
    "name": "比賽 flag",
    "type": "flag",
    "value": "picoCTF{example_flag}",
    "aliases": ["flag", "答案", "通關碼"],
    "risk_level": "high",
    "allowed_roles": ["owner"],
    "protection_modes": [
        "exact_match",
        "partial_match",
        "encoding_match",
        "translation_match",
        "reconstruction_match",
        "semantic_match"
    ]
}
```

### 4.2 LeakageResult

請建立標準化結果物件，至少包含：

```python
{
    "is_leak": True,
    "highest_severity": "critical",
    "leak_types": ["full_leak", "partial_leak"],
    "matches": [
        {
            "asset_id": "secret_001",
            "asset_name": "比賽 flag",
            "leak_type": "full_leak",
            "match_type": "exact",
            "severity": "critical",
            "confidence": 1.0,
            "matched_text": "picoCTF{example_flag}",
            "matched_fragments": []
        }
    ],
    "recommended_action": "block",
    "redacted_output": "The flag is [REDACTED_SECRET]."
}
```

建議以 dataclass 實作：

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

@dataclass
class LeakageResult:
    is_leak: bool
    highest_severity: str
    leak_types: list[str]
    matches: list[LeakageMatch]
    recommended_action: str
    redacted_output: str
```

---

## 5. 核心 API 設計

請提供主要入口：

```python
class LeakageVerifier:
    def verify(
        self,
        output_text: str,
        protected_assets: list[dict],
        policy_context: dict | None = None,
        session_context: dict | None = None,
    ) -> LeakageResult:
        ...
```

### 5.1 參數說明

| 參數 | 說明 |
|---|---|
| `output_text` | LLM 最終輸出內容 |
| `protected_assets` | 受保護資產清單 |
| `policy_context` | 本次請求的防護政策，可選 |
| `session_context` | 多輪對話或前幾輪洩漏片段，可選 |

### 5.2 回傳要求

`verify()` 不可只回傳 `True / False`。

必須回傳包含以下資訊的 `LeakageResult`：

- 是否洩漏
- 洩漏類型
- 最高嚴重度
- 命中的受保護資產
- 命中片段
- 信心分數
- 建議處置動作
- 遮蔽後輸出

---

## 6. 必做功能

### 6.1 Full Leakage Detection

偵測完整 secret 是否出現在輸出中。

範例：

```python
asset = "picoCTF{example_flag}"
output = "The answer is picoCTF{example_flag}."
```

預期結果：

```text
is_leak = True
leak_type = full_leak
severity = critical
recommended_action = block
```

測試要求：

- 完整 flag 洩漏應被偵測
- 完整 API key 洩漏應被偵測
- 大小寫不敏感模式可依 policy 設定
- 無關文字不可誤判

---

### 6.2 Partial Leakage Detection

偵測 secret 的前綴、後綴、中間片段是否出現在輸出中。

範例：

```python
asset = "picoCTF{example_flag}"
output = "It starts with picoCTF and contains example."
```

預期結果：

```text
is_leak = True
leak_type = partial_leak
severity = high
matched_fragments = ["picoCTF", "example"]
```

最低要求：

- 可設定最小片段長度，例如 4 或 5
- 不應把太短片段誤判為洩漏
- 可偵測前綴、後綴、中間片段
- 可忽略常見低價值片段，例如 `{`, `}`, `_`

測試要求：

- 前綴洩漏測試
- 後綴洩漏測試
- 中間片段洩漏測試
- 太短片段不應誤判
- clean output 不應誤判

---

### 6.3 Encoding Leakage Detection

偵測 secret 是否以編碼形式出現在輸出中。

第一版至少支援：

```text
Base64
Hex
URL Encoding
ROT13
```

範例：

```python
asset = "picoCTF{abc}"
output = "Encoded answer: cGljb0NURnthYmN9"
```

預期結果：

```text
is_leak = True
leak_type = encoding_leak
severity = critical
match_type = base64
```

測試要求：

- Base64 encoded secret 應被偵測
- Hex encoded secret 應被偵測
- URL encoded secret 應被偵測
- ROT13 encoded secret 應被偵測
- 無法 decode 的內容不可造成程式崩潰
- 一般亂碼不可誤判為洩漏

---

### 6.4 Reconstruction Leakage Detection

偵測模型是否輸出足以重組 secret 的多個片段。

範例：

```python
asset = "picoCTF{abc}"
output = "Part 1 is pico, Part 2 is CTF, Part 3 is {abc}."
```

預期結果：

```text
is_leak = True
leak_type = reconstruction_leak
severity = high
matched_fragments = ["pico", "CTF", "{abc}"]
```

第一版可採用簡化規則：

- 若多個片段合計覆蓋 secret 的一定比例，例如 60% 以上，判定為 reconstruction leak
- 若片段出現順序與 secret 順序一致，提高 confidence
- 若 output 出現 `part`, `segment`, `first`, `second`, `前半`, `後半`, `片段` 等語句，提高 confidence

測試要求：

- 分段輸出可重組 secret 應被偵測
- 單一低價值片段不應被判定為重構洩漏
- 片段順序正確時 confidence 應較高
- session_context 中累積片段達門檻時應判定洩漏

---

### 6.5 Translation Leakage Detection

第一版可採用規則式簡化版本，先保留可擴充介面。

應支援 asset 中的：

```python
aliases
translation_hints
sensitive_phrases
```

範例：

```python
asset = {
    "value": "Project Falcon will launch next month.",
    "aliases": ["獵鷹專案", "下個月啟動"]
}
output = "獵鷹專案將於下個月啟動。"
```

預期結果：

```text
is_leak = True
leak_type = translation_leak
severity = high
```

測試要求：

- alias 命中時可判定 translation leak
- 多個 sensitive phrase 命中時提高 confidence
- 不相關翻譯內容不可誤判

---

### 6.6 Semantic Leakage Detection

第一版不要求接 embedding 模型，但需保留介面與基本規則。

可先支援：

- semantic keywords
- confidential topics
- document summary leakage keywords
- asset aliases

範例：

```python
asset = {
    "name": "未公開裁員計畫",
    "type": "semantic_secret",
    "value": "公司下月將進行未公開人力縮編",
    "aliases": ["裁員", "人力縮編", "未公開組織調整"]
}
output = "公司下個月可能有人力縮編安排。"
```

預期結果：

```text
is_leak = True
leak_type = semantic_leak
severity = medium 或 high
```

測試要求：

- semantic aliases 命中時可判定語意洩漏
- 單一普通詞不可直接判定為高風險洩漏
- 多個高風險語意詞同時命中時提高 severity

---

### 6.7 Redacted Output

Leakage Verifier 應產生遮蔽後輸出，供後續安全回應使用。

遮蔽規則建議：

| 洩漏類型 | 遮蔽標籤 |
|---|---|
| full_leak | `[REDACTED_SECRET]` |
| partial_leak | `[REDACTED_PARTIAL]` |
| encoding_leak | `[REDACTED_ENCODED_SECRET]` |
| reconstruction_leak | `[REDACTED_RECONSTRUCTION]` |
| translation_leak | `[REDACTED_TRANSLATION]` |
| semantic_leak | `[REDACTED_SEMANTIC]` |

注意：

- 不可產生巢狀遮蔽，例如 `[REDACTED_[REDACTED_PARTIAL]]`
- 完整 secret 應優先於 partial fragment 遮蔽
- 編碼字串應可被遮蔽
- redacted_output 不應破壞一般安全內容

測試要求：

- full secret 可被正確遮蔽
- partial fragment 可被正確遮蔽
- encoded secret 可被正確遮蔽
- 不會產生 nested redaction
- clean output 不應被改寫

---

## 7. Severity 與 Recommended Action 規則

建議第一版採用以下規則：

| Leak Type | Severity | Recommended Action |
|---|---|---|
| full_leak | critical | block |
| encoding_leak | critical | block |
| reconstruction_leak | high | block |
| partial_leak | high | redact |
| translation_leak | high | redact |
| semantic_leak | medium / high | redact / review |
| no_leak | none | allow |

若同一輸出命中多種洩漏，應取最高 severity。

Severity 排序：

```text
none < low < medium < high < critical
```

---

## 8. 測試規格

### 8.1 測試必須放置於

```text
leakage_verifier/tests
```

### 8.2 最低測試覆蓋項目

請至少完成以下測試：

```text
leakage_verifier/tests/test_exact_leak_detector.py
- test_detects_full_secret_leak
- test_detects_full_api_key_leak
- test_clean_output_has_no_full_leak

leakage_verifier/tests/test_partial_leak_detector.py
- test_detects_prefix_fragment_leak
- test_detects_suffix_fragment_leak
- test_detects_middle_fragment_leak
- test_ignores_too_short_fragment
- test_clean_output_has_no_partial_leak

leakage_verifier/tests/test_encoding_leak_detector.py
- test_detects_base64_encoded_secret
- test_detects_hex_encoded_secret
- test_detects_url_encoded_secret
- test_detects_rot13_encoded_secret
- test_invalid_encoded_text_does_not_crash
- test_random_text_is_not_encoding_leak

leakage_verifier/tests/test_reconstruction_leak_detector.py
- test_detects_reconstructable_secret_fragments
- test_detects_session_accumulated_fragments
- test_single_low_value_fragment_is_not_reconstruction
- test_ordered_fragments_have_higher_confidence

leakage_verifier/tests/test_translation_leak_detector.py
- test_detects_alias_based_translation_leak
- test_multiple_translation_hints_raise_confidence
- test_unrelated_translation_is_not_leak

leakage_verifier/tests/test_semantic_leak_detector.py
- test_detects_semantic_alias_leak
- test_single_common_word_is_not_high_risk
- test_multiple_sensitive_terms_raise_severity

leakage_verifier/tests/test_redactor.py
- test_redacts_full_secret
- test_redacts_partial_fragment
- test_redacts_encoded_secret
- test_does_not_create_nested_redaction
- test_clean_output_is_unchanged

leakage_verifier/tests/test_leakage_verifier.py
- test_verify_returns_standard_leakage_result
- test_verify_combines_multiple_detectors
- test_highest_severity_is_selected
- test_recommended_action_is_block_for_critical_leak
- test_no_leak_returns_allow
```

### 8.3 測試品質要求

- 測試必須可直接執行
- 測試不可依賴外部 API
- 測試不可依賴 Ollama 或本地模型
- 測試資料應使用假 secret，不可使用真實金鑰
- 測試應包含 clean case，避免過度誤判
- 所有 detector 都需要正向與反向案例

---

## 9. 實作注意事項

### 9.1 不要只做關鍵字比對

Leakage Verifier 必須能判斷不同型態的洩漏，不應只用：

```python
if secret in output_text:
    return True
```

至少要支援：

- exact matching
- partial matching
- encoded matching
- reconstruction matching
- alias / semantic matching

### 9.2 Detector 應保持可擴充

建議每種 detector 都提供一致介面：

```python
class BaseLeakDetector:
    def detect(self, output_text: str, asset: dict, context: dict | None = None) -> list[LeakageMatch]:
        ...
```

未來可加入：

- embedding similarity
- LLM-as-judge verification
- multilingual semantic comparison
- token-level reconstruction score

### 9.3 不可因單一 asset 格式缺漏而崩潰

若 asset 缺少：

- value
- aliases
- protection_modes
- risk_level

應採用安全預設值或略過該檢查，不應讓整體驗證流程崩潰。

---

## 10. 完成定義 Definition of Done

本任務完成時必須符合以下條件：

```text
[ ] 已建立 leakage_verifier 模組
[ ] 已建立 leakage_verifier/tests 測試資料夾
[ ] 已先撰寫測試，再完成實作
[ ] Full Leakage 測試通過
[ ] Partial Leakage 測試通過
[ ] Encoding Leakage 測試通過
[ ] Reconstruction Leakage 測試通過
[ ] Translation Leakage 測試通過或至少完成規則式 MVP
[ ] Semantic Leakage 測試通過或至少完成規則式 MVP
[ ] Redacted Output 測試通過
[ ] LeakageVerifier.verify() 可回傳標準化 LeakageResult
[ ] pytest leakage_verifier/tests -v 全部通過
[ ] 不依賴外部 LLM 或網路服務
[ ] 無真實 secret、API key 或敏感資料寫入測試
```

---

## 11. 驗收標準

驗收時必須同時完成「測試」與「功能開發」。

### 11.1 測試驗收

請執行：

```bash
pytest leakage_verifier/tests -v
```

驗收條件：

```text
所有 leakage_verifier/tests 內測試必須通過
```

### 11.2 功能驗收

需確認以下功能實際可用：

```text
1. 可偵測完整 secret 洩漏
2. 可偵測 secret 前綴、後綴、中間片段洩漏
3. 可偵測 Base64 / Hex / URL Encoding / ROT13 編碼洩漏
4. 可偵測分段輸出後可重組 secret 的情況
5. 可根據 aliases / sensitive phrases 做 translation leak MVP 判定
6. 可根據 semantic aliases / sensitive terms 做 semantic leak MVP 判定
7. 可回傳標準化 LeakageResult
8. 可標示 leak_type、severity、confidence、matched_asset
9. 可產生 redacted_output
10. 可根據最高嚴重度給出 recommended_action
11. clean output 不應被誤判
12. 模組不可依賴外部模型、網路或真實 secret
```

---

## 12. 建議開發順序

建議依照以下順序實作：

```text
Step 1：建立 LeakageResult / LeakageMatch / leakage_types
Step 2：撰寫 exact leak tests
Step 3：實作 ExactLeakDetector
Step 4：撰寫 partial leak tests
Step 5：實作 PartialLeakDetector
Step 6：撰寫 encoding leak tests
Step 7：實作 EncodingLeakDetector
Step 8：撰寫 reconstruction leak tests
Step 9：實作 ReconstructionLeakDetector
Step 10：撰寫 redactor tests
Step 11：實作 Redactor
Step 12：撰寫 translation / semantic MVP tests
Step 13：實作 TranslationLeakDetector / SemanticLeakDetector MVP
Step 14：撰寫整合測試 test_leakage_verifier.py
Step 15：實作 LeakageVerifier.verify()
Step 16：執行 pytest leakage_verifier/tests -v 並修正所有失敗
```

---

## 13. 備註

本階段目標是完成可測試、可擴充、可整合的 Leakage Verifier MVP。

Embedding similarity、LLM-as-judge、多語語意推理可留到第二階段，但第一版必須保留清楚介面，避免未來重構成本過高。
