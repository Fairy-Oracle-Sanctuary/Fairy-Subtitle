<h1 align="center">
  fairy-subtitle
</h1>

> A simple and powerful Python subtitle parsing library that supports parsing and processing of multiple subtitle formats.

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

## Features

- Supports multiple common subtitle formats: SRT, VTT, ASS, SUB, SBV
- Simple and easy-to-use API interface
- Flexible subtitle item operations (merge, split, insert, delete, etc.)
- Complete exception handling mechanism
- Support for format conversion and saving
- Pure Python implementation with no third-party dependencies

## Installation

```bash
pip install fairy-subtitle
```

## Quick Start

### Parse Subtitle Files

```python
from fairy_subtitle import SubtitleLoader

# Parse SRT file
subtitle = SubtitleLoader.load("example.srt")

# Parse VTT file
subtitle = SubtitleLoader.load("example.vtt")

# Parse ASS file
subtitle = SubtitleLoader.load("example.ass")

# Parse with specified format
subtitle = SubtitleLoader.load("example.txt", format="srt")
```

### Subtitle Operations

```python
# Get number of subtitles
print(f"Number of subtitles: {len(subtitle)}")

# Get subtitle duration
print(f"Subtitle duration: {subtitle.get_duration():.2f} seconds")

# Access subtitles
print(subtitle[0])  # First subtitle
print(subtitle[-1])  # Last subtitle

# Merge subtitles
subtitle.merge(0, 2)  # Merge subtitles from index 0 to 2

# Split subtitle
subtitle.split(0, 10.5)  # Split subtitle at index 0 at 10.5 seconds

# Insert subtitle
from fairy_subtitle.models import Cue
subtitle.insert(0, Cue(start=0.0, end=5.0, text="New subtitle"))

# Delete subtitle
subtitle.remove(0)  # Delete subtitle at index 0
```

### Search and Filter

```python
# Search for subtitles containing specific text
results = subtitle.find("keyword")

# Filter subtitles within specific time range
filtered = subtitle.filter_by_time(0, 100)
```

### Format Conversion and Saving

```python
# Convert to SRT format string
srt_content = subtitle.to_srt()

# Convert to VTT format string
vtt_content = subtitle.to_vtt()

# Convert to ASS format string
ass_content = subtitle.to_ass()

# Save as specified format
subtitle.save("output.vtt")  # Save in original format
subtitle.save("output.srt", save_format="srt")  # Save as SRT format
subtitle.save("output.ass", save_format="ass")  # Save as ASS format
```

## API Reference

### SubtitleLoader

#### `load(file_path: str, format: str = None) -> Subtitle`
Parse subtitle file and return Subtitle object.

- `file_path`: Subtitle file path
- `format`: Subtitle format (optional, auto-detected)

### Subtitle

#### Basic Properties

- `cues`: List of subtitles
- `info`: Subtitle information

#### Basic Methods

- `__len__()`: Return number of subtitles
- `__getitem__(index)`: Get subtitle at specified index
- `get_duration()`: Return total subtitle duration
- `merge(index1: int, index2: int)`: Merge subtitles
- `split(index: int, time: float)`: Split subtitle
- `insert(index: int, cue: Cue)`: Insert subtitle
- `remove(index: int)`: Delete subtitle
- `find(text: str) -> list[Cue]`: Search subtitles
- `filter_by_time(start: float, end: float) -> list[Cue]`: Filter subtitles
- `to_dict()`: Convert to dictionary
- `to_srt()`: Convert to SRT format
- `to_vtt()`: Convert to VTT format
- `to_ass()`: Convert to ASS format
- `save(file_path: str, save_format: str = None)`: Save subtitle

### Cue

#### Basic Properties

- `start`: Start time (seconds)
- `end`: End time (seconds)
- `text`: Subtitle text
- `index`: Subtitle index

#### Basic Methods

- `to_dict()`: Convert to dictionary

## License

This project is licensed under the MIT License - see the LICENSE file for details

## Contributing

Welcome to submit Issues and Pull Requests!

## Feedback

If you encounter any issues during use, please submit an Issue on GitHub:

[https://github.com/baby2016/fairy-subtitle/issues]