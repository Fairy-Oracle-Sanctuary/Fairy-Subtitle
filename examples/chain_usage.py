#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 fairy-subtitle 库的链式调用功能
Test for fairy-subtitle library's method chaining functionality
"""

import os
from fairy_subtitle import SubtitleLoader

# 获取示例文件路径
example_file = os.path.join(os.path.dirname(__file__), "examples", "example.srt")

def test_chain_method():
    print("===== 测试链式调用功能 =====")
    
    # 示例1: 加载字幕 -> 时间偏移 -> 保存为VTT格式
    print("示例1: 加载字幕 -> 时间偏移 -> 保存为VTT格式")
    try:
        # 链式调用: load -> shift -> save
        SubtitleLoader.load(example_file)\
            .shift(1.5)\
            .save("chain_test_example1.vtt", "vtt")
        print("✓ 示例1执行成功")
    except Exception as e:
        print(f"✗ 示例1执行失败: {e}")
    
    # 示例2: 加载字幕 -> 查找特定文本 -> 保存为SRT格式
    print("\n示例2: 加载字幕 -> 查找特定文本 -> 保存为SRT格式")
    try:
        # 链式调用: load -> find -> save
        SubtitleLoader.load(example_file)\
            .find("风宫莲")\
            .save("chain_test_example2.srt")
        print("✓ 示例2执行成功")
    except Exception as e:
        print(f"✗ 示例2执行失败: {e}")
    
    # 示例3: 加载字幕 -> 按时间筛选 -> 时间偏移 -> 保存为ASS格式
    print("\n示例3: 加载字幕 -> 按时间筛选 -> 时间偏移 -> 保存为ASS格式")
    try:
        # 链式调用: load -> filter_by_time -> shift -> save
        SubtitleLoader.load(example_file)\
            .filter_by_time(0, 10)\
            .shift(0.5)\
            .save("chain_test_example3.ass", "ass")
        print("✓ 示例3执行成功")
    except Exception as e:
        print(f"✗ 示例3执行失败: {e}")
    
    # 示例4: 加载字幕 -> 合并字幕 -> 保存
    print("\n示例4: 加载字幕 -> 合并字幕 -> 保存")
    try:
        # 链式调用: load -> merge -> save
        SubtitleLoader.load(example_file)\
            .merge(0, 2)\
            .save("chain_test_example4.srt")
        print("✓ 示例4执行成功")
    except Exception as e:
        print(f"✗ 示例4执行失败: {e}")
    
    # 示例5: 加载字幕 -> 分割字幕 -> 保存
    print("\n示例5: 加载字幕 -> 分割字幕 -> 保存")
    try:
        # 链式调用: load -> split -> save
        SubtitleLoader.load(example_file)\
            .split(0, 1.5)\
            .save("chain_test_example5.srt")
        print("✓ 示例5执行成功")
    except Exception as e:
        print(f"✗ 示例5执行失败: {e}")
    
    # 示例6: 加载字幕 -> 查找特定文本 -> 按时间筛选 -> 时间偏移 -> 保存为VTT格式
    print("\n示例6: 加载字幕 -> 查找特定文本 -> 按时间筛选 -> 时间偏移 -> 保存为VTT格式")
    try:
        # 链式调用: load -> find -> filter_by_time -> shift -> save
        SubtitleLoader.load(example_file)\
            .find("蕾米莉亚")\
            .filter_by_time(0, 20)\
            .shift(1.0)\
            .save("chain_test_example6.vtt", "vtt")
        print("✓ 示例6执行成功")
    except Exception as e:
        print(f"✗ 示例6执行失败: {e}")
    
    print("\n===== 所有测试完成 =====")

if __name__ == "__main__":
    test_chain_method()