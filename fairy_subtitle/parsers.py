# fairy_script/parsers.py

import re

from fairy_subtitle.block import ass_script_info
from fairy_subtitle.exceptions import (
    InvalidSubtitleContentError,
    InvalidTimeFormatError,
)
from fairy_subtitle.models import AssInfo, Cue, Subtitle, SubtitleInfo


def _parse_srt_time(time_str: str) -> float:
    """将 'HH:MM:SS,ms' 格式的时间转换为秒数 (float)
    Convert 'HH:MM:SS,ms' format time to seconds (float)
    """
    h, m, s_ms = time_str.split(":")
    s, ms = s_ms.split(",")
    total_seconds = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    return float(total_seconds)


def parse_srt(file_path: str, content: str) -> Subtitle:
    """
    解析 SRT 格式的文本内容，并返回一个 Subtitle 对象。
    Parse SRT format text content and return a Subtitle object.
    """
    cues = []
    # SRT 字幕块之间由两个或更多的换行符分隔
    blocks = re.split(r"\n\s*\n", content)

    earliest_start_time = float("inf")
    latest_end_time = 0
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            raise InvalidSubtitleContentError(f"无效的字幕块，行数不足3行:\n{block}")

        try:
            # 1. 解析序号
            index = int(lines[0]) - 1

            # 2. 解析时间轴
            time_str = lines[1]
            start_str, end_str = time_str.split(" --> ")
            start_time = _parse_srt_time(start_str)
            end_time = _parse_srt_time(end_str)
            earliest_start_time = min(earliest_start_time, start_time)
            latest_end_time = max(latest_end_time, end_time)

            # 3. 解析文本 (可能有多行)
            text = "\n".join(lines[2:])

            # 4. 创建 Cue 对象并添加到列表
            cue = Cue(start=start_time, end=end_time, text=text, index=index)
            cues.append(cue)

        except (ValueError, IndexError) as e:
            if "unpack" in str(e):
                raise InvalidTimeFormatError(f"时间格式错误: {time_str}")
            elif "int" in str(e):
                raise InvalidSubtitleContentError(f"序号格式错误: {lines[0]}")
            else:
                raise InvalidSubtitleContentError(f"解析字幕块失败: {e}")
        except IndexError as e:
            raise InvalidSubtitleContentError(f"字幕块索引错误: {e}")

        # 5. 创建 SubtitleInfo 对象
        info = SubtitleInfo(
            path=file_path,
            format="srt",
            duration=latest_end_time - earliest_start_time,
            size=len(cues),
            other_info=None,
        )

    return Subtitle(cues=cues, info=info)


def _parse_ass_time(time_str: str) -> float:
    """将 'HH:MM:SS,ms' 格式的时间转换为秒数 (float)
    Convert 'HH:MM:SS,ms' format time to seconds (float)
    """
    h, m, s_ms = time_str.split(":")
    s, ms = s_ms.split(".")
    total_seconds = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    return float(total_seconds)


def parse_ass_script_info(content: str) -> dict:
    """
    解析 ASS 格式的 [Script Info] 部分，并返回一个字典。
    Parse the [Script Info] section of ASS format and return a dictionary.
    """
    script_info = {}
    script_info_set = set(ass_script_info)  # 集合查找速度为O(1)
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("!:"):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key in script_info_set:
                script_info[key] = value

    return script_info


def parse_ass_v4_style(content: str) -> dict:
    """
    解析 ASS 格式的 [V4+ Styles] 部分，并返回一个字典。
    Parse the [V4+ Styles] section of ASS format and return a dictionary.
    """
    v4_style = {}

    read_v4_styles = list(filter(None, content.split("\n")))
    read_styles_format = read_v4_styles[0].split(":", 1)[-1].split(",")

    format = []
    style_name_index = 0
    for index, format_item in enumerate(read_styles_format):
        format.append(format_item.strip())
        if format_item.strip() == "Name":
            style_name_index = index
    v4_style["Format"] = format

    for style_items in read_v4_styles[1:]:
        style_item = style_items.split(":", 1)[-1].split(",")
        style_list = []
        style_name = ""
        for index, item in enumerate(style_item):
            style_list.append(item.strip())
            if index == style_name_index:
                style_name = item.strip()
        v4_style[style_name] = style_list

    return v4_style


def parse_ass_events(content: str) -> tuple[dict, list[Cue], float]:
    """
    解析 ASS 格式的 [Events] 部分。
    Parse the [Events] section of ASS format.
    """
    events = {}

    # 一次性分割所有行并过滤空行
    read_events = [line.strip() for line in content.split("\n") if line.strip()]

    # 解析格式行
    if not read_events:
        return events, [], 0.0

    format_line = read_events[0]
    # 一次性分割并提取格式字段
    format_items = format_line.split(":", 1)[-1].split(",")

    # 预计算并缓存关键索引位置
    format_mapping = {}
    text_index = 9
    start_index = 1
    end_index = 2

    for idx, item in enumerate(format_items):
        item_stripped = item.strip()
        format_mapping[item_stripped] = idx
        if item_stripped == "Text":
            text_index = idx
        elif item_stripped == "Start":
            start_index = idx
        elif item_stripped == "End":
            end_index = idx

    # 存储格式列表
    events["Format"] = [item.strip() for item in format_items]

    # 初始化变量
    earliest_start_time = float("inf")
    latest_end_time = 0.0
    text_dialogue = []
    text_comment = []
    cues = []

    # 处理每一行事件数据
    for i, line in enumerate(read_events[1:], 0):
        # 只分割一次获取类型和数据部分
        if ":" in line:
            event_type, data_part = line.split(":", 1)
            event_type = event_type.strip()

            # 分割数据部分
            data_items = data_part.split(",")

            # 确保索引有效
            if (
                text_index < len(data_items)
                and start_index < len(data_items)
                and end_index < len(data_items)
            ):
                # 直接获取所需字段
                text = data_items[text_index].strip()

                try:
                    # 解析时间
                    start_time = _parse_ass_time(data_items[start_index].strip())
                    end_time = _parse_ass_time(data_items[end_index].strip())

                    # 更新时间范围
                    earliest_start_time = min(earliest_start_time, start_time)
                    latest_end_time = max(latest_end_time, end_time)

                    # 创建Cue对象
                    cue = Cue(start=start_time, end=end_time, text=text, index=i)
                    cues.append(cue)

                    # 根据类型存储数据
                    stripped_items = [item.strip() for item in data_items]
                    if event_type == "Dialogue":
                        text_dialogue.append(stripped_items)
                    elif event_type == "Comment":
                        text_comment.append(stripped_items)
                except Exception:
                    # 忽略解析失败的行，继续处理其他行
                    continue

    events["Dialogue"] = text_dialogue
    events["Comment"] = text_comment
    duration = latest_end_time - earliest_start_time if cues else 0.0

    return events, cues, duration


def parse_ass_fonts(content: str) -> dict:
    """
    解析 ASS 格式的 [Fonts] 部分，并返回一个字典。
    Parse the [Fonts] section of ASS format and return a dictionary.
    """
    fonts = []
    for line in content.split("\n"):
        line = line.strip()
        if line and not line.startswith("!"):
            fonts.append(line)
    return {"fonts": fonts}


def parse_ass_graphics(content: str) -> dict:
    """
    解析 ASS 格式的 [Graphics] 部分，并返回一个字典。
    Parse the [Graphics] section of ASS format and return a dictionary.
    """
    graphics = []
    for line in content.split("\n"):
        line = line.strip()
        if line and not line.startswith("!"):
            graphics.append(line)
    return {"graphics": graphics}


def parse_ass(file_path: str, content: str) -> Subtitle:
    """
    解析 ASS 格式的文本内容，并返回一个 Subtitle 对象。
    组成:
        [Script Info]
        [V4+ Styles]
        [Events]
        [fonts]
        [Graphics]
    Parse ASS format text content and return a Subtitle object.
    Components:
        [Script Info]
        [V4+ Styles]
        [Events]
        [fonts]
        [Graphics]
    """

    # 使用正则表达式分割各个部分
    parts = {}
    current_part = None
    current_content = []

    for line in content.split("\n"):
        # 检查是否是新的部分开始
        if line.strip().startswith("[") and line.strip().endswith("]"):
            # 如果有当前部分，保存它
            if current_part is not None:
                parts[current_part] = "\n".join(current_content)
            # 开始新的部分
            current_part = line.strip()
            current_content = []
        else:
            if current_part is not None:
                current_content.append(line)

    # 保存最后一个部分
    if current_part is not None:
        parts[current_part] = "\n".join(current_content)

    # 初始化默认值
    script_info = {}
    v4_style = {}
    events = {}
    cues = []
    duration = 0.0
    fonts = {}
    graphics = {}

    # 解析各个部分
    if "[Script Info]" in parts:
        script_info = parse_ass_script_info(parts["[Script Info]"])

    if "[V4+ Styles]" in parts:
        v4_style = parse_ass_v4_style(parts["[V4+ Styles]"])

    if "[Events]" in parts:
        events, cues, duration = parse_ass_events(parts["[Events]"])

    if "[Fonts]" in parts:
        fonts = parse_ass_fonts(parts["[Fonts]"])

    if "[Graphics]" in parts:
        graphics = parse_ass_graphics(parts["[Graphics]"])

    # 创建 AssInfo 对象
    ass_info = AssInfo(
        script_Info=script_info,
        v4_Styles=v4_style,
        events=events,
        fonts=fonts,
        graphics=graphics,
    )

    # 创建 SubtitleInfo 对象
    info = SubtitleInfo(
        path=file_path,
        format="ass",
        duration=duration,
        size=len(cues),
        other_info=ass_info,
    )

    return Subtitle(cues=cues, info=info)


def _parse_vtt_time(time_str: str) -> float:
    """将 VTT 格式的时间字符串转换为秒数 (float)
    Convert VTT format time string to seconds (float)
    """
    # VTT 格式: 00:00:00.000 或 00:00.000
    parts = time_str.split(":")
    if len(parts) == 2:
        # MM:SS.mmm 格式
        minutes, seconds_ms = parts
        hours = 0
    elif len(parts) == 3:
        # HH:MM:SS.mmm 格式
        hours, minutes, seconds_ms = parts
    else:
        raise InvalidTimeFormatError(f"无效的 VTT 时间格式: {time_str}")

    seconds, ms = seconds_ms.split(".")
    total_seconds = (
        int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(ms) / 1000
    )
    return float(total_seconds)


def parse_vtt(file_path: str, content: str) -> Subtitle:
    """
    解析 VTT 格式的文本内容，并返回一个 Subtitle 对象。
    Parse VTT format text content and return a Subtitle object.
    """
    cues = []
    earliest_start_time = float("inf")
    latest_end_time = 0.0

    # 处理BOM
    if content.startswith("\ufeff"):
        content = content[1:]

    # 定义时间戳的正则表达式
    timestamp_pattern = re.compile(
        r"(\d{2}:\d{2}:\d{2}\.\d{3}|\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3}|\d{2}:\d{2}\.\d{3})"
    )

    # 分割字幕块 (使用两个或更多的换行符作为分隔符)
    blocks = re.split(r"\n\s*\n", content)

    for block in blocks:
        # 跳过空块
        if not block.strip():
            continue

        # 跳过WEBVTT头部和注释块
        if (
            block.strip() == "WEBVTT"
            or block.strip().startswith("NOTE")
            or block.strip().startswith("STYLE")
        ):
            continue

        # 在块中查找时间戳
        timestamp_match = timestamp_pattern.search(block)
        if timestamp_match:
            try:
                # 提取开始和结束时间
                start_time_str = timestamp_match.group(1)
                end_time_str = timestamp_match.group(2)

                # 转换时间
                start_time = _parse_vtt_time(start_time_str)
                end_time = _parse_vtt_time(end_time_str)

                # 提取字幕文本 (时间戳后面的部分)
                lines = block.split("\n")
                text_lines = []
                found_timestamp = False

                for line in lines:
                    if timestamp_pattern.search(line):
                        found_timestamp = True
                        continue
                    # 跳过序号行 (数字行)
                    if (
                        found_timestamp
                        and not re.match(r"^\s*\d+\s*$", line)
                        and line.strip()
                    ):
                        text_lines.append(line.strip())

                # 如果有文本内容，创建字幕
                if text_lines:
                    text = "\n".join(text_lines)
                    cue = Cue(start=start_time, end=end_time, text=text, index=None)
                    cues.append(cue)

                    # 更新时间范围
                    earliest_start_time = min(earliest_start_time, start_time)
                    latest_end_time = max(latest_end_time, end_time)

            except Exception:
                # 忽略解析失败的块
                continue

    # 设置索引
    for i, cue in enumerate(cues):
        cue.index = i

    # 计算时长
    duration = latest_end_time - earliest_start_time if cues else 0.0

    # 创建 SubtitleInfo 对象
    info = SubtitleInfo(
        path=file_path,
        format="vtt",
        duration=duration,
        size=len(cues),
        other_info=None,
    )

    return Subtitle(cues=cues, info=info)


def _parse_srt_time(time_str: str) -> float:
    """将 'HH:MM:SS,ms' 格式的时间转换为秒数 (float)"""
    h, m, s_ms = time_str.split(":")
    s, ms = s_ms.split(",")
    total_seconds = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    return float(total_seconds)


def _parse_ass_time(time_str: str) -> float:
    """将 'HH:MM:SS,ms' 格式的时间转换为秒数 (float)"""
    h, m, s_ms = time_str.split(":")
    s, ms = s_ms.split(".")
    total_seconds = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    return float(total_seconds)


def _parse_vtt_time(time_str: str) -> float:
    """将 VTT 格式的时间字符串转换为秒数 (float)"""
    # VTT 格式: 00:00:00.000 或 00:00.000
    parts = time_str.split(":")
    if len(parts) == 2:
        # MM:SS.mmm 格式
        minutes, seconds_ms = parts
        hours = 0
    elif len(parts) == 3:
        # HH:MM:SS.mmm 格式
        hours, minutes, seconds_ms = parts
    else:
        raise InvalidTimeFormatError(f"无效的 VTT 时间格式: {time_str}")

    seconds, ms = seconds_ms.split(".")
    total_seconds = (
        int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(ms) / 1000
    )
    return float(total_seconds)


# 时间格式转换函数
def _format_srt_time(seconds: float) -> str:
    """将秒数转换为SRT格式时间字符串 (HH:MM:SS,ms)
    Convert seconds to SRT format time string (HH:MM:SS,ms)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_int = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds_int:02d},{milliseconds:03d}"


def _format_vtt_time(seconds: float) -> str:
    """将秒数转换为VTT格式时间字符串 (HH:MM:SS.mmm)
    Convert seconds to VTT format time string (HH:MM:SS.mmm)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_int = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds_int:02d}.{milliseconds:03d}"


def _format_ass_time(seconds: float) -> str:
    """将秒数转换为ASS格式时间字符串 (HH:MM:SS.ms)
    Convert seconds to ASS format time string (HH:MM:SS.ms)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_int = int(seconds % 60)
    milliseconds = int((seconds % 1) * 100)
    return f"{hours:02d}:{minutes:02d}:{seconds_int:02d}.{milliseconds:02d}"


# 格式转换函数
def to_srt(subtitle: Subtitle) -> str:
    """将Subtitle对象转换为SRT格式字符串
    Convert Subtitle object to SRT format string
    """
    srt_content = []
    for i, cue in enumerate(subtitle.cues, 1):
        srt_content.append(str(i))
        start_time = _format_srt_time(cue.start)
        end_time = _format_srt_time(cue.end)
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(cue.text)
        srt_content.append("")  # 空行分隔字幕块
    return "\n".join(srt_content)


def to_vtt(subtitle: Subtitle) -> str:
    """将Subtitle对象转换为VTT格式字符串
    Convert Subtitle object to VTT format string
    """
    vtt_content = ["WEBVTT", ""]
    for i, cue in enumerate(subtitle.cues, 1):
        start_time = _format_vtt_time(cue.start)
        end_time = _format_vtt_time(cue.end)
        vtt_content.append(f"{start_time} --> {end_time}")
        vtt_content.append(cue.text)
        vtt_content.append("")  # 空行分隔字幕块
    return "\n".join(vtt_content)


def to_ass(subtitle: Subtitle) -> str:
    """将Subtitle对象转换为ASS格式字符串
    Convert Subtitle object to ASS format string
    """
    ass_content = [
        "[Script Info]",
        "Title: Converted Subtitle",
        "ScriptType: v4.00+",
        "PlayResX: 1920",
        "PlayResY: 1080",
        "Aspect Ratio: 16:9",
        "Collisions: Normal",
        "Timer: 100.0000",
        "WrapStyle: 0",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,0",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    for i, cue in enumerate(subtitle.cues, 1):
        start_time = _format_ass_time(cue.start)
        end_time = _format_ass_time(cue.end)
        # 简单转换，只保留文本内容
        text = cue.text.replace("\n", "\\N")
        ass_content.append(
            f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}"
        )

    return "\n".join(ass_content)


# 转换函数映射
# Transform function mapping
transform_functions = {"srt": to_srt, "vtt": to_vtt, "ass": to_ass}
