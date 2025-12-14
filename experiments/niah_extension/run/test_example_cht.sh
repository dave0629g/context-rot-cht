#!/bin/bash
# 繁體中文 NIAH 測試範例腳本

set -e  # 遇到錯誤立即停止

echo "=================================="
echo "繁體中文 NIAH 測試範例"
echo "=================================="
echo ""

# 啟動虛擬環境
source ~/Projects/venvs/rot_venv/bin/activate

# 設定路徑
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# 設定變數
HAYSTACK_FOLDER="../../data/chinese_texts"
OUTPUT_FOLDER="../../data/niah_prompts"
RESULTS_FOLDER="../../results"

# 創建輸出資料夾
mkdir -p "$OUTPUT_FOLDER"
mkdir -p "$RESULTS_FOLDER"

# 步驟 1: 創建 Haystacks
echo "步驟 1: 創建繁體中文 Haystacks..."
echo "--------------------------------"
python run/create_haystacks_cht.py \
  --haystack-folder "$HAYSTACK_FOLDER" \
  --needle "台北101是台灣最高的建築物，高度達到508公尺。" \
  --question "台灣最高的建築物是什麼？高度是多少？" \
  --shuffled \
  --output-folder "$OUTPUT_FOLDER"

echo ""
echo "✓ Haystacks 創建完成！"
echo ""

# 步驟 2: 測試 Ollama 連接
echo "步驟 2: 測試 Ollama 連接..."
echo "--------------------------------"
python run/test_ollama.py --model deepseek-r1:1.5b --skip-query

echo ""
echo "✓ Ollama 連接測試完成！"
echo ""

# 步驟 3: 運行 NIAH 實驗（使用較小的 context length 進行測試）
echo "步驟 3: 運行 NIAH 實驗..."
echo "--------------------------------"
python run/run_niah_extension_cht.py \
    --provider ollama \
    --input-path "$OUTPUT_FOLDER/niah_prompts_cht_shuffled.csv" \
    --output-path "$RESULTS_FOLDER/deepseek_niah_cht_test.csv" \
    --input-column prompt \
    --output-column output \
    --model-name deepseek-r1:1.5b \
    --max-context-length 10000 \
    --max-tokens-per-minute 2000000

echo ""
echo "✓ NIAH 實驗完成！"
echo ""

# 步驟 4: 評估結果
echo "步驟 4: 評估結果..."
echo "--------------------------------"
echo "注意: 這一步需要 OpenAI API key"
echo "如果沒有 API key，請跳過此步驟"
echo ""

read -p "是否繼續評估結果？(y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]
then
    python evaluate/evaluate_niah_extension_cht.py \
        --input-path "$RESULTS_FOLDER/deepseek_niah_cht_test.csv" \
        --output-path "$RESULTS_FOLDER/deepseek_niah_cht_evaluated.csv" \
        --model-name gpt-4o-mini \
        --max-context-length 128000 \
        --max-tokens-per-minute 200000

    echo ""
    echo "✓ 評估完成！"
    echo ""

    # 步驟 5: 視覺化
    echo "步驟 5: 生成視覺化..."
    echo "--------------------------------"
    python evaluate/visualize_cht.py \
        --csv-path "$RESULTS_FOLDER/deepseek_niah_cht_evaluated.csv" \
        --title "DeepSeek R1 1.5B 繁體中文 NIAH 測試" \
        --output-path "$RESULTS_FOLDER/deepseek_niah_cht_heatmap.png"

    echo ""
    echo "✓ 視覺化完成！"
else
    echo "跳過評估步驟"
fi

echo ""
echo "=================================="
echo "測試流程完成！"
echo "=================================="
echo ""
echo "結果文件位於: $RESULTS_FOLDER"
echo "- deepseek_niah_cht_test.csv: 模型輸出結果"
echo "- deepseek_niah_cht_evaluated.csv: 評估結果（如果有執行）"
echo "- deepseek_niah_cht_heatmap.png: 視覺化熱圖（如果有執行）"
echo ""
