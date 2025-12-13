# fairy_subtitle/subtitle.py
# A simple and powerful subtitle parsing library

import os
import re

from .exceptions import UnsupportedFormatError
from .models import Subtitle
from .parsers import parse_ass, parse_sbv, parse_srt, parse_sub, parse_vtt

# 未来可以导入更多解析器
# from .parsers import parse_vtt, parse_ass


def _validate_srt_format(content: str) -> bool:
    """
    Validates if content matches SRT format characteristics
    验证内容是否符合SRT格式特征

    SRT format typically starts with numbers followed by timestamp format (00:00:00,000 --> 00:00:00,000)
    SRT格式通常以数字开头，后面跟着时间戳格式 (00:00:00,000 --> 00:00:00,000)
    """
    # 检查是否包含SRT时间戳格式
    srt_timestamp_pattern = r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}"
    return bool(re.search(srt_timestamp_pattern, content))


def _validate_vtt_format(content: str) -> bool:
    """
    Validates if content matches VTT format characteristics
    验证内容是否符合VTT格式特征

    VTT format typically starts with "WEBVTT"
    VTT格式通常以"WEBVTT"开头
    """
    return content.strip().startswith("WEBVTT")


def _validate_ass_format(content: str) -> bool:
    """
    Validates if content matches ASS format characteristics
    验证内容是否符合ASS格式特征

    ASS format typically starts with "[Script Info]"
    ASS格式通常以"[Script Info]"开头
    """
    return content.strip().startswith("[Script Info]")


def _validate_sbv_format(content: str) -> bool:
    """
    Validates if content matches SBV format characteristics
    验证内容是否符合SBV格式特征

    SBV format typically starts with timestamps in format "00:00:00.000,00:00:00.000"
    SBV格式通常以时间戳格式 "00:00:00.000,00:00:00.000" 开头
    """
    # 检查是否包含SBV时间戳格式
    sbv_timestamp_pattern = r"\d{2}:\d{2}:\d{2}\.\d{3},\d{2}:\d{2}:\d{2}\.\d{3}"
    return bool(re.search(sbv_timestamp_pattern, content))


def _validate_sub_format(content: str) -> bool:
    """
    Validates if content matches MicroDVD (.sub) format characteristics
    验证内容是否符合MicroDVD (.sub)格式特征

    MicroDVD format typically uses {frame_range}text format
    MicroDVD格式通常使用{帧范围}文本格式
    """
    # 检查是否包含MicroDVD格式特征
    sub_pattern = r"\{[0-9]+\}[0-9]+\}"
    return bool(re.search(sub_pattern, content))


class SubtitleLoader:
    @staticmethod
    def load(file_path: str, format: str = "auto", encoding: str = "utf-8") -> Subtitle:
        """
        Loads a subtitle file.
        加载字幕文件。

        :param file_path: Path to the subtitle file.
        :param file_path: 文件路径。
        :param format: Subtitle format ('srt', 'vtt', 'ass', 'sbv', 'sub', 'auto').
        :param format: 字幕格式 ('srt', 'vtt', 'ass', 'sbv', 'sub', 'auto')。
        :param encoding: File encoding.
        :param encoding: 文件编码。
        :return: A Subtitle object.
        :return: 一个 Subtitle 对象。
        """
        file_path = os.path.abspath(file_path)

        # 1. 读取文件内容
        with open(file_path, "r", encoding=encoding) as f:
            content = f.read().strip()

        # 2. 处理格式指定
        if format != "auto":
            # 验证文件内容是否与指定格式匹配
            format = format.lower()
            validation_functions = {
                "srt": _validate_srt_format,
                "vtt": _validate_vtt_format,
                "ass": _validate_ass_format,
                "sbv": _validate_sbv_format,
                "sub": _validate_sub_format,
            }

            if format in validation_functions:
                if not validation_functions[format](content):
                    # 如果验证失败，尝试自动检测格式
                    print(
                        f"警告：文件内容与指定格式 '{format}' 不匹配，尝试自动检测格式..."
                    )
                    format = "auto"

        # 3. 自动检测格式 (如果需要)
        if format == "auto":
            # 先尝试基于内容检测
            if _validate_srt_format(content):
                format = "srt"
            elif _validate_vtt_format(content):
                format = "vtt"
            elif _validate_ass_format(content):
                format = "ass"
            elif _validate_sbv_format(content):
                format = "sbv"
            elif _validate_sub_format(content):
                format = "sub"
            else:
                # Fallback detection based on file extension
                # 基于扩展名的后备检测
                if file_path.lower().endswith(".srt"):
                    format = "srt"
                elif file_path.lower().endswith(".vtt"):
                    format = "vtt"
                elif file_path.lower().endswith(".ass"):
                    format = "ass"
                elif file_path.lower().endswith(".sbv"):
                    format = "sbv"
                elif file_path.lower().endswith(".sub"):
                    format = "sub"
                else:
                    raise UnsupportedFormatError(
                        "无法自动检测格式，请手动指定 'srt', 'vtt', 'ass', 'sbv' 或 'sub'。"
                        "Unable to automatically detect format, please manually specify 'srt', 'vtt', 'ass', 'sbv' or 'sub'."
                    )

        # 4. 根据格式选择对应的解析器
        if format == "srt":
            return parse_srt(file_path, content)
        elif format == "vtt":
            return parse_vtt(file_path, content)
        elif format == "ass":
            return parse_ass(file_path, content)
        elif format == "sbv":
            return parse_sbv(file_path, content)
        elif format == "sub":
            return parse_sub(file_path, content)
        else:
            raise UnsupportedFormatError(f"不支持的格式: {format}")


# For user convenience, a simpler alias can be provided in the package's __init__.py
# 为了方便用户，可以在包的 __init__.py 中提供一个更简单的别名
