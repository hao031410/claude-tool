---
name: asr
description: Use when needing automatic speech recognition (语音识别) to transcribe audio files to text or generate subtitles (字幕生成). Trigger words: 语音转文字, 字幕提取, 音频转文字, 语音识别, asr, 字幕生成, 音频转写.
---

# ASR 语音识别技能

## Overview

基于 ModelScope 语音识别，支持多种音频格式转换，输出标准字幕格式。

## When to Use

```dot
digraph use_flow {
    "User needs audio transcription?" [shape=diamond];
    "Need subtitles?" [shape=diamond];
    "Use asr skill" [shape=box];
    "Another solution" [shape=box];
    
    "User needs audio transcription?" -> "Need subtitles?" [label="yes"];
    "User needs audio transcription?" -> "Another solution" [label="no"];
    "Need subtitles?" -> "Use asr skill" [label="yes"];
    "Need subtitles?" -> "Use asr skill" [label="yes (text only];
}
```

**Use when:
- 用户需要将音频文件转写为文字
- 需要生成视频字幕（SRT/VTT 格式）
- 需要批量处理音频文件
- 需要 JSON 格式的语音识别结果

**When NOT to use:**
- 实时麦克风录音（目前只处理文件）
- 大模型语音合成（TTS）

## 触发词：`语音转文字` `音频转文字 `字幕生成 `asr `语音识别

## Workflow

```
Step 0: 配置检查
    ↓
Step 1: 参数收集（音频路径、语言、输出格式）
    ↓
Step 2: 执行识别流程
    ↓
Step 3: 输出结果文件
```

## Step 0: 配置检查

用户需要在项目根目录 `.env` 中配置：
```bash
# 必需：ModelScope API Key
MODELSCOPE_API_KEY=xxx
```

优先级规则：
1. **系统环境变量优先级最高**（`EXPORT 方式）
2. 其次读取 `.env` 文件配置
3. 使用默认值作为回退

如果未找到 API Key，必须立即终止并提示用户配置。

## Step 1: 参数收集（必选

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `audio_path` | 音频文件路径 | 必填 |
| `language` | 识别语言 (zh/en/auto) | `zh` |
| `output_format` | 输出格式 (srt/vtt/json) | `srt` |
| `segment_duration` | 分段时长（秒） | `10` |
| `speaker_diarization` | 说话人分离 | `false` |

**确认规则：** 路径必须确认，默认参数不需要确认。

## Step 2: 执行识别流程

1. **音频预处理**：
   - 使用 ffmpeg 转码为 WAV（PCM 16kHz 单声道
   - 按 `segment_duration` 分段

2. **API 调用：
   - 调用 ModelScope ASR API
   - 获取识别结果（包含时间戳）

3. **后处理：
   - 时间戳对齐
   - 语义分段
   - 生成目标格式

4. **输出：
   - 写入文件到原音频同目录
   - 文件名：`input.srt` 或 `input.json`

## Supported Formats

**Input:**
- WAV, MP3, M4A, FLAC, OGG, AAC

**Output:**
| 格式 | 优先级 | 用途 |
|------|----------|------|
| SRT | 最高 | 视频字幕，兼容绝大多数播放器 |
| VTT | 兼容 | Web 视频，HTML5 播放器 |
| JSON | 程序 | 二次开发，结构化数据 |

## Model Recommendations

**推荐模型 (ModelScope):**

| 模型 | 用途 | 特点 |
|------|------|------|
| `paraformer-v2` | 默认 | 中文准确率高，速度平衡 |
| `paraformer-zh` | 中文专用 | 中英混合识别优秀 |
| `speech_paraformer-large-vad-punc` | 高精度 | 带标点恢复，降噪 |

**可通过配置选择模型：** `ASR_DEFAULT_MODEL=paraformer-zh`

## 代码结构

```
src/
├── core.py          # 核心识别流程
├── providers/
│   ├── base.py      # 抽象基类
│   └── modelscope.py # ModelScope 实现
├── audio/
│   ├── converter.py # 音频转码
│   └── splitter.py  # 音频分段
└── output/
    ├── srt.py       # SRT 生成
    ├── vtt.py       # VTT 生成
    └── json.py      # JSON 生成
```

## Common Mistakes

| 错误 | 修复 |
|------|------|
| ffmpeg 未安装 | 提示用户安装 `brew install ffmpeg` 或 `apt install ffmpeg` |
| API Key 未配置 | 立即终止提示，不要继续执行 |
| 音频采样率不匹配 | 统一转码为 16kHz，不需要用户处理 |

## Important Constraints

1. **ffmpeg 依赖必须存在** - 需要音频转码
2. **API Key 必须配置** - 需要 ModelScope API
3. **配置优先级** - 环境变量 > `.env` > 默认值
4. **输出格式** - SRT 优先，兼容 VTT/JSON

## 多平台扩展

预留了 Provider 抽象接口，后续扩展：
- `bailian` - 阿里云百炼
- `volcano` - 字节火山引擎
- `openai` - OpenAI Whisper

每个平台实现 `ASRProvider 抽象接口即可接入。
