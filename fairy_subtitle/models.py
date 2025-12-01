# fairy_script/models.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class Cue:
    """代表一个独立的字幕条目"""

    start: float  # 开始时间，单位秒
    end: float  # 结束时间，单位秒
    text: str  # 字幕文本
    index: Optional[int] = None  # SRT 的序号

    @property
    def duration(self) -> float:
        return self.end - self.start


@dataclass
class AssInfo:
    """ASS 字幕的信息"""

    script_Info: dict
    v4_Styles: dict
    events: dict
    fonts: dict


@dataclass
class SubtitleInfo:
    """代表字幕文件的基本信息"""

    path: str  # 字幕文件路径
    format: str  # 字幕格式
    duration: float  # 字幕文件的时长，单位秒
    size: int  # 字幕总数
    other_info: any = None  # 字幕文件的其他信息


@dataclass
class Subtitle:
    """代表一个完整的字幕文件"""

    cues: list[Cue]  # 字幕列表
    info: SubtitleInfo  # 字幕格式，目前支持 srt

    def __len__(self) -> int:
        return self.info.size

    def __getitem__(self, index: int) -> Cue:
        return self.cues[index]

    def __iter__(self):
        return iter(self.cues)

    def _recalculate_indices(self, index: int = 0):
        """重新计算 SRT 序号, 从 index 开始"""
        for i, cue in enumerate(self.cues, start=index):
            cue.index = i

    def _recalcluate_duration(self):
        """重新计算字幕文件的时长"""
        earliest_start = min(cue.start for cue in self.cues)
        latest_end = max(cue.end for cue in self.cues)
        self.info.duration = latest_end - earliest_start

    def show(self, index: int = None):
        """打印字幕内容"""
        if index is not None and index < 0 or index >= len(self.cues):
            raise IndexError("Index out of range")
        if self.format == "srt":
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
        """返回字幕格式"""
        return self.format

    def get_duration(self) -> float:
        """返回字幕文件的时长"""
        return self.info.duration

    def get_size(self) -> int:
        """返回字幕总数"""
        return self.info.size

    def get_other_info(self) -> any:
        """返回字幕文件的其他信息"""
        return self.info.other_info

    def get_path(self) -> str:
        """返回字幕文件路径"""
        return self.info.path

    def get_times(self) -> list[tuple[float, float]]:
        """返回所有字幕的开始和结束时间列表"""
        return [(cue.start, cue.end) for cue in self.cues]

    def get_start_times(self) -> list[float]:
        """返回所有字幕的开始时间列表"""
        return [cue.start for cue in self.cues]

    def get_end_times(self) -> list[float]:
        """返回所有字幕的结束时间列表"""
        return [cue.end for cue in self.cues]

    def get_texts(self) -> list[str]:
        """返回所有字幕的文本内容列表"""
        return [cue.text for cue in self.cues]

    def shift(self, offset: float):
        """将字幕文件中所有字幕的开始和结束时间都加上偏移量"""
        if offset == 0:
            return
        for cue in self.cues:
            cue.start += offset
            cue.end += offset

    def find(self, text: str):
        """返回所有包含指定文本的 Cue 对象列表"""
        return [cue for cue in self.cues if text in cue.text]

    def filter_by_time(self, start: float, end: float):
        """返回在指定时间区间内的字幕列表"""
        if start > end:
            start, end = end, start
        return [
            cue
            for cue in self.cues
            if start <= cue.start <= end or start <= cue.end <= end
        ]

    def merge(self, index1: int, index2: int):
        """就地修改。合并一个区间内的字幕块。"""
        if index1 < 0 or index2 >= len(self.cues) or index1 > index2:
            raise IndexError("Index out of range")
        if index1 == index2:
            return
        start_time = self.cues[index1].start
        end_time = self.cues[index2].end
        merged_text = "\n".join(cue.text for cue in self.cues[index1 : index2 + 1])
        merged_index = self.cues[index1].index
        merged_cue = Cue(
            start=start_time, end=end_time, text=merged_text, index=merged_index
        )
        self.cues[index1 : index2 + 1] = [merged_cue]
        self._recalculate_indices(index1)
        self._recalcluate_duration()

    def split(self, index: int, time: float):
        """就地修改。将指定字幕块分割成两个字幕块。"""
        if index < 0 or index >= len(self.cues):
            raise IndexError("Index out of range")
        if time < self.cues[index].start or time > self.cues[index].end:
            raise ValueError("Time is not within the cue")
        new_cue = Cue(start=time, end=self.cues[index].end, text=self.cues[index].text)
        self.cues[index].end = time
        self.cues.insert(index + 1, new_cue)
        self._recalculate_indices(index)

    def insert(self, index: int, cue: Cue):
        """就地修改。在指定位置插入一个字幕块。"""
        if index < 0 or index > len(self.cues):
            raise IndexError("Index out of range")
        self.cues.insert(index, cue)
        self._recalculate_indices(index)
        self._recalcluate_duration()

    def remove(self, index: int):
        """就地修改。删除指定位置的字幕块。"""
        if index < 0 or index >= len(self.cues):
            raise IndexError("Index out of range")
        self.cues.pop(index)
        self._recalculate_indices(index - 1)
        self._recalcluate_duration()
