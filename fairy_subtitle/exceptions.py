"""
fairy-subtitle 自定义异常类模块

提供专门用于字幕处理的异常类，使错误处理更加清晰和结构化。
"""


class SubtitleError(Exception):
    """字幕处理相关错误的基类"""

    pass


class FormatError(SubtitleError):
    """字幕格式相关错误"""

    pass


class ParseError(SubtitleError):
    """字幕解析错误"""

    pass


class UnsupportedFormatError(FormatError):
    """不支持的字幕格式"""

    pass


class InvalidTimeFormatError(ParseError):
    """无效的时间格式"""

    pass


class InvalidSubtitleContentError(ParseError):
    """无效的字幕内容"""

    pass
