# 繁體中文 NIAH 快速開始指南

## 已準備好的資源

✅ **範例繁體中文文本** (在 `data/chinese_texts/`):
- `taiwan_geography.txt` - 台灣地理 (3.3 KB)
- `technology_history.txt` - 科技歷史 (4.9 KB)
- `food_culture.txt` - 飲食文化 (4.7 KB)
- `education_system.txt` - 教育制度 (4.9 KB)

✅ **完整的測試工具**:
- 創建 haystacks
- 運行實驗
- 評估結果
- 視覺化
- 分析干擾項

✅ **支援的 Provider**:
- Ollama (本地模型，無需 API key)
- OpenAI
- Anthropic
- Google

## 方法 1: 使用自動化腳本（推薦）

最簡單的方式是使用已經準備好的測試腳本：

```bash
# 進入實驗目錄
cd experiments/niah_extension

# 運行測試腳本
./run/test_example_cht.sh
```

這個腳本會自動執行：
1. 創建繁體中文 haystacks
2. 測試 Ollama 連接
3. 運行 NIAH 實驗（使用 DeepSeek R1 1.5B）
4. 可選：評估結果（需要 OpenAI API key）
5. 可選：生成視覺化熱圖

## 方法 2: 手動執行（逐步了解每個步驟）

### 步驟 1: 啟動環境

```bash
source ~/Projects/venvs/rot_venv/bin/activate
cd experiments/niah_extension
```

### 步驟 2: 創建 Haystacks

```bash
python run/create_haystacks_cht.py \
  --haystack-folder ../../data/chinese_texts \
  --needle "台北101是台灣最高的建築物，高度達到508公尺。" \
  --question "台灣最高的建築物是什麼？高度是多少？" \
  --shuffled \
  --output-folder ../../data/niah_prompts
```

**輸出**: `niah_prompts_cht_shuffled.csv`

### 步驟 3: 測試 Ollama（確保連接正常）

```bash
python run/test_ollama.py --model deepseek-r1:1.5b
```

### 步驟 4: 運行實驗

使用 Ollama 本地模型（無需 API key）：

```bash
python run/run_niah_extension_cht.py \
    --provider ollama \
    --input-path ../../data/niah_prompts/niah_prompts_cht_shuffled.csv \
    --output-path ../../results/deepseek_niah_cht.csv \
    --input-column prompt \
    --output-column output \
    --model-name deepseek-r1:1.5b \
    --max-context-length 32000 \
    --max-tokens-per-minute 2000000
```

**或使用 OpenAI**（需要 API key）：

```bash
# 確保 .env 文件中有 OPENAI_API_KEY
python run/run_niah_extension_cht.py \
    --provider openai \
    --input-path ../../data/niah_prompts/niah_prompts_cht_shuffled.csv \
    --output-path ../../results/gpt4_niah_cht.csv \
    --input-column prompt \
    --output-column output \
    --model-name gpt-4o-mini \
    --max-context-length 128000 \
    --max-tokens-per-minute 150000
```

### 步驟 5: 評估結果（需要 OpenAI API key）

```bash
python evaluate/evaluate_niah_extension_cht.py \
    --input-path ../../results/deepseek_niah_cht.csv \
    --output-path ../../results/deepseek_niah_cht_evaluated.csv \
    --model-name gpt-4o-mini
```

### 步驟 6: 視覺化

```bash
python evaluate/visualize_cht.py \
    --csv-path ../../results/deepseek_niah_cht_evaluated.csv \
    --title "DeepSeek R1 1.5B 繁體中文 NIAH" \
    --output-path ../../results/deepseek_niah_cht_heatmap.png
```

## 可用的模型

### Ollama 本地模型（你已經安裝的）

根據你的系統，可用模型有：

- **deepseek-r1:1.5b** (1.04 GB) - 最小，適合測試
- **deepseek-r1:7b** (4.36 GB) - 中等大小
- **qwen2:7b** (4.13 GB) - 中文表現好
- **gemma3:latest** (3.11 GB)
- **gemma3:27b** (16.20 GB) - 大型模型
- **deepseek-r1:32b** (18.49 GB) - 最大

建議從最小的模型開始測試！

### 不同模型的 Context Length

記得根據模型調整 `--max-context-length`：

| 模型 | Context Length |
|------|----------------|
| deepseek-r1:1.5b | 32,000 |
| deepseek-r1:7b | 32,000 |
| qwen2:7b | 32,768 |
| gpt-4o-mini | 128,000 |
| gpt-4-turbo | 128,000 |

## 測試不同的 Needle 和 Question

你可以修改 needle 和 question 來測試不同的情境：

**範例 1: 科技主題**
```bash
--needle "量子運算使用量子位元進行平行運算，在某些問題上遠超傳統電腦。" \
--question "量子運算的主要優勢是什麼？"
```

**範例 2: 飲食主題**
```bash
--needle "珍珠奶茶是台灣發明的特色飲品，已經風靡全世界。" \
--question "珍珠奶茶的起源地是哪裡？"
```

**範例 3: 教育主題**
```bash
--needle "108課綱強調核心素養的培養，重視能力而非只是知識的傳授。" \
--question "108課綱的主要特色是什麼？"
```

## 測試干擾項（進階）

創建 `data/distractors_cht.json`：

```json
{
  "0": {
    "distractor": "台北101的高度是450公尺。",
    "rewrite_for_analysis": "450公尺"
  },
  "1": {
    "distractor": "台北101的高度是600公尺。",
    "rewrite_for_analysis": "600公尺"
  },
  "2": {
    "distractor": "台北101的高度是380公尺。",
    "rewrite_for_analysis": "380公尺"
  }
}
```

然後在創建 haystacks 時添加 `--distractors` 參數：

```bash
python run/create_haystacks_cht.py \
  --haystack-folder ../../data/chinese_texts \
  --needle "台北101是台灣最高的建築物，高度達到508公尺。" \
  --question "台灣最高的建築物是什麼？高度是多少？" \
  --shuffled \
  --output-folder ../../data/niah_prompts \
  --distractors "台北101的高度是450公尺" "台北101的高度是600公尺" "台北101的高度是380公尺"
```

## 常見問題

### Q: Ollama 連接失敗怎麼辦？

```bash
# 檢查 Ollama 是否運行
curl http://127.0.0.1:11434/api/tags

# 如果沒有運行，啟動 Ollama
ollama serve

# 在另一個終端檢查可用模型
ollama list
```

### Q: 模型不存在怎麼辦？

```bash
# 下載模型
ollama pull deepseek-r1:1.5b

# 檢查是否成功
ollama list
```

### Q: 記憶體不足怎麼辦？

1. 使用更小的模型（如 deepseek-r1:1.5b）
2. 減少 `--max-context-length`
3. 關閉其他應用程式

### Q: 視覺化中文顯示為方框？

確保系統安裝了中文字體。macOS 通常內建支援，Linux 可能需要：

```bash
sudo apt-install fonts-wqy-zenhei
```

### Q: 沒有 OpenAI API key 可以完成整個流程嗎？

可以！你可以：
1. 使用 Ollama 運行實驗（步驟 4）
2. 手動檢查輸出結果（CSV 文件）
3. 跳過自動評估步驟

或者使用免費的 OpenAI API 額度（新用戶通常有 $5 免費額度）。

## 下一步

完成基本測試後，你可以：

1. **測試不同模型** - 比較不同模型的表現
2. **調整 context length** - 測試模型在不同長度下的表現
3. **添加干擾項** - 測試模型抵抗錯誤資訊的能力
4. **使用自己的文本** - 添加更多繁體中文文本到 `data/chinese_texts/`
5. **分析結果** - 深入分析熱圖，了解模型的優缺點

## 完整文檔

詳細說明請參考：
- [experiments/niah_extension/README_CHT.md](experiments/niah_extension/README_CHT.md)

## 需要幫助？

如果遇到問題，檢查：
1. 虛擬環境是否已啟動
2. Ollama 服務是否正在運行
3. 所需的套件是否已安裝
4. 文件路徑是否正確

祝測試順利！🚀
