#!/usr/bin/env python3
"""
記憶體監控和測試工具
用於測試matplotlib記憶體洩露修復是否有效
"""

import requests
import time
import psutil
import os
import json
from typing import Dict, List

class MemoryMonitor:
    def __init__(self, base_url: str = "http://localhost:5011"):
        self.base_url = base_url
        self.process = psutil.Process(os.getpid())
        self.memory_usage = []
    
    def get_memory_usage(self) -> Dict[str, float]:
        """獲取當前記憶體使用情況"""
        memory = self.process.memory_info()
        return {
            "rss": memory.rss / 1024 / 1024,  # MB
            "vms": memory.vms / 1024 / 1024,  # MB
            "percent": self.process.memory_percent()
        }
    
    def test_endpoints(self, iterations: int = 20):
        """測試各個端點的記憶體使用"""
        print(f"開始記憶體洩露測試，迭代次數: {iterations}")
        
        # 測試資料
        test_data = {
            "choropleth": {
                "data": [
                    {"county": "臺北市", "value": 100},
                    {"county": "新北市", "value": 200},
                    {"county": "桃園市", "value": 150}
                ],
                "column": "value",
                "level": "county"
            },
            "dot": {
                "x": [121.5, 121.6, 121.7],
                "y": [25.0, 25.1, 25.2],
                "size": 10,
                "color": "red"
            },
            "hist2d": {
                "x": [121.5, 121.6, 121.7, 121.8] * 25,
                "y": [25.0, 25.1, 25.2, 25.3] * 25,
                "bins": 50
            },
            "bubble": {
                "x": [121.5, 121.6, 121.7],
                "y": [25.0, 25.1, 25.2],
                "size": [10, 20, 15],
                "color": ["red", "blue", "green"]
            }
        }
        
        endpoints = [
            ("GET", "/boundary", None),
            ("POST", "/choropleth", test_data["choropleth"]),
            ("POST", "/dot", test_data["dot"]),
            ("POST", "/hist2d", test_data["hist2d"]),
            ("POST", "/bubble", test_data["bubble"])
        ]
        
        for i in range(iterations):
            print(f"\n迭代 {i+1}/{iterations}")
            initial_memory = self.get_memory_usage()
            print(f"初始記憶體: {initial_memory['rss']:.2f} MB")
            
            for method, endpoint, data in endpoints:
                try:
                    start_memory = self.get_memory_usage()
                    
                    if method == "GET":
                        response = requests.get(f"{self.base_url}{endpoint}")
                    else:
                        response = requests.post(f"{self.base_url}{endpoint}", json=data)
                    
                    if response.status_code == 200:
                        # 模擬獲取圖片數據但不保存
                        _ = response.content
                        print(f"✓ {endpoint}: {response.status_code}")
                    else:
                        print(f"✗ {endpoint}: {response.status_code}")
                    
                    end_memory = self.get_memory_usage()
                    memory_diff = end_memory['rss'] - start_memory['rss']
                    print(f"  記憶體變化: {memory_diff:+.2f} MB")
                    
                except Exception as e:
                    print(f"✗ {endpoint}: Error - {e}")
            
            final_memory = self.get_memory_usage()
            total_diff = final_memory['rss'] - initial_memory['rss']
            print(f"迭代總記憶體變化: {total_diff:+.2f} MB")
            
            self.memory_usage.append({
                "iteration": i + 1,
                "memory": final_memory,
                "diff": total_diff
            })
            
            # 每10次迭代手動清理記憶體
            if (i + 1) % 10 == 0:
                try:
                    cleanup_response = requests.post(f"{self.base_url}/cleanup")
                    if cleanup_response.status_code == 200:
                        print("✓ 手動記憶體清理完成")
                except Exception as e:
                    print(f"✗ 記憶體清理失敗: {e}")
            
            time.sleep(0.5)  # 短暫休息
    
    def analyze_results(self):
        """分析記憶體使用結果"""
        if not self.memory_usage:
            print("沒有記憶體使用數據")
            return
        
        print("\n=== 記憶體洩露分析 ===")
        
        initial_memory = self.memory_usage[0]['memory']['rss']
        final_memory = self.memory_usage[-1]['memory']['rss']
        total_diff = final_memory - initial_memory
        
        print(f"初始記憶體: {initial_memory:.2f} MB")
        print(f"最終記憶體: {final_memory:.2f} MB")
        print(f"總記憶體變化: {total_diff:+.2f} MB")
        
        # 檢查是否有持續的記憶體增長
        increasing_trend = 0
        for i in range(1, len(self.memory_usage)):
            if self.memory_usage[i]['memory']['rss'] > self.memory_usage[i-1]['memory']['rss']:
                increasing_trend += 1
        
        leak_percentage = (increasing_trend / (len(self.memory_usage) - 1)) * 100
        print(f"記憶體增長趨勢: {leak_percentage:.1f}%")
        
        if total_diff > 50:  # 超過50MB
            print("⚠️  可能存在記憶體洩露")
        elif leak_percentage > 70:
            print("⚠️  記憶體使用有持續增長趨勢")
        else:
            print("✓ 記憶體使用正常")
    
    def save_results(self, filename: str = "memory_test_results.json"):
        """保存測試結果"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.memory_usage, f, ensure_ascii=False, indent=2)
        print(f"測試結果已保存到: {filename}")


def main():
    print("GIS Toolkit 記憶體洩露測試工具")
    print("請確保API服務已在 http://localhost:5010 運行")
    
    monitor = MemoryMonitor()
    
    try:
        # 測試API是否可用
        response = requests.get("http://localhost:5011/")
        if response.status_code != 200:
            print("API服務不可用，請先啟動服務")
            return
        
        monitor.test_endpoints(iterations=30)
        monitor.analyze_results()
        monitor.save_results()
        
    except KeyboardInterrupt:
        print("\n測試被用戶中斷")
        monitor.analyze_results()
    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")


if __name__ == "__main__":
    main()
