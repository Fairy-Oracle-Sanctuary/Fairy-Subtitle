import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fairy_subtitle import SubtitleLoader


def main():
    sbv_parser = SubtitleLoader.load("examples/example.srt")
    sbv_parser.save("examples/example_test.sbv", "sbv")


if __name__ == "__main__":
    main()
