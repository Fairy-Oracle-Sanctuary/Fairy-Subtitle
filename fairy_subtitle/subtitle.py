# fairy_script/subtitle.py

import os

from .exceptions import UnsupportedFormatError
from .models import Subtitle
from .parsers import parse_ass, parse_srt, parse_vtt  # 添加parse_vtt导入

# 未来可以导入更多解析器
# from .parsers import parse_vtt, parse_ass


class SubtitleLoader:
    @staticmethod
    def load(file_path: str, format: str = "auto", encoding: str = "utf-8") -> Subtitle:
        """
        加载字幕文件。

        :param file_path: 文件路径。
        :param format: 字幕格式 ('srt', 'vtt', 'ass', 'auto')。
        :param encoding: 文件编码。
        :return: 一个 Subtitle 对象。
        """
        file_path = os.path.abspath(file_path)

        # 1. 自动检测格式 (如果需要)
        if format == "auto":
            # 简单的基于扩展名的检测
            if file_path.lower().endswith(".srt"):
                format = "srt"
            elif file_path.lower().endswith(".vtt"):
                format = "vtt"
            elif file_path.lower().endswith(".ass"):
                format = "ass"
            else:
                raise UnsupportedFormatError(
                    "无法自动检测格式，请手动指定 'srt', 'vtt' 或 'ass'。"
                )

        # 2. 读取文件内容
        with open(file_path, "r", encoding=encoding) as f:
            content = f.read().strip()

        # 3. 根据格式选择对应的解析器
        if format == "srt":
            return parse_srt(file_path, content)
        elif format == 'vtt':
            return parse_vtt(file_path, content)  # 启用VTT解析
        elif format == "ass":
            return parse_ass(file_path, content)
        else:
            raise UnsupportedFormatError(f"不支持的格式: {format}")


# 为了方便用户，可以在包的 __init__.py 中提供一个更简单的别名