# 繁體中文 NIAH 實驗 - 完整總結

## 📋 已完成的工作

### 1. 核心工具（繁體中文版本）

#### 運行階段 (`experiments/niah_extension/run/`)
- ✅ **create_haystacks_cht.py** - 創建繁體中文測試資料
  - 支援中文句子分割（。！？；）
  - 隨機打亂和順序模式
  - 支援干擾項
  
- ✅ **run_niah_extension_cht.py** - 運行繁體中文實驗
  - 支援 4 種 providers（Ollama, OpenAI, Anthropic, Google）
  - 繁體中文介面
  - 支援自定義 Ollama URL

- ✅ **test_ollama.py** - 測試 Ollama 連接
  - 列出可用模型
  - 測試簡單查詢
  - 連接診斷

#### 評估階段 (`experiments/niah_extension/evaluate/`)
- ✅ **evaluate_niah_extension_cht.py** - 評估結果
  - 使用 LLM 作為評判器
  - 繁體中文評估提示
  - 自動批次處理

- ✅ **visualize_cht.py** - 視覺化熱圖
  - 支援中文字體
  - 生成性能熱圖
  - 顯示準確率統計

- ✅ **analyze_distractors_cht.py** - 分析干擾項
  - 識別模型選擇的干擾項
  - 生成分佈直方圖
  - 繁體中文標籤

### 2. Provider 支援

#### 新增的 Provider (`experiments/models/providers/`)
- ✅ **ollama.py** - Ollama 本地模型支援
  - 使用 REST API
  - 支援自定義 base URL
  - 完整錯誤處理

#### 更新的 Provider
- ✅ **run_niah_extension.py** - 添加 Ollama 支援到原始版本

### 3. 範例資料

#### 繁體中文文本 (`data/chinese_texts/`)
- ✅ **taiwan_geography.txt** (3.3 KB) - 台灣地理
  - 涵蓋地形、河流、氣候、城市等
  
- ✅ **technology_history.txt** (4.9 KB) - 科技歷史
  - 從古代發明到現代 AI
  
- ✅ **food_culture.txt** (4.7 KB) - 飲食文化
  - 台灣小吃、夜市、節慶食物等
  
- ✅ **education_system.txt** (4.9 KB) - 教育制度
  - 教育體系、改革、挑戰等

### 4. 文檔

- ✅ **README_CHT.md** - 完整使用手冊
  - 詳細的步驟說明
  - 參數解釋
  - 疑難排解

- ✅ **QUICKSTART_CHT.md** - 快速開始指南
  - 簡化的入門流程
  - 常見問題解答
  - 範例指令

- ✅ **test_example_cht.sh** - 自動化測試腳本
  - 一鍵執行完整流程
  - 互動式選項

## 🎯 完整流程

```
1. 準備文本資料
   ↓
2. 創建 Haystacks (create_haystacks_cht.py)
   ↓
3. 運行實驗 (run_niah_extension_cht.py)
   ↓
4. 評估結果 (evaluate_niah_extension_cht.py)
   ↓
5. 視覺化 (visualize_cht.py)
   ↓
6. 分析干擾項 (analyze_distractors_cht.py) [可選]
```

## 🚀 快速開始

### 最簡單的方式（推薦）

```bash
cd experiments/niah_extension
./run/test_example_cht.sh
```

### 手動執行

```bash
# 1. 啟動環境
source ~/Projects/venvs/rot_venv/bin/activate
cd experiments/niah_extension

# 2. 創建 haystacks
python run/create_haystacks_cht.py \
  --haystack-folder ../../data/chinese_texts \
  --needle "台北101是台灣最高的建築物，高度達到508公尺。" \
  --question "台灣最高的建築物是什麼？高度是多少？" \
  --shuffled \
  --output-folder ../../data/niah_prompts

# 3. 運行實驗（Ollama）
python run/run_niah_extension_cht.py \
    --provider ollama \
    --input-path ../../data/niah_prompts/niah_prompts_cht_shuffled.csv \
    --output-path ../../results/deepseek_niah_cht.csv \
    --input-column prompt \
    --output-column output \
    --model-name deepseek-r1:1.5b \
    --max-context-length 32000 \
    --max-tokens-per-minute 2000000

# 4. 評估結果（需要 OpenAI API key）
python evaluate/evaluate_niah_extension_cht.py \
    --input-path ../../results/deepseek_niah_cht.csv \
    --output-path ../../results/deepseek_niah_cht_evaluated.csv

# 5. 視覺化
python evaluate/visualize_cht.py \
    --csv-path ../../results/deepseek_niah_cht_evaluated.csv \
    --output-path ../../results/deepseek_niah_cht_heatmap.png
```

## 🔧 支援的模型

### Ollama（本地，無需 API key）
- deepseek-r1:1.5b (1.04 GB) ⭐ 推薦新手
- deepseek-r1:7b (4.36 GB)
- deepseek-r1:32b (18.49 GB)
- qwen2:7b (4.13 GB) - 中文表現佳
- gemma3:latest (3.11 GB)
- gemma3:27b (16.20 GB)

### OpenAI（需要 API key）
- gpt-4o-mini (經濟實惠)
- gpt-4-turbo
- gpt-4

### Anthropic（需要 API key）
- claude-3-haiku
- claude-3-sonnet
- claude-3-opus

### Google（需要 API key）
- gemini-pro

## 📊 輸出文件

### 創建 Haystacks
- `niah_prompts_cht_shuffled.csv` - 隨機模式
- `niah_prompts_cht_sequential.csv` - 順序模式

### 運行實驗
- `{model_name}_niah_cht.csv` - 包含模型輸出的完整資料

### 評估結果
- `{model_name}_niah_cht_evaluated.csv` - 添加 llm_judge_output 欄位

### 視覺化
- `{model_name}_niah_cht_heatmap.png` - 性能熱圖

### 分析干擾項
- `{model_name}_distractors_analysis_cht.csv` - 干擾項標籤
- `{model_name}_distractors_histogram_cht.png` - 分佈圖

## 🎨 主要特點

1. **完整繁體中文支援**
   - 所有訊息都是繁體中文
   - 正確的中文句子分割
   - 中文字體支援

2. **多 Provider 支援**
   - Ollama（本地，免費）
   - OpenAI（雲端）
   - Anthropic（雲端）
   - Google（雲端）

3. **彈性配置**
   - 自定義 needle 和 question
   - 調整 context length
   - 添加干擾項

4. **完整流程**
   - 資料準備 → 實驗 → 評估 → 視覺化 → 分析

5. **易用性**
   - 自動化腳本
   - 詳細文檔
   - 範例資料

## 📁 文件結構

```
context-rot-cht/
├── data/
│   ├── chinese_texts/          # 繁體中文範例文本
│   │   ├── taiwan_geography.txt
│   │   ├── technology_history.txt
│   │   ├── food_culture.txt
│   │   └── education_system.txt
│   └── niah_prompts/           # 生成的 prompts（執行後產生）
│
├── experiments/
│   ├── models/
│   │   └── providers/
│   │       └── ollama.py       # ✨ 新增：Ollama provider
│   │
│   └── niah_extension/
│       ├── run/
│       │   ├── create_haystacks_cht.py      # ✨ 繁中版
│       │   ├── run_niah_extension_cht.py    # ✨ 繁中版
│       │   ├── test_ollama.py               # ✨ 測試工具
│       │   └── test_example_cht.sh          # ✨ 自動化腳本
│       │
│       ├── evaluate/
│       │   ├── evaluate_niah_extension_cht.py  # ✨ 繁中版
│       │   ├── visualize_cht.py                # ✨ 繁中版
│       │   └── analyze_distractors_cht.py      # ✨ 繁中版
│       │
│       └── README_CHT.md       # ✨ 繁中文檔
│
├── QUICKSTART_CHT.md           # ✨ 快速開始指南
└── SUMMARY_CHT.md              # ✨ 本文件
```

## ✅ 檢查清單

開始測試前，確認：

- [ ] 已啟動虛擬環境 (`source ~/Projects/venvs/rot_venv/bin/activate`)
- [ ] Ollama 服務正在運行（如果使用 Ollama）
- [ ] 已下載所需模型（`ollama pull deepseek-r1:1.5b`）
- [ ] 繁體中文文本文件已準備好
- [ ] （可選）OpenAI API key 已設定（用於評估）

## 🎓 學習路徑

### 初學者
1. 執行 `test_example_cht.sh` 了解整個流程
2. 閱讀生成的 CSV 文件，了解資料結構
3. 嘗試修改 needle 和 question

### 進階使用者
1. 測試不同的模型，比較性能
2. 調整 context length，觀察影響
3. 添加干擾項，測試模型的魯棒性
4. 使用自己的繁體中文文本

### 研究者
1. 深入分析熱圖，找出模型的弱點
2. 比較不同 provider 的表現
3. 研究 needle 位置對準確率的影響
4. 分析干擾項對模型的影響模式

## 🔍 下一步建議

1. **執行基本測試**
   ```bash
   cd experiments/niah_extension
   ./run/test_example_cht.sh
   ```

2. **查看結果**
   - 檢查 `results/` 目錄中的文件
   - 觀察熱圖中的模式

3. **實驗不同配置**
   - 不同的 needle 和 question
   - 不同的模型
   - 不同的 context length

4. **分析結果**
   - 哪些位置的 needle 最難找到？
   - 模型在什麼長度下表現最好？
   - 干擾項如何影響性能？

## 📞 獲取幫助

如果遇到問題：

1. 查看 [QUICKSTART_CHT.md](QUICKSTART_CHT.md) 的常見問題
2. 查看 [README_CHT.md](experiments/niah_extension/README_CHT.md) 的疑難排解
3. 檢查終端輸出的錯誤訊息
4. 確認所有前置條件都已滿足

## 🎉 準備就緒！

你現在擁有完整的繁體中文 NIAH 測試環境。從最簡單的自動化腳本開始，逐步探索各種功能吧！

祝實驗順利！🚀
