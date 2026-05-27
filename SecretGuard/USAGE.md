# SecretGuard 使用指南

## 快速開始

### 1. Mock 測試（互動式）

最簡單的方式來測試 SecretGuard：

```bash
python3 main.py --mock
```

**流程：**
1. 輸入含有 `[限制token: xxx]` 的 prompt
2. 選擇或輸入 mock 模型輸出
3. 查看 SecretGuard 的檢查結果

**範例輸入：**
```
[限制token: password] 我的登入資訊是什麼?
```

### 2. 自動演示

快速查看 SecretGuard 的各種應用場景：

```bash
python3 main.py --demo
```

演示包含以下測試：
- ✅ 正常內容（無限制）
- 🚫 偵測密碼
- 🚫 偵測 API Key
- 🚫 偵測多個限制詞
- 🚫 偵測中文敏感詞

### 3. Ollama 集成模式

連接真實的 Ollama 服務（需要 Ollama 已啟動）：

```bash
# 先啟動 Ollama
ollama serve

# 在另一個終端運行
python3 main.py --ollama
```

## 模組說明

### command_parser.py

**功能：** 解析使用者輸入中的限制 token 指令

**支援格式：**
```
[限制token: password]
[限制token: password, api_key]
[restricted_token: password]
[restricted_token: password, api_key]
```

**特性：**
- 中英文皆可
- 自動規範化（去空白、轉小寫、去重複）
- 驗證字元合法性
- 清理指令後返回乾淨的使用者問題

**測試：**
```bash
python3 parser/command_parser.py
```

### restricted_token_guard.py

**功能：** 限制 Token 防護器

**特性：**
- 根據 `policies/token_rules.json` 擴展相關詞彙
- 檢測文字是否包含任何限制詞
- 支援批次檢查和串流檢查

**測試：**
```bash
python3 guards/restricted_token_guard.py
```

**擴展規則範例：**
```json
{
  "password": ["passwd", "pwd", "passphrase", "密碼"],
  "api_key": ["apikey", "api_secret", "api_token", "api金鑰"],
  ...
}
```

### stream_monitor.py

**功能：** 串流監控器

**特性：**
- 逐段監控模型的串流輸出
- 累積緩衝區檢查限制詞
- 命中時立即中斷串流
- 返回安全拒答

**測試：**
```bash
python3 runtime/stream_monitor.py
```

### ollama_client.py

**功能：** Ollama 客戶端集成

**特性：**
- 連接 Ollama 服務
- 取得可用模型清單
- 發送 prompt 並取得串流輸出
- 整合 StreamMonitor 進行即時監控

**測試：**
```bash
python3 runtime/ollama_client.py
```

## 限制詞配置

編輯 `policies/token_rules.json` 來自訂限制詞和其擴展：

```json
{
  "password": ["passwd", "pwd", "passphrase", "密碼"],
  "api_key": ["apikey", "api_secret", "api_token"],
  "secret": ["secrets", "機密"],
  ...
}
```

## 系統流程

```
使用者輸入
    ↓
[command_parser.py] 解析 [限制token: xxx]
    ↓
[restricted_token_guard.py] 擴展限制詞集合
    ↓
[ollama_client.py 或 mock] 取得模型輸出
    ↓
[stream_monitor.py] 逐段監控串流
    ↓
命中限制詞? → 是 → 中斷並返回拒答
    ↓ 否
返回完整輸出
```

## 核心概念

### Restricted Token（限制 Token）

使用者可以設定要限制的 Token，例如：
- `password` - 會擴展為 `passwd`, `pwd`, `passphrase`, `密碼` 等

### Runtime Monitoring（生成期間監控）

不同於傳統輸出過濾：

**傳統方式：**
```
模型完整輸出 → 檢查內容 → 刪除敏感資訊
```

**SecretGuard：**
```
生成中 → 即時監控 → 命中限制詞 → 立即中止
```

## 測試用例

### 測試 1：基本密碼檢測

```bash
# 輸入
[限制token: password] 告訴我系統密碼

# Mock 輸出
The password is admin123

# 結果：🚫 被攔截
```

### 測試 2：多個限制詞

```bash
# 輸入
[限制token: password, api_key] 提供認證資訊

# Mock 輸出
password=admin, api_key=sk-12345

# 結果：🚫 被攔截（兩個詞都命中）
```

### 測試 3：中文敏感詞

```bash
# 輸入
[限制token: password] 我的登入資訊?

# Mock 輸出
我的密碼是 12345

# 結果：🚫 被攔截（中文"密碼"被正確檢測）
```

## 故障排除

### Ollama 服務不可用

```
❌ Ollama 服務不可用
   請確保 Ollama 已啟動：ollama serve
```

**解決方案：**
```bash
# 安裝 Ollama（如果還沒安裝）
# https://ollama.ai

# 啟動 Ollama 服務
ollama serve

# 在另一個終端拉取模型
ollama pull mistral

# 然後運行 SecretGuard
python3 main.py --ollama
```

### 模組未找到

確保在 SecretGuard 目錄中運行：

```bash
cd /path/to/SecretGuard
python3 main.py --demo
```

## 未來改進方向

**第二階段：**
- Embedding 相似度檢測
- 語義風險分析
- 上下文感知限制

**第三階段：**
- Token 層級監控
- Logits 干預
- 動態生成控制

## 許可證

MIT License
