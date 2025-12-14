#!/bin/bash
# 繁體中文 NIAH 完整測試矩陣
# 這個腳本會執行一系列測試來全面評估模型性能

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 啟動虛擬環境
source ~/Projects/venvs/rot_venv/bin/activate

# 設定路徑
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# 創建結果資料夾
RESULTS_DIR="../../results/comprehensive_test_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESULTS_DIR"

echo -e "${BLUE}=================================="
echo "繁體中文 NIAH 完整測試矩陣"
echo "==================================${NC}"
echo ""
echo "結果將儲存在: $RESULTS_DIR"
echo ""

# Judge 設定
JUDGE_PROVIDER="ollama"
JUDGE_MODEL="gemma3:27b"

# ============================================
# 函數: 運行單一測試
# ============================================
run_test() {
    local test_id=$1
    local model=$2
    local max_context=$3
    local input_csv=$4
    local output_name=$5
    local description=$6

    echo -e "${YELLOW}[${test_id}] ${description}${NC}"
    echo "  模型: ${model}"
    echo "  Max Context: ${max_context}"
    echo "  輸入: ${input_csv}"

    # 運行實驗
    python run/run_niah_extension_cht.py \
        --provider ollama \
        --input-path "${input_csv}" \
        --output-path "${RESULTS_DIR}/${output_name}.csv" \
        --input-column prompt \
        --output-column output \
        --model-name "${model}" \
        --max-context-length ${max_context} \
        --max-tokens-per-minute 2000000

    # 評估結果
    echo "  評估中..."
    python evaluate/evaluate_niah_extension_cht.py \
        --provider ${JUDGE_PROVIDER} \
        --model-name ${JUDGE_MODEL} \
        --input-path "${RESULTS_DIR}/${output_name}.csv" \
        --output-path "${RESULTS_DIR}/${output_name}_evaluated.csv" \
        --max-tokens-per-minute 2000000

    # 生成視覺化
    echo "  生成視覺化..."
    python evaluate/visualize_cht.py \
        --csv-path "${RESULTS_DIR}/${output_name}_evaluated.csv" \
        --title "${description}" \
        --output-path "${RESULTS_DIR}/${output_name}_heatmap.png"

    echo -e "${GREEN}  ✓ 完成${NC}"
    echo ""
}

# ============================================
# 階段 1: 準備 Haystacks
# ============================================
echo -e "${BLUE}階段 1: 準備測試資料${NC}"
echo ""

# 1.1 基礎 haystack (如果還沒有)
if [ ! -f "../../data/niah_prompts/niah_prompts_cht_shuffled.csv" ]; then
    echo "創建隨機模式 haystack..."
    python run/create_haystacks_cht.py \
      --haystack-folder ../../data/chinese_texts \
      --needle "台北101是台灣最高的建築物，高度達到508公尺。" \
      --question "台灣最高的建築物是什麼？高度是多少？" \
      --shuffled \
      --output-folder ../../data/niah_prompts
fi

# 1.2 順序模式 haystack
if [ ! -f "../../data/niah_prompts/niah_prompts_cht_sequential.csv" ]; then
    echo "創建順序模式 haystack..."
    python run/create_haystacks_cht.py \
      --haystack-folder ../../data/chinese_texts \
      --needle "台北101是台灣最高的建築物，高度達到508公尺。" \
      --question "台灣最高的建築物是什麼？高度是多少？" \
      --output-folder ../../data/niah_prompts
fi

echo -e "${GREEN}✓ 測試資料準備完成${NC}"
echo ""

# ============================================
# 階段 2: 基礎性能測試
# ============================================
echo -e "${BLUE}階段 2: 基礎性能測試 (比較不同模型)${NC}"
echo ""

# T1: DeepSeek R1 1.5B
run_test "T1.1" \
    "deepseek-r1:1.5b" \
    32000 \
    "../../data/niah_prompts/niah_prompts_cht_shuffled.csv" \
    "t1_deepseek_1.5b_shuffled" \
    "DeepSeek R1 1.5B - 隨機模式"

run_test "T1.2" \
    "deepseek-r1:1.5b" \
    32000 \
    "../../data/niah_prompts/niah_prompts_cht_sequential.csv" \
    "t1_deepseek_1.5b_sequential" \
    "DeepSeek R1 1.5B - 順序模式"

# T2: DeepSeek R1 7B
run_test "T2.1" \
    "deepseek-r1:7b" \
    32000 \
    "../../data/niah_prompts/niah_prompts_cht_shuffled.csv" \
    "t2_deepseek_7b_shuffled" \
    "DeepSeek R1 7B - 隨機模式"

run_test "T2.2" \
    "deepseek-r1:7b" \
    32000 \
    "../../data/niah_prompts/niah_prompts_cht_sequential.csv" \
    "t2_deepseek_7b_sequential" \
    "DeepSeek R1 7B - 順序模式"

# T3: Qwen2 7B
run_test "T3.1" \
    "qwen2:7b" \
    32768 \
    "../../data/niah_prompts/niah_prompts_cht_shuffled.csv" \
    "t3_qwen2_7b_shuffled" \
    "Qwen2 7B - 隨機模式"

run_test "T3.2" \
    "qwen2:7b" \
    32768 \
    "../../data/niah_prompts/niah_prompts_cht_sequential.csv" \
    "t3_qwen2_7b_sequential" \
    "Qwen2 7B - 順序模式"

# ============================================
# 階段 3: Context Length 測試
# ============================================
echo -e "${BLUE}階段 3: Context Length 影響測試${NC}"
echo ""

# 使用表現最好的模型 (假設是 Qwen2 7B)
BEST_MODEL="qwen2:7b"

run_test "T4.1" \
    "${BEST_MODEL}" \
    5000 \
    "../../data/niah_prompts/niah_prompts_cht_shuffled.csv" \
    "t4_${BEST_MODEL//:/_}_5k" \
    "${BEST_MODEL} - 短 Context (5K)"

run_test "T4.2" \
    "${BEST_MODEL}" \
    10000 \
    "../../data/niah_prompts/niah_prompts_cht_shuffled.csv" \
    "t4_${BEST_MODEL//:/_}_10k" \
    "${BEST_MODEL} - 中 Context (10K)"

run_test "T4.3" \
    "${BEST_MODEL}" \
    32768 \
    "../../data/niah_prompts/niah_prompts_cht_shuffled.csv" \
    "t4_${BEST_MODEL//:/_}_32k" \
    "${BEST_MODEL} - 長 Context (32K)"

# ============================================
# 生成測試報告
# ============================================
echo -e "${BLUE}=================================="
echo "生成測試報告"
echo "==================================${NC}"

REPORT_FILE="${RESULTS_DIR}/test_report.txt"

cat > "$REPORT_FILE" << EOF
繁體中文 NIAH 完整測試報告
===============================
測試時間: $(date)
Judge 模型: ${JUDGE_MODEL}

測試結果摘要:
---------------

階段 1: 基礎性能測試
EOF

# 提取每個測試的準確率
for file in ${RESULTS_DIR}/*_evaluated.csv; do
    if [ -f "$file" ]; then
        base_name=$(basename "$file" _evaluated.csv)
        accuracy=$(python -c "
import pandas as pd
df = pd.read_csv('$file')
df['accuracy'] = df['llm_judge_output'].apply(lambda x: 1 if str(x).strip().lower() == 'true' else 0)
print(f'{df[\"accuracy\"].mean():.3f}')
" 2>/dev/null || echo "N/A")
        echo "  ${base_name}: ${accuracy}" >> "$REPORT_FILE"
    fi
done

cat >> "$REPORT_FILE" << EOF

測試檔案位置:
---------------
$RESULTS_DIR

視覺化檔案:
---------------
EOF

ls -1 ${RESULTS_DIR}/*.png >> "$REPORT_FILE" 2>/dev/null || echo "  無視覺化檔案" >> "$REPORT_FILE"

echo -e "${GREEN}✓ 報告已生成: ${REPORT_FILE}${NC}"
echo ""

# ============================================
# 完成
# ============================================
echo -e "${GREEN}=================================="
echo "所有測試完成！"
echo "==================================${NC}"
echo ""
echo "結果位置: $RESULTS_DIR"
echo "測試報告: $REPORT_FILE"
echo ""
echo "建議下一步:"
echo "1. 查看各個測試的熱圖"
echo "2. 比較不同模型的準確率"
echo "3. 分析 context length 對性能的影響"
echo ""
