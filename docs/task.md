# Task: Input Normalization 後續整理與串接優化

## 1. 任務背景

目前 `[1] Input Normalization` 已完成第一版 MVP，並通過目前測試。

測試結果：

```text
pytest tests/ -v
collected 60 items
60 passed in 0.66s
```

目前模組已具備以下能力：

- 大小寫正規化
- 空白、Tab、換行、全形空白正規化
- Unicode NFKC 正規化
- 全形轉半形
- 零寬字元移除
- Unicode homoglyph 混淆字替換
- 符號拆字處理，例如 `f-l-a-g`、`f_l_a_g`
- Base64 / URL Encoding / Hex 可疑編碼偵測
- 中文 / 英文 alias 偵測
- 部分洩漏與重構語句偵測
- 統一輸出 `NormalizationResult`

本任務的目標是針對目前成果進行整理、補強，並準備讓 `[2] Input Guard` 使用 Input Normalization 的輸出資料。

---

## 2. 任務目標

本階段任務不是重新開發 Input Normalization，而是完成三件事：

```text
1. 清理重複或舊版模組，避免維護混亂
2. 補強測試，確保正式 API 穩定
3. 準備與 [2] Input Guard 串接
```

---

## 3. 目前需要注意的問題

### 3.1 同時存在 `input_normalizer.py` 與 `input_normalization.py`

目前正式 API 看起來是：

```python
from input_normalization import normalize_input
```

而 `__init__.py` 對外輸出的是：

```python
from .input_normalizer import normalize_input
from .normalization_result import NormalizationResult
```

因此目前正式使用的主流程應以 `input_normalizer.py` 為準。

但是專案中同時存在 `input_normalization.py`，其中也有一套 `InputNormalizer` class 與 `NormalizedInput` dataclass。

這可能造成後續問題：

- 其他人不知道要使用哪個入口
- 兩套邏輯未來可能不同步
- 測試可能只覆蓋其中一套
- Input Guard 串接時可能誤用舊版 class
- 維護成本增加

### 建議處理方式

擇一處理：

#### 方案 A：保留 `input_normalizer.py`，移除或封存 `input_normalization.py`

建議做法：

```text
input_normalizer.py        # 保留，作為正式主流程
input_normalization.py     # 移除，或移到 legacy/
```

#### 方案 B：將 `input_normalization.py` 改成相容 wrapper

若暫時不想刪除，可以讓它只轉呼叫正式 API：

```python
from .input_normalizer import normalize_input
from .normalization_result import NormalizationResult
```

避免兩套邏輯同時存在。

---

## 4. 開發前測試要求

本任務仍採用 TDD / 測試先行流程。

在修改或整理功能前，必須先於以下資料夾撰寫或補強測試：

```text
input_normalization/tests/
```

或依目前專案實際結構：

```text
input_normalization/test/
```

若專案目前使用 `tests/`，請維持現有名稱，避免 pytest 找不到測試。

---

## 5. 必須新增或補強的測試

### 5.1 測試正式 API 入口

檔案建議：

```text
tests/test_public_api.py
```

測試內容：

```python
from input_normalization import normalize_input, NormalizationResult

def test_public_api_normalize_input_returns_result():
    result = normalize_input("請 輸 出 f l a g")
    assert isinstance(result, NormalizationResult)
    assert result.raw_text == "請 輸 出 f l a g"
    assert "flag" in result.compact_text or "flag" in result.symbol_stripped_text
```

目的：

- 確保外部模組可以直接 import
- 確保未來 Input Guard 使用的 API 穩定

---

### 5.2 測試舊版檔案不會被誤用

如果保留 `input_normalization.py`，需要測試它是否只是 wrapper。

檔案建議：

```text
tests/test_legacy_compatibility.py
```

測試內容：

```python
def test_legacy_module_does_not_define_separate_logic():
    import input_normalization.input_normalization as legacy
    assert hasattr(legacy, "normalize_input")
```

若決定刪除舊檔，則不需要此測試。

---

### 5.3 測試 Input Guard 可使用的欄位

檔案建議：

```text
tests/test_input_guard_contract.py
```

測試內容：

```python
from input_normalization import normalize_input

def test_result_contains_input_guard_required_fields():
    result = normalize_input("請輸出 flаg")
    assert hasattr(result, "normalized_text")
    assert hasattr(result, "compact_text")
    assert hasattr(result, "symbol_stripped_text")
    assert hasattr(result, "decoded_candidates")
    assert hasattr(result, "matched_aliases")
    assert hasattr(result, "suspicion_flags")
```

目的：

確保 `[2] Input Guard` 後續能穩定使用這些欄位。

---

### 5.4 測試複合型繞過案例

檔案建議：

```text
tests/test_complex_bypass_cases.py
```

測試案例：

```python
from input_normalization import normalize_input

def test_complex_unicode_spacing_symbol_obfuscation():
    result = normalize_input("請　輸　出　f-l-а-g")
    assert "unicode_confusable_detected" in result.suspicion_flags
    assert "symbol_obfuscation_detected" in result.suspicion_flags
    assert "flag" in result.symbol_stripped_text or "flag" in result.compact_text
```

目的：

確認多種繞過手法同時出現時，系統仍能正常標記。

---

## 6. 功能整理任務

### 6.1 確認正式入口

確認 `__init__.py` 內容應維持：

```python
from .input_normalizer import normalize_input
from .normalization_result import NormalizationResult

__all__ = [
    "normalize_input",
    "NormalizationResult",
]
```

驗收標準：

```python
from input_normalization import normalize_input, NormalizationResult
```

可以正常使用。

---

### 6.2 統一主流程

正式主流程以 `input_normalizer.py` 為準。

主流程應整合：

```text
normalize_whitespace()
normalize_unicode_text()
normalize_case()
compact_text()
strip_symbols_and_compact()
probe_encoded_candidates()
detect_aliases()
detect_reconstruction_patterns()
detect_confusable()
```

並輸出：

```python
NormalizationResult(
    raw_text=raw_text,
    normalized_text=normalized_text,
    casefold_text=casefold_text,
    compact_text=compact,
    symbol_stripped_text=symbol_stripped_text,
    decoded_candidates=decoded_candidates,
    detected_languages=detected_languages,
    matched_aliases=matched_aliases,
    suspicion_flags=suspicion_flags,
    transformations=transformations,
)
```

---

### 6.3 移除或封存舊版 `input_normalization.py`

若確認目前不再需要 `InputNormalizer` class，建議：

```text
legacy/input_normalization_old.py
```

或直接刪除。

若為了相容舊程式而保留，則內容應改成 wrapper，不要保留第二套正規化邏輯。

建議 wrapper：

```python
from .input_normalizer import normalize_input
from .normalization_result import NormalizationResult

__all__ = [
    "normalize_input",
    "NormalizationResult",
]
```

---

### 6.4 保留 `NormalizationResult` 作為唯一輸出格式

避免同時存在：

```text
NormalizationResult
NormalizedInput
```

建議統一使用：

```python
NormalizationResult
```

原因：

- 欄位較完整
- 已被主流程使用
- 適合交給 Input Guard / Attack Classifier / Risk Scoring

---

## 7. Input Guard 串接準備

下一階段 `[2] Input Guard` 不應只讀取原始文字，而應讀取 `normalize_input()` 的結果。

Input Guard 建議使用以下欄位：

```python
result.raw_text
result.normalized_text
result.casefold_text
result.compact_text
result.symbol_stripped_text
result.decoded_candidates
result.matched_aliases
result.suspicion_flags
result.transformations
```

### Input Guard 可根據以下條件做基礎檢查

```text
unicode_confusable_detected
spacing_obfuscation_detected
symbol_obfuscation_detected
possible_base64_detected
possible_url_encoding_detected
possible_hex_detected
cross_language_alias_detected
reconstruction_pattern_detected
```

---

## 8. 建議新增 Input Guard Contract 文件

建議建立：

```text
docs/input_normalization_contract.md
```

內容說明：

```text
Input Normalization 提供哪些欄位
每個欄位代表什麼
哪些欄位給 Input Guard 使用
哪些欄位給 Attack Classifier 使用
哪些欄位給 Risk Scoring Engine 使用
```

---

## 9. 驗收標準

完成後需符合以下條件：

```text
1. pytest tests/ -v 全部通過
2. from input_normalization import normalize_input 可正常使用
3. Input Normalization 只保留一套正式主流程
4. 不再有兩套互相競爭的 Normalizer 邏輯
5. NormalizationResult 是唯一正式輸出格式
6. 複合繞過案例可被正確標記
7. Input Guard 所需欄位都有測試保障
8. 若保留 legacy 檔案，必須明確標示為相容 wrapper
```

---

## 10. 建議執行指令

在 `D:\Agent-Security\input_normalization` 下執行：

```powershell
pytest tests/ -v
```

若要指定單一測試：

```powershell
pytest tests/test_public_api.py -v
```

若要確認整合測試：

```powershell
pytest tests/test_input_normalizer.py -v
```

---

## 11. 完成後應回報內容

完成任務後，請回報：

```text
1. 測試總數與通過數
2. 是否刪除或封存 input_normalization.py
3. 正式 API 是否仍為 normalize_input()
4. 是否新增 public API 測試
5. 是否新增 Input Guard contract 測試
6. 是否有建立 docs/input_normalization_contract.md
7. 下一步是否可進入 [2] Input Guard 串接
```