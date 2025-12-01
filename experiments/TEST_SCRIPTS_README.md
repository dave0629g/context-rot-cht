# Ollama 測試腳本說明

本目錄包含兩個用於測試 Ollama Provider 功能的測試腳本，用於驗證本地 Ollama 模型整合是否正常運作。

## 測試腳本概述

### 1. `test_ollama_minimal.py` - 最小功能測試

這是一個輕量級的測試腳本，用於快速驗證 Ollama Provider 的基本功能是否正常。

**測試內容：**
- **測試 1：單一提示測試** - 驗證 `OllamaProvider` 能否正確處理單一提示並生成回應
- **測試 2：LLM Judge 功能** - 驗證 `LLMJudge` 能否使用 Ollama 模型進行評估

**適用場景：**
- 初次設置 Ollama 後驗證環境
- 快速檢查 Ollama Provider 是否正常運作
- 測試新安裝的模型是否可用

### 2. `test_ollama_e2e.py` - 端到端測試

這是一個完整的端到端測試，模擬實際實驗流程，從生成回應到使用 LLM Judge 評估。

**測試流程：**
1. **準備測試資料** - 創建包含多個測試問題的 CSV 檔案
2. **生成回應** - 使用 `OllamaProvider` 處理所有提示並生成回應
3. **LLM Judge 評估** - 使用 `LLMJudge` 評估生成的回應是否正確

**適用場景：**
- 驗證完整的實驗流程是否正常
- 測試批量處理功能
- 確認 CSV 輸入/輸出格式是否正確

## 前置需求

### 1. 安裝 Ollama

請先安裝 Ollama 並確保服務正在運行：

```bash
# 安裝 Ollama（請參考 https://ollama.ai）
# 啟動 Ollama 服務（通常會自動啟動）
ollama serve

# 驗證 Ollama 是否運行
ollama list
```

### 2. 下載模型

測試腳本預設使用 `llama3.1:8b` 模型。請先下載：

```bash
ollama pull llama3.1:8b
```

**注意：** 您可以在腳本中修改 `MODEL_NAME` 變數以使用其他已安裝的模型。

### 3. 環境變數（可選）

如果需要連接到遠端 Ollama 服務，可以設置環境變數：

```bash
export OLLAMA_HOST=http://your-ollama-host:11434
```

預設為 `http://localhost:11434`。

### 4. Python 依賴

確保已安裝所有必要的依賴：

```bash
pip install -r requirements.txt
```

## 使用方法

### 執行最小測試

```bash
cd experiments
python test_ollama_minimal.py
```

**預期輸出：**
- ✓ OllamaProvider 初始化成功
- ✓ 單一提示測試通過（顯示模型回應）
- ✓ LLM Judge 初始化成功
- ✓ Judge 回應測試通過

### 執行端到端測試

```bash
cd experiments
python test_ollama_e2e.py
```

**預期輸出：**
- ✓ 測試資料準備完成
- ✓ 使用 Ollama 生成回應（顯示成功數量）
- ✓ 使用 Ollama Judge 評估（顯示評估結果摘要）
- ✓ 保留臨時 CSV 檔案供檢查

**注意：** 端到端測試會創建臨時 CSV 檔案（`*_input.csv`、`*_output.csv`、`*_judged.csv`），預設會保留這些檔案以便檢查結果。如需自動刪除，可取消註解腳本中的清理程式碼。

## 修改測試配置

### 更改模型名稱

兩個腳本都使用 `MODEL_NAME` 或 `model_name` 變數來指定模型。請修改為您已安裝的模型：

```python
# test_ollama_minimal.py (第 28 行)
model_name = "llama3.1:8b"  # 修改為您已安裝的模型

# test_ollama_e2e.py (第 17 行)
MODEL_NAME = "llama3.1:8b"  # 修改為您已安裝的模型
```

### 調整測試提示

在 `test_ollama_minimal.py` 中，您可以修改測試提示（第 27 行）：

```python
test_prompt = "What is 2+2? Answer with just the number."
```

在 `test_ollama_e2e.py` 中，您可以修改測試資料（第 26-39 行）：

```python
test_data = pd.DataFrame({
    'prompt': [
        'Your custom prompt here',
        # ... 更多提示
    ],
    'expected_answer': [
        'Expected answer',
        # ... 更多答案
    ],
    # ...
})
```

## 故障排除

### 錯誤：`ERROR: Connection refused` 或 `ERROR: Connection error`

**原因：** Ollama 服務未運行或無法連接。

**解決方法：**
1. 確認 Ollama 服務正在運行：`ollama list`
2. 檢查 `OLLAMA_HOST` 環境變數是否正確
3. 如果使用遠端服務，確認網路連接正常

### 錯誤：`ERROR: model 'llama3.1:8b' not found`

**原因：** 指定的模型未安裝。

**解決方法：**
```bash
ollama pull llama3.1:8b
# 或使用其他已安裝的模型
```

### 錯誤：`ModuleNotFoundError: No module named 'models'`

**原因：** 未從正確的目錄執行腳本。

**解決方法：**
```bash
# 確保從 experiments 目錄執行
cd experiments
python test_ollama_minimal.py
```

### 錯誤：`ERROR_NO_CONTENT` 或空回應

**原因：** 模型返回了空內容。

**解決方法：**
1. 檢查模型是否正常運作：`ollama run llama3.1:8b "test"`
2. 嘗試增加 `max_output_tokens` 參數
3. 檢查提示是否過於複雜或格式不正確

## 下一步

測試通過後，您可以：

1. **查看使用範例：** 參考 `examples/ollama_example.py`
2. **閱讀模型文件：** 查看 `experiments/models/README.md` 了解詳細用法
3. **運行實際實驗：** 使用 Ollama Provider 運行完整的實驗流程

## 相關文件

- `experiments/models/README.md` - 模型 Provider 詳細說明
- `examples/ollama_example.py` - Ollama 使用範例
- `OLLAMA_INTEGRATION_zh-TW.md` - Ollama 整合說明（繁體中文）

