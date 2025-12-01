# Scripts 說明

此目錄包含專案的輔助腳本。

## 可用腳本

### 1. `smoke_test.sh`
快速環境測試腳本

```bash
./scripts/smoke_test.sh
```

### 2. `download_data.sh`
從 Google Drive 下載實驗資料集

#### 使用方式

1. **編輯腳本，填入 Google Drive 連結**

   打開 `scripts/download_data.sh`，在標記為 `TODO` 的區域填入您的連結：

   ```bash
   # 範例 1: 下載單一檔案
   GDRIVE_FILE_ID="YOUR_FILE_ID_HERE"
   gdown "https://drive.google.com/uc?id=${GDRIVE_FILE_ID}" -O "${DATA_DIR}/dataset.zip"

   # 範例 2: 下載整個資料夾
   GDRIVE_FOLDER_ID="YOUR_FOLDER_ID_HERE"
   gdown --folder "https://drive.google.com/drive/folders/${GDRIVE_FOLDER_ID}" -O "${DATA_DIR}/"
   ```

2. **執行腳本**

   ```bash
   ./scripts/download_data.sh
   ```

#### 如何獲取 Google Drive ID

- **檔案連結**: `https://drive.google.com/file/d/FILE_ID/view`
  - FILE_ID 就是您需要的 ID

- **資料夾連結**: `https://drive.google.com/drive/folders/FOLDER_ID`
  - FOLDER_ID 就是您需要的 ID

#### 功能特性

- ✓ 自動建立 `data/` 目錄
- ✓ 自動安裝 `gdown` (如果未安裝)
- ✓ 支援下載單一檔案或整個資料夾
- ✓ 可選的自動解壓縮功能
- ✓ 下載後顯示統計資訊

#### 疑難排解

**問題**: gdown 無法下載大檔案
```bash
# 解決方案: 使用 --fuzzy 參數
gdown --fuzzy "https://drive.google.com/file/d/FILE_ID/view"
```

**問題**: 需要認證的私有檔案
```bash
# 解決方案: 先手動登入 gdown
gdown --help
# 參考 gdown 文檔處理認證
```

## 原始資料集來源

根據原始 README，資料集可從此處下載：
https://drive.google.com/drive/folders/1FuOysriSotnYasJUbZJzn31SWt85_3yf

您可以將此連結填入 `download_data.sh` 腳本中。
