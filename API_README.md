# GIS Toolkit API 更新說明

## 概述

GIS Toolkit API 已經更新為使用物件化參數，提供更好的類型安全性、參數組織和開發體驗。

## API 端點

### 1. GET /boundary
**描述**: 獲取台灣地圖邊界  
**參數**: 無  
**返回**: PNG圖片

### 2. POST /choropleth
**描述**: 創建等值區域圖（分層設色圖）  
**參數**:
```json
{
  "data": [
    {"county": "台北市", "value": 100},
    {"county": "新北市", "value": 200}
  ],
  "column": "value",
  "level": "county",
  "cmap": "GnBu",
  "colorbar_format": "{x:,.0f}",
  "colorbar_tick_visible": true
}
```

### 3. POST /dot
**描述**: 創建點散布圖  
**參數**:
```json
{
  "x": [121.5, 120.2],
  "y": [25.0, 23.0],
  "size": 50,
  "color": "red",
  "alpha": 0.8
}
```

### 4. POST /hist2d
**描述**: 創建2D直方圖  
**參數**:
```json
{
  "x": [121.5, 120.2, 120.7],
  "y": [25.0, 23.0, 24.2],
  "bins": 50,
  "cmap": "Reds",
  "alpha": 0.7,
  "cmin": 2
}
```

### 5. POST /bubble
**描述**: 創建氣泡圖  
**參數**:
```json
{
  "x": [121.5, 120.2, 120.7],
  "y": [25.0, 23.0, 24.2],
  "size": [100, 200, 150],
  "color": ["red", "blue", "green"],
  "alpha": 0.6
}
```

## 更新內容

### 後端更新 (app.py)
1. **導入物件化參數類別**: 從 `src.graph` 導入 `ChoroplethParams`, `Hist2DParams`, `DotParams`, `BubbleParams`
2. **更新API端點**: 所有繪圖端點現在使用參數物件來調用 `Graph` 類的方法
3. **改善錯誤處理**: 保持原有的錯誤處理機制
4. **API文檔**: FastAPI 自動生成的文檔依然可用於測試

### 前端更新 (home.html)
1. **新增氣泡圖端點**: 在API端點列表中添加氣泡圖
2. **更新說明**: 添加關於物件化參數更新的說明
3. **改善視覺效果**: 使用藍色背景區塊突出顯示更新信息

## 使用方式

### 啟動服務器
```bash
python app.py
```
服務器將在 `http://localhost:5010` 啟動

### 訪問API文檔
瀏覽器訪問: `http://localhost:5010/docs`

### 測試API
```bash
python test_api.py
```

## 範例用法

### 使用 curl 測試等值區域圖
```bash
curl -X POST "http://localhost:5010/choropleth" \
     -H "Content-Type: application/json" \
     -d '{
       "data": [
         {"county": "台北市", "value": 100},
         {"county": "新北市", "value": 200}
       ],
       "column": "value",
       "level": "county",
       "cmap": "Blues"
     }' \
     --output choropleth.png
```

### 使用 Python requests
```python
import requests

# 等值區域圖
data = {
    "data": [
        {"county": "台北市", "value": 100},
        {"county": "新北市", "value": 200}
    ],
    "column": "value",
    "level": "county",
    "cmap": "Blues"
}

response = requests.post(
    "http://localhost:5010/choropleth",
    json=data
)

if response.status_code == 200:
    with open("choropleth.png", "wb") as f:
        f.write(response.content)
```

## 技術細節

### 物件化參數的優點
1. **類型安全**: 使用 dataclass 提供類型提示
2. **參數組織**: 相關參數被邏輯性地組織在一起
3. **預設值管理**: 所有預設值集中管理
4. **擴展性**: 新增參數不會影響現有的方法簽名
5. **維護性**: 更易於重用和修改參數

### API 響應格式
- **成功**: 返回 PNG 圖片 (Content-Type: image/png)
- **失敗**: 返回 JSON 錯誤信息 (HTTP 500)

## 故障排除

### 常見問題
1. **連接失敗**: 確保服務器已啟動且端口5010未被占用
2. **圖片生成失敗**: 檢查地理數據格式是否正確
3. **參數錯誤**: 參考API文檔確認參數格式

### 日誌查看
服務器會在控制台輸出詳細的錯誤信息，有助於調試問題。

---

*更新日期: 2025年5月28日*  
*版本: 2.0 - 物件化參數版本*
