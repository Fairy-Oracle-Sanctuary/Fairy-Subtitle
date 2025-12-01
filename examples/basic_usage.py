"""
基础使用示例
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fairy_subtitle import SubtitleLoader


def main():
    # 创建解析器实例
    parser = SubtitleLoader.load("example/example.ass")
    print("===== ASS字幕解析 =====")
    parser.merge(0, 6)
    print(parser.cues[0])


if __name__ == "__main__":
    main()
