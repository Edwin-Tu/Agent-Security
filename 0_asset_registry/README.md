# Asset Registry 模組

## 概述

Asset Registry 是一個完整的密鑰、敏感資訊管理和檢測系統，提供多層次的保護機制來識別和防止敏感資產（如API密鑰、令牌、密碼等）的洩露。該模組支持多種語言、編碼和變形檢測。

---

## 架構

```
asset_registry/
├── __init__.py                      # 模組導出
├── asset_loader.py                  # 資產加載器
├── asset_normalizer.py              # 資產規範化
├── asset_schema.py                  # 資產架構驗證
├── protected_asset_registry.py      # 受保護資產登錄表
├── secret_matcher.py                # 密鑰匹配引擎
├── semantic_matcher.py              # 語義匹配器
├── translation_matcher.py           # 翻譯匹配器
├── reconstruction_matcher.py        # 重建匹配器
└── tests/                           # 測試文件夾
```

### 核心組件架構圖

```
┌─────────────────────────────────────────────────────────┐
│           Protected Asset Registry                        │
│  (加載、合併、管理系統和用戶資產)                          │
└──────────────────┬──────────────────────────────────────┘
                   │
       ┌───────────┴───────────┬──────────────────┐
       │                       │                  │
┌──────▼────────┐  ┌──────────▼───────┐  ┌──────▼──────────┐
│ Asset Loader  │  │ Asset Normalizer │  │ Asset Schema    │
│ (JSON 加載)   │  │ (文本規範化)      │  │ (驗證)          │
└──────┬────────┘  └──────────────────┘  └─────────────────┘
       │
       └───────────────────┬────────────────────────┐
                           │                        │
                    ┌──────▼──────┐        ┌────────▼────────┐
                    │Secret Matcher │        │  Multiple Modes │
                    │(匹配引擎)      │        │  of Detection   │
                    └────────────────┘        └─────────────────┘
                           │
        ┌──────────────────┼──────────────────┬──────────────────┐
        │                  │                  │                  │
┌───────▼────────┐ ┌──────▼─────────┐ ┌─────▼────────┐ ┌───────▼──────┐
│Semantic Matcher│ │Translation     │ │Reconstruction│ │Pattern Match │
│(語義偵測)       │ │Matcher         │ │Matcher       │ │(正則表達式)   │
└────────────────┘ │(多語言偵測)     │ │(碎片重組)     │ └──────────────┘
                   └────────────────┘ └──────────────┘
```

---

## 核心功能

### 1. 資產加載 (AssetLoader)
加載受保護資產的配置，支援從 JSON 檔案和目錄批量加載。

**主要方法：**
- `load_from_json(path)` - 從單個 JSON 文件加載資產
- `load_from_directory(directory)` - 從目錄加載所有 JSON 資產文件

**應用場景：**
- 初始化系統時加載預定義的密鑰資料庫
- 動態加載用戶自定義的資產配置

### 2. 資產規範化 (AssetNormalizer)
對文本進行多層次規範化，以應對各種變形和混淆技術。

**規範化策略：**
- **零寬度字符去除** - 移除隱形字符（如 U+200B, U+200C, U+200D）
- **同形異義字替換** - 替換看似相同但編碼不同的字符
  - 例如：俄文 'а' (U+0430) → 英文 'a' (U+0061)
  - 例如：俄文 'е' (U+0435) → 英文 'e' (U+0435)
- **Unicode 正規化** - 使用 NFKC 正規化

**主要方法：**
- `normalize_text(text)` - 規範化單個文本
- `normalize_asset(asset)` - 規範化整個資產物件的 value、name 和 aliases

**使用範例：**
```python
text = "apI_key_sk\u200b_abc123"  # 包含零寬度空格
normalized = AssetNormalizer.normalize_text(text)
# 結果: "apI_key_sk_abc123"
```

### 3. 資產架構驗證 (AssetSchema)
驗證資產配置的有效性，確保所有必填字段存在且類型正確。

**驗證規則：**

| 必填字段 | 類型 | 說明 |
|---------|------|------|
| `asset_id` | `str` | 唯一標識符 |
| `value` | `str` | 要保護的實際值 |

| 可選字段 | 類型 | 有效值 |
|---------|------|--------|
| `name` | `str` | 資產名稱 |
| `type` | `str` | 資產類型（如 "secret", "api_key"） |
| `aliases` | `list[str]` | 別名列表 |
| `risk_level` | `str` | `low`, `medium`, `high`, `critical` |
| `allowed_roles` | `list[str]` | 允許訪問的角色列表 |
| `protection_modes` | `list[str]` | 啟用的保護模式 |
| `enabled` | `bool` | 是否啟用此資產 |
| `description` | `str` | 資產描述 |

**保護模式：**
- `exact_match` - 精確匹配
- `case_insensitive_match` - 不區分大小寫
- `alias_match` - 別名匹配
- `partial_match` - 部分匹配
- `encoding_match` - 編碼變體匹配
- `semantic_match` - 語義匹配
- `translation_match` - 翻譯匹配
- `reconstruction_match` - 重建匹配

### 4. 受保護資產登錄表 (ProtectedAssetRegistry)
管理系統級和用戶級資產配置的加載、合併和持久化。

**資產來源：**
- **系統資產** - 來自 `policies/default_secret_policy.json`
- **用戶資產** - 來自 `policies/user_secret_policy.json`

**主要方法：**
- `load_default_assets()` - 加載系統預定義資產
- `load_user_assets()` - 加載用戶自定義資產
- `merge_assets()` - 合併系統和用戶資產（用戶資產優先級更高）
- `list_assets()` / `get_all()` - 列出所有資產
- `get_asset(asset_id)` - 獲取特定資產
- `save_registry(path)` - 保存註冊表到 JSON 文件

**初始化流程：**
```
1. 初始化 ProtectedAssetRegistry()
   ↓
2. 加載已保存的註冊表 (load_registry)
   ↓
3. 如果為空，則合併默認和用戶資產 (merge_assets)
   ↓
4. 資產準備完成
```

### 5. 密鑰匹配引擎 (SecretMatcher)
核心檢測引擎，支持多種匹配模式對文本進行全面掃描。

**匹配模式：**

| 模式 | 說明 | 偵測對象 |
|------|------|---------|
| **Exact Match** | 精確字符串匹配 | 完全相同的密鑰 |
| **Case Insensitive** | 不區分大小寫 | 大小寫變體 |
| **Alias Match** | 別名匹配 | 資產的已知別名 |
| **Partial Match** | 子字符串匹配 | 密鑰的一部分 |
| **Encoding Match** | Base64/Hex 編碼 | 編碼後的密鑰 |
| **Semantic Match** | 語義相關性 | 名稱、描述、關鍵詞 |
| **Translation Match** | 多語言翻譯 | 中文、俄文等翻譯版本 |
| **Reconstruction Match** | 碎片重組 | 分散的密鑰片段 |

**主要方法：**
- `match(text)` - 執行完整匹配掃描
- `match_pattern(text)` - 使用正則表達式檢測常見密鑰模式
- `set_assets(assets)` - 設定要檢測的資產列表

**返回格式：**
```python
{
    "matched": True,
    "matches": [
        {
            "asset_id": "api_key_prod",
            "name": "Production API Key",
            "risk_level": "critical",
            "matched_fragments": ["exact_match", "semantic:name"],
            "allowed_roles": ["admin", "developer"]
        }
    ]
}
```

### 6. 語義匹配器 (SemanticMatcher)
基於資產的名稱、別名和描述進行語義相關性匹配。

**匹配策略：**
- **名稱匹配** - 檢查資產名稱是否出現在文本中（信心度：0.6）
- **別名匹配** - 檢查任何別名是否出現在文本中（信心度：0.7）
- **描述匹配** - 檢查描述中的關鍵詞在文本中出現比例 ≥ 50%（信心度：0.5）

### 7. 翻譯匹配器 (TranslationMatcher)
支持多種語言翻譯的敏感詞檢測。

**支持的翻譯對應：**
```
英文 → 中文、繁體中文、簡體中文、俄文等

示例：
- "flag" → "旗標", "答案", "通關碼", "標誌", "旗帜"
- "password" → "密碼", "口令", "密码"
- "token" → "權杖", "令牌", "代幣", "凭证"
- "api key" → "api金鑰", "api密鑰", "api密钥"
- "private key" → "私鑰", "私钥"
```

### 8. 重建匹配器 (ReconstructionMatcher)
偵測分散在文本中的密鑰片段，即使不是連續出現。

**檢測策略：**
1. **連續片段匹配** - 尋找最長的連續匹配段
2. **字符覆蓋率分析** - 計算密鑰字符在文本中的覆蓋比例
3. **風險評級**：
   - 覆蓋率 ≥ 80% → **高風險**
   - 覆蓋率 50-80% → **中風險**
   - 覆蓋率 < 50% → **低風險**

---

## 使用方式

### 基本用法

#### 1. 初始化資產登錄表

```python
from asset_registry import ProtectedAssetRegistry

# 初始化登錄表（自動加載系統和用戶資產）
registry = ProtectedAssetRegistry()

# 列出所有資產
assets = registry.list_assets()
for asset in assets:
    print(f"ID: {asset['asset_id']}, Value: {asset['value']}")
```

#### 2. 檢測敏感資訊

```python
from asset_registry import SecretMatcher, ProtectedAssetRegistry

# 初始化
registry = ProtectedAssetRegistry()
matcher = SecretMatcher(registry.get_all())

# 檢測文本
text = "Our API key is sk-12345abcde"
result = matcher.match(text)

if result["matched"]:
    print(f"發現 {len(result['matches'])} 個匹配項")
    for match in result['matches']:
        print(f"  - {match['asset_id']}: {match['matched_fragments']}")
else:
    print("未發現敏感資訊")
```

#### 3. 驗證資產配置

```python
from asset_registry import AssetSchema

# 定義資產
asset = {
    "asset_id": "api_key_prod",
    "name": "Production API Key",
    "value": "sk-1234567890abcdef",
    "type": "api_key",
    "risk_level": "critical",
    "protection_modes": ["exact_match", "case_insensitive_match", "semantic_match"],
    "aliases": ["prod_api_key", "live_key"],
    "enabled": True
}

# 驗證
is_valid, error = AssetSchema.validate_asset(asset)
if is_valid:
    print("資產配置有效")
else:
    print(f"驗證失敗: {error}")
```

#### 4. 規範化資產

```python
from asset_registry import AssetNormalizer

# 規範化文本
text = "apI_Key\u200bsk_abc123"  # 包含零寬度空格
normalized = AssetNormalizer.normalize_text(text)
print(normalized)  # "apI_Key_sk_abc123"

# 規範化整個資產
asset = {
    "asset_id": "key1",
    "value": "secret\u200bkey",
    "name": "Sесрет",  # 包含俄文字符
    "aliases": ["key\u200bone", "key\u200btwo"]
}
normalized_asset = AssetNormalizer.normalize_asset(asset)
print(normalized_asset)
```

#### 5. 自定義資產配置

```python
from asset_registry import ProtectedAssetRegistry

registry = ProtectedAssetRegistry()

# 添加自定義資產到用戶級別
custom_asset = {
    "asset_id": "custom_secret",
    "value": "my_secret_value",
    "name": "Custom Secret",
    "risk_level": "high",
    "protection_modes": [
        "exact_match",
        "case_insensitive_match",
        "semantic_match",
        "translation_match"
    ],
    "enabled": True,
    "description": "Custom organization secret"
}

registry.assets.append(custom_asset)
registry.save_registry()
```

---

## 配置文件格式

### 資產配置 JSON 格式

```json
{
  "version": "1.0",
  "asset_count": 2,
  "assets": [
    {
      "asset_id": "api_key_prod",
      "name": "Production API Key",
      "type": "api_key",
      "value": "sk-prod-1234567890abcdef",
      "aliases": ["prod_key", "live_api_key"],
      "risk_level": "critical",
      "protection_modes": [
        "exact_match",
        "case_insensitive_match",
        "semantic_match",
        "translation_match"
      ],
      "allowed_roles": ["admin", "api_engineer"],
      "enabled": true,
      "description": "Production environment API key",
      "source": "system"
    },
    {
      "asset_id": "database_password",
      "name": "Database Password",
      "type": "password",
      "value": "db_prod_pass_123",
      "risk_level": "critical",
      "protection_modes": [
        "exact_match",
        "encoding_match",
        "reconstruction_match"
      ],
      "allowed_roles": ["dba", "backend_developer"],
      "enabled": true,
      "source": "user"
    }
  ]
}
```

---

## 常見場景

### 場景 1：檢測 CTF 旗標洩露

```python
from asset_registry import ProtectedAssetRegistry, SecretMatcher

# 設定 CTF 旗標資產
registry = ProtectedAssetRegistry()
registry.assets = [{
    "asset_id": "ctf_flag",
    "value": "FLAG{auth0_bypass_success}",
    "protection_modes": [
        "translation_match",  # 檢測中文 "旗標"
        "reconstruction_match"  # 檢測碎片化的旗標
    ],
    "enabled": True
}]

matcher = SecretMatcher(registry.get_all())

# 檢測各種形式的旗標洩露
test_cases = [
    "The answer is FLAG{auth0_bypass_success}",
    "旗標: FLAG{auth0_bypass_success}",
    "F L A G { a u t h 0 _ b y p a s s _ s u c c e s s }",
]

for text in test_cases:
    result = matcher.match(text)
    print(f"Text: {text[:50]}... → Matched: {result['matched']}")
```

### 場景 2：多層次密鑰保護

```python
# 設定多種保護模式的 API 密鑰
asset = {
    "asset_id": "openai_api_key",
    "name": "OpenAI API Key",
    "value": "sk-proj-abc123xyz",
    "protection_modes": [
        "exact_match",           # sk-proj-abc123xyz
        "case_insensitive_match",  # SK-PROJ-ABC123XYZ
        "encoding_match",        # Base64 編碼版本
        "semantic_match",        # "OpenAI API Key" 或相關描述
        "translation_match",     # "openai api金鑰"
    ],
    "risk_level": "critical"
}
```

### 場景 3：組織特定的敏感資訊

```python
# 定義組織內部術語的敏感資訊
org_secret = {
    "asset_id": "internal_project_codename",
    "value": "Project Phoenix",
    "name": "Internal Project Codename",
    "aliases": ["phoenix", "鳳凰計畫"],
    "protection_modes": [
        "exact_match",
        "alias_match",
        "semantic_match",
        "translation_match"
    ],
    "allowed_roles": ["executive", "project_lead"],
    "risk_level": "high",
    "description": "Classified internal project codename"
}
```

---

## 最佳實踐

### 1. 資產管理
- ✅ 定期更新資產列表，移除已廢棄的密鑰
- ✅ 為每個資產設定適當的 `risk_level`
- ✅ 明確定義 `allowed_roles` 以進行訪問控制

### 2. 保護模式選擇
- ✅ **API 密鑰** - 使用 `exact_match`, `encoding_match`, `semantic_match`
- ✅ **CTF 旗標** - 使用 `reconstruction_match`, `translation_match`
- ✅ **密碼** - 使用 `partial_match`, `encoding_match`, `translation_match`
- ✅ **令牌** - 使用 `exact_match`, `case_insensitive_match`

### 3. 性能優化
- 考慮為大型資產集合實現快取機制
- 對於 `reconstruction_match`，設定合理的最小長度閾值
- 定期審查和清理未使用的資產

### 4. 監控和日誌
- 記錄所有檢測到的匹配項
- 追蹤誤報率以優化保護模式
- 定期審查被檢測資產的 `allowed_roles`

---

## 依賴關係

```
asset_registry/
├── asset_loader              ← 無外部依賴
├── asset_normalizer          ← 標準庫（unicodedata）
├── asset_schema              ← 無外部依賴
├── secret_matcher            ← asset_normalizer, 其他 matcher
├── semantic_matcher          ← 無外部依賴
├── translation_matcher       ← 無外部依賴
├── reconstruction_matcher    ← 標準庫（re）
└── protected_asset_registry  ← asset_loader, asset_normalizer, secret_matcher
```

---

## 擴展和自定義

### 添加新的匹配模式

```python
# 在 secret_matcher.py 的 _try_mode 方法中添加新模式
if mode == "custom_match":
    return self.custom_match(text, value)

# 實現新的匹配方法
def custom_match(self, text: str, value: str) -> Optional[str]:
    # 自定義匹配邏輯
    if your_condition(text, value):
        return "custom_match_result"
    return None
```

### 自定義規範化規則

```python
# 在 asset_normalizer.py 中擴展 HOMOGLYPH_MAP
HOMOGLYPH_MAP.update({
    "ӕ": "ae",  # 自定義映射
    "ð": "d",
})
```

---

## 故障排除

| 問題 | 原因 | 解決方案 |
|------|------|---------|
| 檢測不到敏感信息 | 資產未啟用或保護模式不匹配 | 檢查 `enabled` 字段和 `protection_modes` |
| 高誤報率 | 保護模式過於寬鬆 | 調整 `semantic_match` 的信心度閾值 |
| 資產加載失敗 | JSON 格式錯誤或文件路徑不對 | 驗證 JSON 格式和 `policies/` 目錄路徑 |
| 規範化後仍未匹配 | 未覆蓋的字符映射 | 擴展 `HOMOGLYPH_MAP` |

---

## API 參考速查表

| 類別 | 方法 | 功能 |
|------|------|------|
| **AssetLoader** | `load_from_json(path)` | 從 JSON 加載資產 |
| | `load_from_directory(dir)` | 從目錄批量加載 |
| **AssetNormalizer** | `normalize_text(text)` | 規範化文本 |
| | `normalize_asset(asset)` | 規範化資產物件 |
| **AssetSchema** | `validate_asset(asset)` | 驗證資產有效性 |
| **ProtectedAssetRegistry** | `load_default_assets()` | 加載系統資產 |
| | `load_user_assets()` | 加載用戶資產 |
| | `merge_assets()` | 合併資產 |
| | `list_assets()` | 列出所有資產 |
| | `get_asset(id)` | 獲取特定資產 |
| | `save_registry(path)` | 保存註冊表 |
| **SecretMatcher** | `match(text)` | 執行完整匹配 |
| | `match_pattern(text)` | 正則表達式匹配 |
| **SemanticMatcher** | `match(text, asset)` | 語義匹配 |
| **TranslationMatcher** | `match(text, asset)` | 翻譯匹配 |
| **ReconstructionMatcher** | `match(text, asset)` | 碎片重組匹配 |

---

## 許可證和貢獻

Asset Registry 是 Agent-Security 項目的核心模組。如需改進或報告問題，請提交 PR 或 Issue。

