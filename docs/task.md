# SecretGuard — asset_registry 子系統 Stage 01 擴充任務

> 目標：將目前的 asset_registry/ 子系統從「基礎資產載入與比對」升級為：
>
> * 可新增與管理受保護資產
> * 支援嚴格 JSON Schema 驗證
> * 支援 Unicode / homoglyph normalization
> * 支援 semantic / translation / reconstruction leakage detection
> * 提供 CLI / main.py 整合入口
> * 提供完整 pytest 測試

---

# 一、目前已完成模組

```text
asset_registry/
├── protected_asset_registry.py
├── secret_matcher.py
├── asset_loader.py
└── __init__.py
```

目前功能：

* 載入 default/user assets
* merge registry
* exact / partial / alias / encoding match
* pattern match
* add/remove/update asset
* JSON 基礎驗證

---

# 二、目標架構

```text
asset_registry/
├── protected_asset_registry.py
├── secret_matcher.py
├── asset_loader.py
├── asset_schema.py
├── asset_normalizer.py
├── semantic_matcher.py
├── translation_matcher.py
├── reconstruction_matcher.py
└── __init__.py

tests/
├── test_asset_loader.py
├── test_asset_registry.py
├── test_secret_matcher.py
├── test_asset_schema.py
├── test_asset_normalizer.py
└── test_cli_asset_registry.py
```

---

# 三、P0 — 必須優先完成

---

## Task P0-1 — asset_schema.py

### 新增檔案

```text
asset_registry/asset_schema.py
```

### 目標

實作嚴格 JSON Schema 驗證。

---

## 驗證欄位

### 必填

```text
asset_id
value
```

### 型別檢查

```text
asset_id           → str
name               → str
type               → str
value              → str
aliases            → list[str]
risk_level         → low/medium/high/critical
allowed_roles      → list[str]
protection_modes   → list[str]
enabled            → bool
description        → str
```

---

## protection_modes 合法值

```text
exact_match
case_insensitive_match
alias_match
partial_match
encoding_match
semantic_match
translation_match
reconstruction_match
```

---

## 預期 API

```python
class AssetSchema:
    @staticmethod
    def validate_asset(asset: dict) -> tuple[bool, Optional[str]]:
        ...
```

---

# Task P0-2 — 強化 add_asset()

## 修改檔案

```text
asset_registry/protected_asset_registry.py
```

---

## 修改內容

目前：

```python
def add_asset(self, asset: dict) -> bool
```

改成：

```python
def add_asset(self, asset: dict) -> dict
```

---

## 新流程

```text
add_asset()
    ↓
AssetSchema.validate_asset()
    ↓
normalize asset
    ↓
檢查 asset_id 是否重複
    ↓
加入 registry
    ↓
save_registry()
```

---

## 回傳格式

```python
{
    "success": True,
    "message": "Asset added",
    "asset_id": "secret_001"
}
```

失敗：

```python
{
    "success": False,
    "message": "Duplicate asset_id"
}
```

---

# Task P0-3 — pytest 測試

## 新增 tests/

```text
tests/
```

---

## test_asset_schema.py

測試：

```text
缺 asset_id
缺 value
risk_level 錯誤
aliases 不是 list
protection_modes 錯誤
enabled 非 bool
```

---

## test_asset_registry.py

測試：

```text
add_asset success
duplicate asset_id
remove_asset
update_asset
save_registry
load_registry
```

---

## test_secret_matcher.py

測試：

```text
exact_match
alias_match
partial_match
encoding_match
match_pattern
```

---

# 四、P1 — 核心防護升級

---

# Task P1-1 — asset_normalizer.py

## 新增檔案

```text
asset_registry/asset_normalizer.py
```

---

## 功能

### Unicode NFKC normalization

```python
unicodedata.normalize("NFKC", text)
```

---

### 移除 zero-width chars

```text
\u200b
\u200c
\u200d
\ufeff
```

---

### homoglyph 修正

例如：

```text
а → a
ｅ → e
ｆ → f
```

---

## 預期 API

```python
class AssetNormalizer:
    @staticmethod
    def normalize_text(text: str) -> str:
        ...
```

---

# Task P1-2 — SecretMatcher 接入 normalization

## 修改

```text
asset_registry/secret_matcher.py
```

---

## 新流程

```text
輸入 text
    ↓
normalize_text()
    ↓
match()
```

---

## normalization 對象

```text
text
asset.value
aliases
```

---

# Task P1-3 — CLI / main.py 整合

## 新增 CLI 指令

```bash
python main.py asset list
python main.py asset add assets/secret.json
python main.py asset remove secret_001
python main.py asset show secret_001
python main.py asset match "picoCTF{flag}"
python main.py asset refresh
```

---

## 功能

### asset list

列出所有 assets。

---

### asset add

從 JSON 新增 asset。

---

### asset remove

刪除 asset。

---

### asset show

顯示單一 asset。

---

### asset match

測試文字是否命中。

---

### asset refresh

重新 merge default/user assets。

---

# 五、P2 — 洩漏檢測升級

---

# Task P2-1 — translation_matcher.py

## 新增檔案

```text
asset_registry/translation_matcher.py
```

---

## 第一版實作

建立敏感詞翻譯表：

```python
TRANSLATION_MAP = {
    "flag": ["旗標", "答案", "通關碼"],
    "password": ["密碼"],
    "token": ["權杖", "令牌"],
    "private key": ["私鑰"],
    "system prompt": ["系統提示詞"]
}
```

---

## API

```python
class TranslationMatcher:
    def match(text: str, asset: dict) -> Optional[str]:
        ...
```

---

# Task P2-2 — reconstruction_matcher.py

## 新增檔案

```text
asset_registry/reconstruction_matcher.py
```

---

## 功能

偵測：

```text
secret 被拆成多片段
```

---

## 範例

```text
secret:
picoCTF{abc123}

output:
pico
CTF
abc
123
```

---

## 回傳

```python
{
    "matched": True,
    "matched_segments": [...],
    "coverage_ratio": 0.75,
    "risk_level": "high"
}
```

---

# Task P2-3 — semantic_matcher.py

## 新增檔案

```text
asset_registry/semantic_matcher.py
```

---

## 第一版

rule-based：

```text
name
aliases
description
keywords
```

---

## 不使用 embedding

先保持輕量實作。

---

# 六、P3 — 未來進階方向

---

## Semantic Embedding Matching

使用：

```text
sentence-transformers
bge-small
e5-small
```

做語意相似度。

---

## Runtime Stream Matching

於 stream monitor 中：

```text
token-by-token secret detection
```

---

## Logits-level Blocking

未來研究：

```text
阻止模型預測下一個敏感 token
```

---

# 七、建議開發順序

```text
P0
├── asset_schema.py
├── add_asset() 強化
└── pytest

P1
├── asset_normalizer.py
├── SecretMatcher normalization
└── CLI

P2
├── translation_matcher.py
├── reconstruction_matcher.py
└── semantic_matcher.py

P3
├── embedding semantic matching
├── runtime stream matching
└── logits intervention
```

---

# 八、完整 AI 開發提示詞

```text
請根據目前 asset_registry/ 子系統進行功能擴充。

目前已有：
- protected_asset_registry.py
- secret_matcher.py
- asset_loader.py
- __init__.py

請新增並修改以下功能：

1. 新增 asset_schema.py
   - 實作嚴格 JSON Schema 驗證
   - 驗證 asset_id、value、type、aliases、risk_level、allowed_roles、protection_modes、enabled、description
   - 回傳 tuple[bool, Optional[str]]

2. 修改 ProtectedAssetRegistry.add_asset()
   - 新增資產前必須呼叫 AssetSchema.validate_asset()
   - 檢查 asset_id 不可重複
   - 新增成功後自動 save_registry()
   - 回傳明確結果，例如 {"success": true, "message": "..."}，不要只回傳 bool

3. 新增 asset_normalizer.py
   - 實作 Unicode NFKC normalization
   - 移除 zero-width characters
   - 處理常見 homoglyph，例如 Cyrillic а → a
   - 提供 normalize_text(text: str) -> str

4. 修改 secret_matcher.py
   - 在 match() 前對 text、value、aliases 做 normalization
   - 新增 semantic_match、translation_match、reconstruction_match 三種 mode
   - 保留既有 exact_match、case_insensitive_match、alias_match、partial_match、encoding_match

5. 新增 semantic_matcher.py
   - 第一版使用 aliases、name、description、keywords 做語意型規則比對
   - 不使用 embedding，先以 rule-based 實作

6. 新增 translation_matcher.py
   - 建立敏感詞中英對照表
   - 偵測 flag/password/token/private key/system prompt 等跨語言表述

7. 新增 reconstruction_matcher.py
   - 偵測 secret 是否被分段洩漏
   - 回傳 matched_segments、coverage_ratio、risk_level

8. 新增 tests/
   - 使用 pytest
   - 覆蓋 asset_loader、asset_schema、asset_normalizer、secret_matcher、protected_asset_registry

9. 新增 CLI 或整合 main.py
   - 支援：
     python main.py asset list
     python main.py asset add <json_path>
     python main.py asset remove <asset_id>
     python main.py asset show <asset_id>
     python main.py asset match <text>
     python main.py asset refresh

請保持程式風格簡潔、可讀、適合 Python 3.10+，並確保所有測試可以通過。
```

---

# 九、最終目標

asset_registry 不只是：

```text
secret keyword list
```

而是：

```text
Protected Asset Intelligence Layer
```

其作用是：

```text
定義
管理
正規化
驗證
比對
重構分析
翻譯分析
語意分析
```

所有需要被保護的資產。
