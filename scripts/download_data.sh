#!/usr/bin/env bash
# ==============================================================================
# Google Drive 資料下載腳本
# Download datasets from Google Drive to data/ directory
# ==============================================================================

set -e  # Exit on error

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "============================================================"
echo "Context Rot - Data Download Script"
echo "============================================================"

# 專案根目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DATA_DIR="${PROJECT_ROOT}/data"

echo -e "${GREEN}✓${NC} Project root: ${PROJECT_ROOT}"

# 建立 data 目錄
mkdir -p "${DATA_DIR}"
echo -e "${GREEN}✓${NC} Data directory: ${DATA_DIR}"

# 檢查 gdown 是否安裝
if ! command -v gdown &> /dev/null; then
    echo -e "${YELLOW}⚠${NC} gdown not found, installing..."
    pip install gdown
fi

echo ""
echo "============================================================"
echo "Downloading datasets..."
echo "============================================================"

# ==============================================================================
# TODO: 請在此處填入您的 Google Drive 連結
# 格式範例:
#   gdown "https://drive.google.com/uc?id=FILE_ID" -O "${DATA_DIR}/filename.zip"
#   gdown --folder "https://drive.google.com/drive/folders/FOLDER_ID" -O "${DATA_DIR}/"
# ==============================================================================

# 範例 1: 下載單一檔案
# GDRIVE_FILE_ID="YOUR_FILE_ID_HERE"
# gdown "https://drive.google.com/uc?id=${GDRIVE_FILE_ID}" -O "${DATA_DIR}/dataset.zip"

# 範例 2: 下載整個資料夾
# GDRIVE_FOLDER_ID="YOUR_FOLDER_ID_HERE"
# gdown --folder "https://drive.google.com/drive/folders/${GDRIVE_FOLDER_ID}" -O "${DATA_DIR}/"

# 範例 3: 從原始 README 提供的連結下載
# 參考: https://drive.google.com/drive/folders/1FuOysriSotnYasJUbZJzn31SWt85_3yf
GDRIVE_FOLDER_ID="1FuOysriSotnYasJUbZJzn31SWt85_3yf"
gdown --folder "https://drive.google.com/drive/folders/${GDRIVE_FOLDER_ID}" -O "${DATA_DIR}/"

echo ""
echo -e "${YELLOW}⚠${NC} Please edit this script and add your Google Drive links"
echo -e "${YELLOW}⚠${NC} Uncomment the appropriate download commands above"
echo ""

# ==============================================================================
# 解壓縮檔案 (如果需要)
# ==============================================================================

# 如果下載的是 zip 檔案，自動解壓縮
# if ls "${DATA_DIR}"/*.zip 1> /dev/null 2>&1; then
#     echo ""
#     echo "============================================================"
#     echo "Extracting archives..."
#     echo "============================================================"
#
#     for zipfile in "${DATA_DIR}"/*.zip; do
#         echo -e "${GREEN}✓${NC} Extracting: $(basename "$zipfile")"
#         unzip -q -o "$zipfile" -d "${DATA_DIR}"
#     done
#
#     echo -e "${GREEN}✓${NC} Extraction completed"
# fi

# ==============================================================================
# 驗證下載結果
# ==============================================================================

echo ""
echo "============================================================"
echo "Download Summary"
echo "============================================================"

# 計算檔案數量和大小
FILE_COUNT=$(find "${DATA_DIR}" -type f | wc -l | tr -d ' ')
TOTAL_SIZE=$(du -sh "${DATA_DIR}" | cut -f1)

echo -e "${GREEN}✓${NC} Files downloaded: ${FILE_COUNT}"
echo -e "${GREEN}✓${NC} Total size: ${TOTAL_SIZE}"
echo ""
echo "Data directory contents:"
ls -lh "${DATA_DIR}"

echo ""
echo "============================================================"
echo "Done!"
echo "============================================================"
