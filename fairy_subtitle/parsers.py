# fairy_script/parsers.py

import re

from fairy_subtitle.block import ass_script_info
from fairy_subtitle.exceptions import (
    InvalidSubtitleContentError,
    InvalidTimeFormatError,
)
from fairy_subtitle.models import AssInfo, Cue, Subtitle, SubtitleInfo


def _parse_srt_time(time_str: str) -> float:
    """将 'HH:MM:SS,ms' 格式的时间转换为秒数 (float)"""
    h, m, s_ms = time_str.split(":")
    s, ms = s_ms.split(",")
    total_seconds = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    return float(total_seconds)


def parse_srt(file_path: str, content: str) -> Subtitle:
    """
    解析 SRT 格式的文本内容，并返回一个 Subtitle 对象。
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
    """将 'HH:MM:SS,ms' 格式的时间转换为秒数 (float)"""
    h, m, s_ms = time_str.split(":")
    s, ms = s_ms.split(".")
    total_seconds = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    return float(total_seconds)


def parse_ass_script_info(content: str) -> dict:
    """
    解析 ASS 格式的 [Script Info] 部分，并返回一个字典。
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


def parse_ass(file_path: str, content: str) -> Subtitle:
    """
    解析 ASS 格式的文本内容，并返回一个 Subtitle 对象。
    组成:
        [Script Info]
        [V4+ Styles]
        [Events]
        [fonts]
        [Graphics]
    """

    # part_names = [
    #     "[Script Info]",
    #     "[V4+ Styles]",
    #     "[Events]",
    #     "[fonts]",
    # ]

    # ASS 字幕块之间由[]来分隔
    blocks = re.split(r"\[.*?\]", content)[1:]

    # [Script Info]
    script_info = parse_ass_script_info(blocks[0])

    # [V4+ Styles]
    v4_style = parse_ass_v4_style(blocks[1])

    # [Events]
    events, cues, duration = parse_ass_events(blocks[2])

    ass_info = AssInfo(
        script_Info=script_info, v4_Styles=v4_style, events=events, fonts=dict()
    )
    info = SubtitleInfo(
        path=file_path,
        format="ass",
        duration=duration,
        size=len(cues),
        other_info=ass_info,
    )

    return Subtitle(cues=cues, info=info)
