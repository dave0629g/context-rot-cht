# Ollama 整合說明 - Context Rot 實驗

本文檔說明為 Context Rot 實驗框架新增的 Ollama 整合功能，讓您能夠使用本地開源模型進行離線實驗。

## 概述

Ollama provider 擴展了現有的模型提供者架構，支援通過 Ollama 進行本地模型推理。這使研究人員能夠：

- 完全離線運行實驗
- 避免大規模測試的 API 成本
- 使用開源模型（Llama、Qwen、Mistral 等）
- 使用本地模型作為 LLM 評判員進行評估

## 快速開始

### 1. 安裝 Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# 或從 https://ollama.ai 下載
```

### 2. 拉取模型

```bash
# 測試用範例模型
ollama pull llama3.1:8b
ollama pull qwen2.5:14b

# 驗證安裝
ollama list
```

### 3. 安裝 Python 依賴

```bash
pip install -r requirements.txt
```

### 4. 運行測試

```bash
# 測試 Ollama provider
python tests/test_ollama_provider.py

# 運行範例腳本
python examples/ollama_example.py
```

## 使用範例

### 1. 基本使用

```python
from models.providers.ollama import OllamaProvider

provider = OllamaProvider()
provider.main(
    input_path="input.csv",
    output_path="output.csv",
    input_column="prompt",
    output_column="response",
    model_name="llama3.1:8b",
    max_context_length=128000,
    max_tokens_per_minute=1000000  # 本地模型無速率限制
)
```

### 2. 使用 Ollama 作為 LLM 評判員

```python
from models.llm_judge import LLMJudge

judge = LLMJudge(
    prompt=your_judge_prompt,
    model_name="qwen2.5:14b",
    provider="ollama"  # 關鍵參數
)

judge.evaluate(
    input_path="results.csv",
    output_path="judged_results.csv",
    max_context_length=128000,
    max_tokens_per_minute=1000000
)
```

### 3. 自訂 Ollama 主機

```bash
export OLLAMA_HOST="http://remote-server:11434"
python your_experiment.py
```

## 新增/修改的檔案

### 新增檔案

1. **[experiments/models/providers/ollama.py](experiments/models/providers/ollama.py)** - Ollama provider 實作
2. **[experiments/models/providers/__init__.py](experiments/models/providers/__init__.py)** - Provider 模組初始化
3. **[examples/ollama_example.py](examples/ollama_example.py)** - 使用範例
4. **[tests/test_ollama_provider.py](tests/test_ollama_provider.py)** - 測試套件
5. **[CHANGELOG.md](CHANGELOG.md)** - 變更日誌
6. **[OLLAMA_INTEGRATION.md](OLLAMA_INTEGRATION.md)** - 英文整合文檔
7. **本檔案** - 中文整合文檔

### 修改檔案

1. **[experiments/models/llm_judge.py](experiments/models/llm_judge.py)** - 新增 provider 參數支援
2. **[requirements.txt](requirements.txt)** - 新增 ollama 依賴
3. **[experiments/models/README.md](experiments/models/README.md)** - 新增 Ollama 文檔
4. **[README.md](README.md)** - 更新快速開始說明

## 推薦模型

| 模型 | 大小 | 上下文長度 | 使用場景 |
|------|------|-----------|---------|
| llama3.1:8b | ~8GB | 128K | 測試、一般任務 |
| qwen2.5:14b | ~14GB | 128K | 評判、複雜任務 |
| mistral:7b | ~7GB | 32K | 快速測試 |
| codellama:13b | ~13GB | 16K | 程式碼相關實驗 |

## 本地模型優勢

- **無速率限制**：每分鐘可處理無限 token
- **無 API 成本**：在您的硬體上免費推理
- **隱私保護**：資料不離開您的機器
- **離線運行**：無需網路連線

## 硬體需求

- **7B 模型**：最少 8GB RAM
- **13-14B 模型**：最少 16GB RAM
- **70B+ 模型**：需要高階硬體或量化

建議使用 GPU 以獲得更快的推理速度。

## 學術用途

此整合特別適合：

1. **可重現性**：本地模型確保結果一致
2. **可訪問性**：無需 API 金鑰或費用
3. **隱私性**：敏感資料保持本地
4. **客製化**：可針對特定任務微調模型
5. **比較研究**：比較 API 與本地模型

## 向後相容

所有變更完全向後相容：

- 現有實驗無需修改即可運行
- `LLMJudge` 預設使用 OpenAI provider
- 其他 provider（OpenAI、Anthropic、Google）保持不變

## 常見問題排解

### 連線被拒絕
```bash
# 確保 Ollama 正在運行
ollama serve
```

### 找不到模型
```bash
# 先拉取模型
ollama pull llama3.1:8b
```

### 記憶體不足
```
解決方案：
- 使用較小的模型
- 增加系統 RAM
- 使用量化模型
```

### 推理速度慢
```
解決方案：
- 使用 GPU（如果可用）
- 使用量化模型
- 減少 max_output_tokens
```

## 參考資源

- [Ollama 官方網站](https://ollama.ai)
- [Ollama Python 函式庫](https://github.com/ollama/ollama-python)
- [Context Rot 技術報告](https://research.trychroma.com/context-rot)

## 環境變數

- **OLLAMA_HOST**（選用）：Ollama 伺服器位址，預設為 `http://localhost:11434`

## 測試覆蓋

測試套件包含：
- 客戶端初始化測試
- 單一提示處理測試
- 批次 CSV 處理測試

所有測試都可通過 `python tests/test_ollama_provider.py` 運行。

---

**版本**：1.0
**日期**：2025-12-02
**狀態**：準備用於學術實驗
