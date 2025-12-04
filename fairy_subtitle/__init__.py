"""
fairy-subtitle - A simple and powerful subtitle parsing library
fairy-subtitle - 一个简单而强大的字幕解析库

Supports parsing and processing of multiple subtitle formats
支持多种字幕格式的解析和处理
"""

__version__ = "1.0.0"
__author__ = "baby2016"
__email__ = "2185823427@qq.com"

from fairy_subtitle.exceptions import (
    FormatError,
    InvalidSubtitleContentError,
    InvalidTimeFormatError,
    ParseError,
    SubtitleError,
    UnsupportedFormatError,
)
from fairy_subtitle.models import Cue
from fairy_subtitle.subtitle import SubtitleLoader

__all__ = [
    "SubtitleLoader",
    "Cue",
    "SubtitleError",
    "FormatError",
    "ParseError",
    "UnsupportedFormatError",
    "InvalidTimeFormatError",
    "InvalidSubtitleContentError",
]
