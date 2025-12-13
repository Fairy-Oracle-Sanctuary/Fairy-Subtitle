<h1 align="center">
  fairy-subtitle
</h1>

> 一个简单而强大的Python字幕解析库，支持多种字幕格式的解析和处理。

<p align="center">

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/LICENSE-MIT-green" alt="LICENSE MIT"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/Python-3.9+-blue" alt="Python 3.9+"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/Version-1.1.0-blue.svg" alt="Version 1.1.0"/>
  </a>
</p>


<p align="center">
<a href="https://github.com/Fairy-Oracle-Sanctuary/Fairy-Subtitle/blob/main/README.md">简体中文</a> | <a href="https://github.com/Fairy-Oracle-Sanctuary/Fairy-Subtitle/blob/main/README.en.md">English</a>
</p>

## 特性

- 支持多种常见字幕格式：SRT、VTT、ASS、SUB、SBV
- 简单易用的API接口
- 灵活的字幕项操作（合并、分割、插入、删除等）
- 完整的异常处理机制
- 支持格式转换和保存
- 纯Python实现，无第三方依赖

## 安装

```bash
pip install fairy-subtitle
```

## 快速开始

### 解析字幕文件

```python
from fairy_subtitle import SubtitleLoader

# 解析SRT文件
subtitle = SubtitleLoader.load("example.srt")

# 解析VTT文件
subtitle = SubtitleLoader.load("example.vtt")

# 解析ASS文件
subtitle = SubtitleLoader.load("example.ass")

# 指定格式解析
subtitle = SubtitleLoader.load("example.txt", format="srt")
```

### 字幕操作

```python
# 获取字幕数量
print(f"字幕数量: {len(subtitle)}")

# 获取字幕时长
print(f"字幕时长: {subtitle.get_duration():.2f}秒")

# 访问字幕
print(subtitle[0])  # 第一个字幕
print(subtitle[-1])  # 最后一个字幕

# 合并字幕
subtitle.merge(0, 2)  # 合并第0到第2个字幕

# 分割字幕
subtitle.split(0, 10.5)  # 在10.5秒处分割第0个字幕

# 插入字幕
from fairy_subtitle.models import Cue
subtitle.insert(0, Cue(start=0.0, end=5.0, text="新字幕"))

# 删除字幕
subtitle.remove(0)  # 删除第0个字幕
```

### 搜索和过滤

```python
# 搜索包含特定文本的字幕
results = subtitle.find("关键词")

# 过滤特定时间范围内的字幕
filtered = subtitle.filter_by_time(0, 100)
```

### 格式转换和保存

```python
# 转换为SRT格式字符串
srt_content = subtitle.to_srt()

# 转换为VTT格式字符串
vtt_content = subtitle.to_vtt()

# 转换为ASS格式字符串
ass_content = subtitle.to_ass()

# 保存为指定格式
subtitle.save("output.vtt")  # 保存为原始格式
subtitle.save("output.srt", save_format="srt")  # 保存为SRT格式
subtitle.save("output.ass", save_format="ass")  # 保存为ASS格式
```

## API参考

### SubtitleLoader

#### `load(file_path: str, format: str = None) -> Subtitle`
解析字幕文件并返回Subtitle对象。

- `file_path`: 字幕文件路径
- `format`: 字幕格式（可选，自动检测）

### Subtitle

#### 基本属性

- `cues`: 字幕列表
- `info`: 字幕信息

#### 基本方法

- `__len__()`: 返回字幕数量
- `__getitem__(index)`: 获取指定索引的字幕
- `get_duration()`: 返回字幕总时长
- `merge(index1: int, index2: int)`: 合并字幕
- `split(index: int, time: float)`: 分割字幕
- `insert(index: int, cue: Cue)`: 插入字幕
- `remove(index: int)`: 删除字幕
- `find(text: str) -> list[Cue]`: 搜索字幕
- `filter_by_time(start: float, end: float) -> list[Cue]`: 过滤字幕
- `to_dict()`: 转换为字典
- `to_srt()`: 转换为SRT格式
- `to_vtt()`: 转换为VTT格式
- `to_ass()`: 转换为ASS格式
- `save(file_path: str, save_format: str = None)`: 保存字幕

### Cue

#### 基本属性

- `start`: 开始时间（秒）
- `end`: 结束时间（秒）
- `text`: 字幕文本
- `index`: 字幕索引

#### 基本方法

- `to_dict()`: 转换为字典

## 许可证

本项目采用MIT许可证 - 详情请查看LICENSE文件

## 贡献

欢迎提交Issue和Pull Request！

## 问题反馈

如果您在使用过程中遇到问题，请在GitHub上提交Issue：

[https://github.com/baby2016/fairy-subtitle/issues]