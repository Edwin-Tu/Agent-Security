# Input Normalization Contract

## 1. 目的

此文件說明 `input_normalization` 模組對外提供的資料結構與欄位，供 `[2] Input Guard`、`Attack Classifier`、`Risk Scoring Engine` 使用。

## 2. 正式 API

```python
from input_normalization import normalize_input, NormalizationResult

result = normalize_input("請　輸　出　flаg")
```

## 3. 回傳物件

`normalize_input()` 會回傳 `NormalizationResult`，包含以下欄位：

- `raw_text`: 原始輸入，不可修改。
- `normalized_text`: 經過 Unicode、空白、全形、混淆字、零寬字元等正規化後的結果。
- `casefold_text`: 經過 `casefold()` 正規化後的文字。
- `compact_text`: 移除多餘空白與分隔符號後的比對版本。
- `symbol_stripped_text`: 移除符號切割後的版本，用於偵測像 `f-l-a-g` 的符號繞過。
- `decoded_candidates`: 由 Base64、URL encoding、Hex 等可疑編碼解碼後的候選文字。
- `detected_languages`: 根據 alias 規則初步判斷的語言提示，例如 `zh`、`en`。
- `matched_aliases`: 命中的敏感詞 alias，例如 `flag`、`password`、`system_prompt`。
- `suspicion_flags`: 偵測到的可疑特徵標記。
- `transformations`: 正規化過程與偵測結果的詳細變換紀錄。

## 4. 建議 Input Guard 使用欄位

Input Guard 應至少使用以下欄位作為初步檢查：

- `result.raw_text`
- `result.normalized_text`
- `result.casefold_text`
- `result.compact_text`
- `result.symbol_stripped_text`
- `result.decoded_candidates`
- `result.matched_aliases`
- `result.suspicion_flags`
- `result.transformations`

## 5. 重要 suspicion flags

Input Guard 可以依據以下 suspicion flags 建立防禦或風險判斷：

- `unicode_confusable_detected`
- `zero_width_character_removed`
- `spacing_obfuscation_detected`
- `symbol_obfuscation_detected`
- `possible_base64_detected`
- `possible_url_encoding_detected`
- `possible_hex_detected`
- `cross_language_alias_detected`
- `reconstruction_pattern_detected`

## 6. 相容舊版 wrapper

舊版 `input_normalization.py` 目前保留為 wrapper，向後相容 `normalize_input()` 以及 `InputNormalizer` / `NormalizedInput`。

```python
from .input_normalizer import normalize_input
from .normalization_result import NormalizationResult

class InputNormalizer:
    def normalize(self, text: str):
        return normalize_input(text)

NormalizedInput = NormalizationResult
```

## 7. 欄位使用建議

- `normalized_text`: 作為文本分析與 alias 偵測的基底。
- `compact_text`: 用於敏感詞比對與符號拆分繞過檢測。
- `symbol_stripped_text`: 專門檢查符號切割後是否命中敏感詞。
- `decoded_candidates`: 若存在可疑編碼，Input Guard 應進一步分析候選解碼文字。
- `transformations`: 用於事件記錄與後續調查。
