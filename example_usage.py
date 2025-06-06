#!/usr/bin/env python3
"""
Graph類使用範例 - 展示如何使用物件化參數
"""
import pandas as pd
import numpy as np
from src.graph import Graph, ChoroplethParams, Hist2DParams, DotParams, BubbleParams


def main():
    # 創建Graph實例
    graph = Graph()
    
    # 1. 等值區域圖範例
    print("1. 等值區域圖範例")
    
    # 創建示例數據
    sample_data = pd.DataFrame({
        'county': ['台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市'],
        'population': [2600000, 4000000, 2250000, 2800000, 1880000, 2770000]
    })
    
    # 使用ChoroplethParams物件
    choropleth_params = ChoroplethParams(
        data=sample_data,
        column='population',
        level='county',
        cmap='GnBu',
        colorbar_format='{x:,.0f}',
        colorbar_tick_visible=True
    )
    
    # 繪製等值區域圖
    fig, ax = graph.plot_choropleth(choropleth_params)
    print("等值區域圖繪製完成")
    
    # 2. 2D直方圖範例
    print("2. 2D直方圖範例")
    
    # 生成隨機座標數據
    np.random.seed(42)
    x_coords = np.random.uniform(119, 122, 1000)
    y_coords = np.random.uniform(22, 25, 1000)
    
    hist2d_params = Hist2DParams(
        x=x_coords.tolist(),
        y=y_coords.tolist(),
        bins=50,
        cmap='Reds',
        alpha=0.7,
        cmin=2
    )
    
    fig, ax = graph.plot_hist2d(hist2d_params)
    print("2D直方圖繪製完成")
    
    # 3. 點圖範例
    print("3. 點圖範例")
    
    # 生成示例點位數據
    x_points = [121.5, 121.0, 120.7, 120.2, 120.5, 120.3]
    y_points = [25.0, 24.8, 24.2, 23.5, 22.8, 22.6]
    
    dot_params = DotParams(
        x=x_points,
        y=y_points,
        size=50,
        color='blue',
        alpha=0.8
    )
    
    fig, ax = graph.plot_dot(dot_params)
    print("點圖繪製完成")
    
    # 4. 氣泡圖範例
    print("4. 氣泡圖範例")
    
    # 不同大小和顏色的氣泡數據
    bubble_sizes = [100, 200, 150, 300, 250, 180]
    bubble_colors = ['red', 'green', 'blue', 'orange', 'purple', 'yellow']
    
    bubble_params = BubbleParams(
        x=x_points,
        y=y_points,
        size=bubble_sizes,
        color=bubble_colors,
        alpha=0.6
    )
    
    fig, ax = graph.plot_bubble(bubble_params)
    print("氣泡圖繪製完成")
    
    print("\n所有圖表繪製完成！")
    print("\n使用物件化參數的優點：")
    print("- 參數組織更清晰")
    print("- 類型安全")
    print("- 更容易重用和修改參數")
    print("- 支持預設值和驗證")


if __name__ == "__main__":
    main()
