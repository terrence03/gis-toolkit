#!/usr/bin/env python3
"""
API測試腳本 - 測試更新後的API端點
"""
import requests
import json
import time


def test_api_endpoints():
    """測試所有API端點"""
    base_url = "http://localhost:5010"
    
    print("🧪 開始測試GIS Toolkit API...")
    print(f"基礎URL: {base_url}")
    print("-" * 50)
    
    # 測試首頁
    print("1. 測試首頁端點...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ 首頁端點正常")
        else:
            print(f"❌ 首頁端點失敗: {response.status_code}")
    except Exception as e:
        print(f"❌ 首頁端點連接失敗: {e}")
    
    # 測試邊界圖
    print("\n2. 測試邊界圖端點...")
    try:
        response = requests.get(f"{base_url}/boundary")
        if response.status_code == 200:
            print("✅ 邊界圖端點正常")
            with open("test_boundary.png", "wb") as f:
                f.write(response.content)
            print("   已保存為 test_boundary.png")
        else:
            print(f"❌ 邊界圖端點失敗: {response.status_code}")
    except Exception as e:
        print(f"❌ 邊界圖端點失敗: {e}")
    
    # 測試等值區域圖
    print("\n3. 測試等值區域圖端點...")
    choropleth_data = {
        "data": [
            {"county": "臺北市", "value": 100},
            {"county": "新北市", "value": 200},
            {"county": "桃園市", "value": 150},
            {"county": "臺中市", "value": 180},
            {"county": "臺南市", "value": 120},
            {"county": "高雄市", "value": 220}
        ],
        "column": "value",
        "level": "county",
        "cmap": "Blues",
        "colorbar_format": "{x:,.0f}",
        "colorbar_tick_visible": True
    }
    
    try:
        response = requests.post(
            f"{base_url}/choropleth",
            json=choropleth_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("✅ 等值區域圖端點正常")
            with open("test_choropleth.png", "wb") as f:
                f.write(response.content)
            print("   已保存為 test_choropleth.png")
        else:
            print(f"❌ 等值區域圖端點失敗: {response.status_code}")
            print(f"   錯誤信息: {response.text}")
    except Exception as e:
        print(f"❌ 等值區域圖端點失敗: {e}")
    
    # 測試點圖
    print("\n4. 測試點圖端點...")
    dot_data = {
        "x": [121.5, 120.2, 120.7, 120.9, 120.3],
        "y": [25.0, 23.0, 24.2, 24.8, 22.6],
        "size": 100,
        "color": "red",
        "alpha": 0.8
    }
    
    try:
        response = requests.post(
            f"{base_url}/dot",
            json=dot_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("✅ 點圖端點正常")
            with open("test_dot.png", "wb") as f:
                f.write(response.content)
            print("   已保存為 test_dot.png")
        else:
            print(f"❌ 點圖端點失敗: {response.status_code}")
            print(f"   錯誤信息: {response.text}")
    except Exception as e:
        print(f"❌ 點圖端點失敗: {e}")
    
    # 測試2D直方圖
    print("\n5. 測試2D直方圖端點...")
    hist2d_data = {
        "x": [120.96, 121.5, 120.2, 120.7, 120.9, 120.3] * 20,
        "y": [23.70, 25.0, 23.0, 24.2, 24.8, 22.6] * 20,
        "bins": 30,
        "cmap": "Reds",
        "alpha": 0.7,
        "cmin": 2
    }
    
    try:
        response = requests.post(
            f"{base_url}/hist2d",
            json=hist2d_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("✅ 2D直方圖端點正常")
            with open("test_hist2d.png", "wb") as f:
                f.write(response.content)
            print("   已保存為 test_hist2d.png")
        else:
            print(f"❌ 2D直方圖端點失敗: {response.status_code}")
            print(f"   錯誤信息: {response.text}")
    except Exception as e:
        print(f"❌ 2D直方圖端點失敗: {e}")
    
    # 測試氣泡圖
    print("\n6. 測試氣泡圖端點...")
    bubble_data = {
        "x": [121.5, 120.2, 120.7, 120.9, 120.3],
        "y": [25.0, 23.0, 24.2, 24.8, 22.6],
        "size": [100, 200, 150, 300, 250],
        "color": ["red", "blue", "green", "orange", "purple"],
        "alpha": 0.6
    }
    
    try:
        response = requests.post(
            f"{base_url}/bubble",
            json=bubble_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("✅ 氣泡圖端點正常")
            with open("test_bubble.png", "wb") as f:
                f.write(response.content)
            print("   已保存為 test_bubble.png")
        else:
            print(f"❌ 氣泡圖端點失敗: {response.status_code}")
            print(f"   錯誤信息: {response.text}")
    except Exception as e:
        print(f"❌ 氣泡圖端點失敗: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API測試完成！")
    print("   請檢查生成的PNG文件以驗證圖表質量。")
    print("   如需更詳細的API文檔，請訪問: http://localhost:5010/docs")


if __name__ == "__main__":
    # 先等待一下確保服務器已啟動
    print("等待API服務器啟動...")
    time.sleep(2)
    test_api_endpoints()
