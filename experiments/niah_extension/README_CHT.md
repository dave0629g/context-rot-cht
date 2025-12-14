# 繁體中文 NIAH (Needle in a Haystack) 實驗流程

這個文檔說明如何使用繁體中文版本的 NIAH 工具進行完整的實驗流程。

## 目錄

1. [環境設置](#環境設置)
2. [步驟 1: 創建 Haystacks](#步驟-1-創建-haystacks)
3. [步驟 2: 運行 NIAH 實驗](#步驟-2-運行-niah-實驗)
4. [步驟 3: 評估結果](#步驟-3-評估結果)
5. [步驟 4: 視覺化](#步驟-4-視覺化)
6. [步驟 5: 分析干擾項（可選）](#步驟-5-分析干擾項可選)

## 環境設置

```bash
# 啟動虛擬環境
source ~/Projects/venvs/rot_venv/bin/activate

# 進入實驗目錄
cd experiments/niah_extension

# 確保安裝所需套件
pip install tiktoken pandas matplotlib requests
```

## 步驟 1: 創建 Haystacks

首先需要準備繁體中文文本文件，然後使用 `create_haystacks_cht.py` 生成測試資料。

### 準備文本資料

在 `../../data/chinese_texts/` 目錄中放置繁體中文 `.txt` 文件。

### 生成 Haystacks

```bash
python run/create_haystacks_cht.py \
  --haystack-folder ../../data/chinese_texts \
  --needle "台北101是台灣最高的建築物，高度達到508公尺。" \
  --question "台灣最高的建築物是什麼？高度是多少？" \
  --shuffled \
  --output-folder ../../data/niah_prompts
```

**參數說明：**
- `--haystack-folder`: 包含繁體中文文本的資料夾
- `--needle`: 要插入的關鍵資訊（正確答案）
- `--question`: 要問的問題
- `--shuffled`: 使用隨機打亂模式（建議使用）
- `--output-folder`: 輸出資料夾
- `--distractors`: （可選）干擾句子

**輸出：**
- `niah_prompts_cht_shuffled.csv` 或 `niah_prompts_cht_sequential.csv`

## 步驟 2: 運行 NIAH 實驗

使用不同的 provider 運行實驗。

### 使用 Ollama（本地模型）

```bash
# 先測試連接
python run/test_ollama.py --model deepseek-r1:1.5b

# 運行實驗
python run/run_niah_extension_cht.py \
    --provider ollama \
    --input-path ../../data/niah_prompts/niah_prompts_cht_shuffled.csv \
    --output-path ../../results/deepseek_r1_1.5b_niah_results_cht.csv \
    --input-column prompt \
    --output-column output \
    --model-name deepseek-r1:1.5b \
    --max-context-length 32000 \
    --max-tokens-per-minute 2000000
```

### 使用 OpenAI

```bash
python run/run_niah_extension_cht.py \
    --provider openai \
    --input-path ../../data/niah_prompts/niah_prompts_cht_shuffled.csv \
    --output-path ../../results/gpt4_niah_results_cht.csv \
    --input-column prompt \
    --output-column output \
    --model-name gpt-4-turbo \
    --max-context-length 128000 \
    --max-tokens-per-minute 150000
```

**參數說明：**
- `--provider`: 選擇 provider（ollama, openai, anthropic, google）
- `--input-path`: 步驟 1 生成的 CSV 文件
- `--output-path`: 結果輸出路徑
- `--model-name`: 模型名稱
- `--max-context-length`: 模型的最大 context 長度
- `--max-tokens-per-minute`: 速率限制

**可用的 Ollama 模型：**
- `deepseek-r1:1.5b` (最小，1.04 GB)
- `deepseek-r1:7b` (4.36 GB)
- `qwen2:7b` (4.13 GB)
- `gemma3:latest` (3.11 GB)

## 步驟 3: 評估結果

使用 LLM 評判器評估模型輸出的準確性。

```bash
python evaluate/evaluate_niah_extension_cht.py \
    --input-path ../../results/deepseek_r1_1.5b_niah_results_cht.csv \
    --output-path ../../results/deepseek_r1_1.5b_niah_evaluated_cht.csv \
    --model-name gpt-4.1-2025-04-14 \
    --output-column output \
    --question-column question \
    --correct-answer-column answer \
    --max-context-length 1047576 \
    --max-tokens-per-minute 2000000
```

**參數說明：**
- `--input-path`: 步驟 2 的輸出文件
- `--output-path`: 評估結果輸出路徑
- `--model-name`: 用於評判的模型（預設使用 GPT-4）
- 其他欄位名稱參數根據你的 CSV 結構調整

**輸出：**
- 添加 `llm_judge_output` 欄位，包含 "true" 或 "false"

## 步驟 4: 視覺化

生成性能熱圖。

```bash
python evaluate/visualize_cht.py \
    --csv-path ../../results/deepseek_r1_1.5b_niah_evaluated_cht.csv \
    --title "DeepSeek R1 1.5B 繁體中文 NIAH 性能" \
    --output-path ../../results/deepseek_r1_1.5b_niah_heatmap_cht.png
```

**參數說明：**
- `--csv-path`: 步驟 3 的評估結果文件
- `--title`: 圖表標題（可選）
- `--output-path`: 輸出圖片路徑

**輸出：**
- 熱圖 PNG 文件
- 終端顯示整體準確率和總樣本數

## 步驟 5: 分析干擾項（可選）

如果你在步驟 1 中添加了干擾項，可以分析模型如何受干擾項影響。

### 準備干擾項 JSON 文件

創建 `distractors_cht.json`：

```json
{
  "0": {
    "distractor": "台灣最高的建築物是台中摩天輪，高度達到600公尺。",
    "rewrite_for_analysis": "台中摩天輪（600公尺）"
  },
  "1": {
    "distractor": "台灣最高的建築物是高雄85大樓，高度達到347公尺。",
    "rewrite_for_analysis": "高雄85大樓（347公尺）"
  }
}
```

### 運行分析

```bash
python evaluate/analyze_distractors_cht.py \
    --input-path ../../results/deepseek_r1_1.5b_niah_evaluated_cht.csv \
    --output-path ../../results/deepseek_r1_1.5b_distractors_analysis_cht.csv \
    --visual-path ../../results/deepseek_r1_1.5b_distractors_histogram_cht.png \
    --model-name "DeepSeek R1 1.5B" \
    --distractors-file ../../data/distractors_cht.json \
    --output-column output \
    --question-column question \
    --correct-answer-column answer \
    --max-context-length 1047576 \
    --max-tokens-per-minute 2000000
```

**輸出：**
- CSV 文件包含 `distractor_label` 欄位
- 直方圖顯示模型選擇不同干擾項的分佈

## 完整範例工作流程

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

# 3. 測試 Ollama
python run/test_ollama.py --model deepseek-r1:1.5b

# 4. 運行實驗
python run/run_niah_extension_cht.py \
    --provider ollama \
    --input-path ../../data/niah_prompts/niah_prompts_cht_shuffled.csv \
    --output-path ../../results/deepseek_niah_cht.csv \
    --input-column prompt \
    --output-column output \
    --model-name deepseek-r1:1.5b \
    --max-context-length 32000 \
    --max-tokens-per-minute 2000000

# 5. 評估結果
python evaluate/evaluate_niah_extension_cht.py \
    --input-path ../../results/deepseek_niah_cht.csv \
    --output-path ../../results/deepseek_niah_evaluated_cht.csv

# 6. 視覺化
python evaluate/visualize_cht.py \
    --csv-path ../../results/deepseek_niah_evaluated_cht.csv \
    --title "DeepSeek R1 1.5B 繁體中文 NIAH" \
    --output-path ../../results/deepseek_niah_heatmap_cht.png
```

## 注意事項

1. **Ollama 服務**：確保 Ollama 服務正在運行（`ollama serve`）
2. **模型下載**：使用前確保已下載所需模型（`ollama pull <model-name>`）
3. **API 密鑰**：使用 OpenAI/Anthropic/Google 時需要設置相應的 API 密鑰在 `.env` 文件中
4. **Context 長度**：根據不同模型調整 `--max-context-length`
5. **中文字體**：視覺化需要系統支援中文字體

## 文件結構

```
niah_extension/
├── run/
│   ├── create_haystacks_cht.py      # 創建繁體中文測試資料
│   ├── run_niah_extension_cht.py    # 運行繁體中文實驗
│   └── test_ollama.py               # 測試 Ollama 連接
├── evaluate/
│   ├── evaluate_niah_extension_cht.py   # 評估結果
│   ├── visualize_cht.py                 # 視覺化
│   └── analyze_distractors_cht.py       # 分析干擾項
└── README_CHT.md                    # 本文檔
```

## 疑難排解

### Ollama 連接失敗
```bash
# 檢查 Ollama 是否運行
curl http://127.0.0.1:11434/api/tags

# 啟動 Ollama
ollama serve
```

### 中文顯示問題
如果視覺化中文字體顯示為方框，安裝中文字體：
- macOS: 系統自帶中文字體
- Linux: `sudo apt-install fonts-wqy-zenhei`
- Windows: 確保安裝了中文字體

### 記憶體不足
使用較小的模型或減少 `max-context-length`。
