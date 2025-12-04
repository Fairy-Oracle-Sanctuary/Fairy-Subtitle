"""
基础使用示例
Basic Usage Example
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fairy_subtitle import SubtitleLoader


def main():
    # 创建解析器实例
    print("===== ASS字幕解析 =====")
    print("===== ASS Subtitle Parsing =====")
    ass_parser = SubtitleLoader.load("examples/example.ass", format="srt")
    print(f"ASS字幕数量: {len(ass_parser)}")
    print(f"Number of ASS subtitles: {len(ass_parser)}")
    print(f"ASS字幕时长: {ass_parser.get_duration():.2f}秒")
    print(f"ASS subtitle duration: {ass_parser.get_duration():.2f} seconds")
    print("合并前第一个字幕:")
    print("First subtitle before merging:")
    print(ass_parser[0])
    ass_parser.merge(0, 2)
    print("合并后第一个字幕:")
    print("First subtitle after merging:")
    print(ass_parser[0])
    print()

    # 解析SRT文件
    print("===== SRT字幕解析 =====")
    print("===== SRT Subtitle Parsing =====")
    srt_parser = SubtitleLoader.load("examples/example.srt")
    print(f"SRT字幕数量: {len(srt_parser)}")
    print(f"Number of SRT subtitles: {len(srt_parser)}")
    print(f"SRT字幕时长: {srt_parser.get_duration():.2f}秒")
    print(f"SRT subtitle duration: {srt_parser.get_duration():.2f} seconds")
    print("第一个SRT字幕:")
    print("First SRT subtitle:")
    print(srt_parser[0])
    print()

    # 解析VTT文件
    print("===== VTT字幕解析 =====")
    print("===== VTT Subtitle Parsing =====")
    vtt_parser = SubtitleLoader.load("examples/example.vtt")
    print(f"VTT字幕数量: {len(vtt_parser)}")
    print(f"Number of VTT subtitles: {len(vtt_parser)}")
    print(f"VTT字幕时长: {vtt_parser.get_duration():.2f}秒")
    print(f"VTT subtitle duration: {vtt_parser.get_duration():.2f} seconds")
    print("第一个VTT字幕:")
    print("First VTT subtitle:")
    print(vtt_parser[0])
    print()

    # 演示字幕操作功能
    print("===== 字幕操作演示 =====")
    print("===== Subtitle Operations Demo =====")
    # 查找包含特定文本的字幕
    # Find subtitles containing specific text
    search_results = srt_parser.find("字幕")
    print(f"包含'字幕'的字幕数量: {len(search_results)}")
    print(f"Number of subtitles containing '字幕': {len(search_results)}")

    # 过滤特定时间范围内的字幕
    # Filter subtitles within a specific time range
    filtered_cues = srt_parser.filter_by_time(10.0, 30.0)
    print(f"10-30秒范围内的字幕数量: {len(filtered_cues)}")
    print(f"Number of subtitles between 10-30 seconds: {len(filtered_cues)}")

    # 时间偏移示例
    # Time shift example
    print("时间偏移前第一个字幕:")
    print("First subtitle before time shift:")
    print(srt_parser[0])
    srt_parser.shift(1.0)  # 所有字幕向后移动1秒
    srt_parser.shift(1.0)  # Shift all subtitles forward by 1 second
    print("向后移动1秒后第一个字幕:")
    print("First subtitle after shifting forward by 1 second:")
    print(srt_parser[0])


if __name__ == "__main__":
    main()
