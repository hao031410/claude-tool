# ASR - 语音识别技能

基于 ModelScope 的语音识别技能，将音频文件转写为字幕。

## 功能特性

- 支持主流音频格式：WAV/MP3/M4A/FLAC/OGG/AAC
- 自动音频转码和分段（5-10秒/段）
- 多种输出格式：SRT/VTT/JSON
- 支持中文/英文识别
- 多平台扩展设计：ModelScope（已实现）、百炼（预留）、火山（预留）
- 配置优先级：环境变量 > `.env` > 默认值

## 安装

### 依赖

```bash
# 安装 ffmpeg
macOS:
brew install ffmpeg

Ubuntu/Debian:
sudo apt install ffmpeg
```

### Python 依赖

```bash
cd skills/asr
pip install -r requirements.txt
```

## 配置

在项目根目录创建 `.env` 文件：

```bash
# ModelScope API Key（必填）
MODELSCOPE_API_KEY=your-api-key-here

# 可选：其他平台
# BAILIAN_API_KEY=your-bailian-key
# VOLCANO_API_KEY=your-volcano-key

# 默认配置
ASR_DEFAULT_PROVIDER=modelscope
ASR_DEFAULT_MODEL=paraformer-v2
ASR_DEFAULT_LANGUAGE=zh
ASR_DEFAULT_OUTPUT_FORMAT=srt
ASR_SEGMENT_DURATION=10
```

**获取 ModelScope API Key：**
1. 访问 [ModelScope](https://modelscope.cn/)
2. 注册/登录账号
3. 在个人设置中获取 API Key

## 使用

### 命令行

```bash
# 基本用法（使用默认配置）
./bin/asr input.mp3

# 指定输出格式
./bin/asr input.mp3 --format vtt

# 指定语言
./bin/asr input.mp3 --language en

# 指定分段时长
./bin/asr input.mp3 --segment-duration 5

# 详细日志
./bin/asr input.mp3 --verbose
```

### Python API

```python
from asr.src.core import load_config, ASRCore

# 加载配置
config = load_config()

# 创建处理器
asr = ASRCore(config)

# 识别
output_path = asr.transcribe(
    "input.mp3",
    output_format="srt",
    language="zh",
    segment_duration=10,
)

print(f"Output: {output_path}")
```

## 模型选择

ModelScope 推荐模型：

| 模型 | 模型 ID | 特点 |
|------|---------|------|
| paraformer-v2 | damo/speech_paraformer-v2 | 默认推荐，平衡准确率与速度 |
| paraformer-zh | damo/speech_paraformer-zh | 中文专用，中英混合识别更准 |
| paraformer-large | damo/speech_paraformer-large-vad-punc | 高精度，带标点恢复、语音活动检测 |

在 `.env` 中设置：
```bash
ASR_DEFAULT_MODEL=paraformer-large
```

## 输出格式

### SRT（推荐）

```
1
00:00:00,000 --> 00:00:05,200
这是第一段字幕

2
00:00:05,200 --> 00:00:12,500
这是第二段字幕
```

### JSON

```json
[
  {
    "start_sec": 0.0,
    "end_sec": 5.2,
    "text": "这是第一段字幕"
  },
  {
    "start_sec": 5.2,
    "end_sec": 12.5,
    "text": "这是第二段字幕"
  }
]
```

## 架构

```
asr/
├── SKILL.md              # 技能规范
├── README.md             # 使用说明
├── requirements.txt      # Python 依赖
├── bin/
│   └── asr              # 命令行入口
└── src/
    ├── __init__.py
    ├── core.py           # 核心流程
    ├── providers/        # 多平台实现
    │   ├── __init__.py
    │   ├── base.py       # 抽象基类
    │   ├── modelscope.py # ModelScope 实现
    │   ├── bailian.py    # 百炼（预留）
    │   └── volcano.py    # 火山（预留）
    ├── audio/            # 音频处理
    │   ├── __init__.py
    │   ├── converter.py  # 格式转换
    │   └── splitter.py   # 分段
    └── output/           # 输出格式
        ├── __init__.py
        ├── srt.py        # SRT
        ├── vtt.py        # VTT
        └── json.py       # JSON
```

## 扩展新平台

1. 在 `src/providers/` 新建文件，继承 `ASRProvider`
2. 实现 `transcribe()` 和 `transcribe_batch()`
3. 在 `src/core.py` 的 `PROVIDERS` 字典中添加

## License

MIT
