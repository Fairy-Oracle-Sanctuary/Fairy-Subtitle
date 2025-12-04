# fairy_subtitle/models.py
# A simple and powerful Python subtitle parsing library

from dataclasses import dataclass
from typing import Optional


@dataclass
class Cue:
    """Represents an individual subtitle entry
    代表一个独立的字幕条目"""

    start: float  # Start time in seconds
    end: float  # End time in seconds
    text: str  # Subtitle text
    index: Optional[int] = None  # SRT index number

    @property
    def duration(self) -> float:
        """Returns the duration of the subtitle in seconds
        返回字幕的持续时间（秒）"""
        return self.end - self.start


@dataclass
class AssInfo:
    """ASS subtitle information
    ASS 字幕的信息"""

    script_Info: dict
    v4_Styles: dict
    events: dict
    fonts: dict
    graphics: dict  # 添加graphics字段


@dataclass
class SubtitleInfo:
    """Represents basic information about a subtitle file
    代表字幕文件的基本信息"""

    path: str  # Path to the subtitle file
    format: str  # Subtitle format
    duration: float  # Duration of the subtitle file in seconds
    size: int  # Total number of subtitles
    other_info: any = None  # Other information about the subtitle file


@dataclass
class Subtitle:
    """Represents a complete subtitle file
    代表一个完整的字幕文件"""

    cues: list[Cue]  # List of subtitles
    info: SubtitleInfo  # Subtitle information, currently supports srt

    def __len__(self) -> int:
        return self.info.size

    def __getitem__(self, index: int) -> Cue:
        return self.cues[index]

    def __iter__(self):
        return iter(self.cues)

    def _recalculate_indices(self, index: int = 0):
        """Recalculates SRT indices starting from the specified index
        重新计算 SRT 序号, 从 index 开始"""
        for i, cue in enumerate(self.cues, start=index):
            cue.index = i

    def _recalcluate_duration(self):
        """Recalculates the total duration of the subtitle file
        重新计算字幕文件的时长"""
        earliest_start = min(cue.start for cue in self.cues)
        latest_end = max(cue.end for cue in self.cues)
        self.info.duration = latest_end - earliest_start

    def show(self, index: int = None):
        """Prints subtitle content
        打印字幕内容"""
        if index is not None and index < 0 or index >= len(self.cues):
            raise IndexError("Index out of range")
        if self.info.format == "srt":
            if index is None:
                for cue in self.cues:
                    print(
                        f"{cue.index}\n{cue.start:.3f} --> {cue.end:.3f}\n{cue.text}\n"
                    )
            else:
                print(
                    f"{self.cues[index].index}\n{self.cues[index].start:.3f} --> {self.cues[index].end:.3f}\n{self.cues[index].text}\n"
                )

    def get_format(self) -> str:
        """Returns the subtitle format
        返回字幕格式"""
        return self.info.format

    def get_duration(self) -> float:
        """Returns the total duration of the subtitle file
        返回字幕文件的时长"""
        return self.info.duration

    def get_size(self) -> int:
        """Returns the total number of subtitles
        返回字幕总数"""
        return self.info.size

    def get_other_info(self) -> any:
        """Returns other information about the subtitle file
        返回字幕文件的其他信息"""
        return self.info.other_info

    def get_path(self) -> str:
        """Returns the path to the subtitle file
        返回字幕文件路径"""
        return self.info.path

    def get_times(self) -> list[tuple[float, float]]:
        """Returns a list of start and end times for all subtitles
        返回所有字幕的开始和结束时间列表"""
        return [(cue.start, cue.end) for cue in self.cues]

    def get_start_times(self) -> list[float]:
        """Returns a list of start times for all subtitles
        返回所有字幕的开始时间列表"""
        return [cue.start for cue in self.cues]

    def get_end_times(self) -> list[float]:
        """Returns a list of end times for all subtitles
        返回所有字幕的结束时间列表"""
        return [cue.end for cue in self.cues]

    def get_texts(self) -> list[str]:
        """Returns a list of text content for all subtitles
        返回所有字幕的文本内容列表"""
        return [cue.text for cue in self.cues]

    def shift(self, offset: float):
        """Shifts all subtitle start and end times by the specified offset
        将字幕文件中所有字幕的开始和结束时间都加上偏移量"""
        if offset == 0:
            return
        for cue in self.cues:
            cue.start += offset
            cue.end += offset

    def find(self, text: str):
        """Returns a list of Cue objects containing the specified text
        返回所有包含指定文本的 Cue 对象列表"""
        return [cue for cue in self.cues if text in cue.text]

    def filter_by_time(self, start: float, end: float):
        """Returns a list of subtitles within the specified time interval
        返回在指定时间区间内的字幕列表"""
        if start > end:
            start, end = end, start
        return [
            cue
            for cue in self.cues
            if start <= cue.start <= end or start <= cue.end <= end
        ]

    def merge(self, index1: int, index2: int):
        """In-place modification. Merges subtitles within a specified range.
        就地修改。合并一个区间内的字幕块。"""
        if index1 < 0 or index2 >= len(self.cues) or index1 > index2:
            raise IndexError("Index out of range")
        if index1 == index2:
            return
        start_time = self.cues[index1].start
        end_time = self.cues[index2].end
        merged_text = "\n".join(cue.text for cue in self.cues[index1 : index2 + 1])
        merged_cue = Cue(start=start_time, end=end_time, text=merged_text, index=None)
        self.cues[index1 : index2 + 1] = [merged_cue]
        self._recalculate_indices(index1)
        self._recalcluate_duration()

    def split(self, index: int, time: float):
        """In-place modification. Splits a specified subtitle into two.
        就地修改。将指定字幕块分割成两个字幕块。"""
        if index < 0 or index >= len(self.cues):
            raise IndexError("Index out of range")
        if time < self.cues[index].start or time > self.cues[index].end:
            raise ValueError("Time is not within the cue")
        new_cue = Cue(
            start=time, end=self.cues[index].end, text=self.cues[index].text, index=None
        )
        self.cues[index].end = time
        self.cues.insert(index + 1, new_cue)
        self._recalculate_indices(index)

    def insert(self, index: int, cue: Cue):
        """In-place modification. Inserts a subtitle at the specified position.
        就地修改。在指定位置插入一个字幕块。"""
        if index < 0 or index > len(self.cues):
            raise IndexError("Index out of range")
        cue.index = None  # 重置索引，让_recalculate_indices统一设置
        self.cues.insert(index, cue)
        self._recalculate_indices(index)
        self._recalcluate_duration()

    def remove(self, index: int):
        """In-place modification. Removes a subtitle at the specified position.
        就地修改。删除指定位置的字幕块。"""
        if index < 0 or index >= len(self.cues):
            raise IndexError("Index out of range")
        self.cues.pop(index)
        self._recalculate_indices(index - 1)
        self._recalcluate_duration()

    def to_dict(self) -> dict:
        """Converts a Subtitle object to a dictionary.
        将 Subtitle 对象转换为字典。"""
        return {
            "cues": [cue.to_dict() for cue in self.cues],
            "info": self.info.to_dict(),
        }

    def save(self, file_path: str, save_format: str = None) -> None:
        """
        Saves the subtitle to a file in the specified format.
        将字幕保存为指定格式的文件。

        Args:
            file_path (str): Path to save the file
            save_format (str): Format to save in, defaults to original format

        Raises:
            ValueError: If the specified format is not supported
        """
        # 如果没有指定格式，使用原始格式
        if save_format is None:
            save_format = self.info.format

        # 确保格式是小写
        save_format = save_format.lower()

        # 检查格式是否支持
        if save_format not in transform_functions:
            raise ValueError(f"不支持的格式: {save_format}")

        # 获取转换函数
        transform_func = transform_functions[save_format]

        # 转换字幕
        content = transform_func(self)

        # 保存到文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def to_srt(self) -> str:
        """Converts the subtitle to SRT format string.
        将字幕转换为 SRT 格式字符串。"""
        return to_srt(self)

    def to_vtt(self) -> str:
        """Converts the subtitle to VTT format string.
        将字幕转换为 VTT 格式字符串。"""
        return to_vtt(self)

    def to_ass(self) -> str:
        """Converts the subtitle to ASS format string.
        将字幕转换为 ASS 格式字符串。"""
        return to_ass(self)


# Internal helper functions for time formatting


def _format_srt_time(seconds: float) -> str:
    """Converts seconds to SRT format time string (HH:MM:SS,ms)
    将秒数转换为SRT格式时间字符串 (HH:MM:SS,ms)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_int = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds_int:02d},{milliseconds:03d}"


def _format_vtt_time(seconds: float) -> str:
    """Converts seconds to VTT format time string (HH:MM:SS.mmm)
    将秒数转换为VTT格式时间字符串 (HH:MM:SS.mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_int = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds_int:02d}.{milliseconds:03d}"


def _format_ass_time(seconds: float) -> str:
    """Converts seconds to ASS format time string (HH:MM:SS.ms)
    将秒数转换为ASS格式时间字符串 (HH:MM:SS.ms)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_int = int(seconds % 60)
    milliseconds = int((seconds % 1) * 100)
    return f"{hours:02d}:{minutes:02d}:{seconds_int:02d}.{milliseconds:02d}"


# Format conversion functions


def to_srt(subtitle: "Subtitle") -> str:
    """Converts Subtitle object to SRT format string
    将Subtitle对象转换为SRT格式字符串"""
    srt_content = []
    for i, cue in enumerate(subtitle.cues, 1):
        srt_content.append(str(i))
        start_time = _format_srt_time(cue.start)
        end_time = _format_srt_time(cue.end)
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(cue.text)
        srt_content.append("")  # 空行分隔字幕块
    return "\n".join(srt_content)


def to_vtt(subtitle: "Subtitle") -> str:
    """Converts Subtitle object to VTT format string
    将Subtitle对象转换为VTT格式字符串"""
    vtt_content = ["WEBVTT", ""]
    for i, cue in enumerate(subtitle.cues, 1):
        start_time = _format_vtt_time(cue.start)
        end_time = _format_vtt_time(cue.end)
        vtt_content.append(f"{start_time} --> {end_time}")
        vtt_content.append(cue.text)
        vtt_content.append("")  # 空行分隔字幕块
    return "\n".join(vtt_content)


def to_ass(subtitle: "Subtitle") -> str:
    """Converts Subtitle object to ASS format string
    将Subtitle对象转换为ASS格式字符串"""
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
transform_functions = {"srt": to_srt, "vtt": to_vtt, "ass": to_ass}
