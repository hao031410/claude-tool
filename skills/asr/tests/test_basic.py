"""基础功能测试"""

import pytest
from pathlib import Path

from asr.src.core import load_config
from asr.src.audio.converter import AudioConverter
from asr.src.output.srt import SRTWriter
from asr.src.output.vtt import VTTWriter
from asr.src.output.json import JSONWriter


def test_ffmpeg_installed():
    """测试 ffmpeg 是否安装"""
    assert AudioConverter.check_ffmpeg() is True


def test_srt_format_timestamp():
    """测试 SRT 时间戳格式化"""
    cases = [
        (0.0, "00:00:00,000"),
        (5.2, "00:00:05,200"),
        (61.5, "00:01:01,500"),
        (3661.123, "01:01:01,123"),
    ]
    for seconds, expected in cases:
        assert SRTWriter.format_timestamp(seconds) == expected


def test_vtt_format_timestamp():
    """测试 VTT 时间戳格式化"""
    cases = [
        (0.0, "00:00:00.000"),
        (5.2, "00:00:05.200"),
    ]
    for seconds, expected in cases:
        assert VTTWriter.format_timestamp(seconds) == expected


def test_srt_write(tmp_path):
    """测试 SRT 文件写入"""
    segments = [
        {"start_sec": 0.0, "end_sec": 5.2, "text": "第一行"},
        {"start_sec": 5.2, "end_sec": 12.5, "text": "第二行"},
    ]
    output_file = tmp_path / "test.srt"
    SRTWriter.write(segments, str(output_file))
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "第一行" in content
    assert "00:00:00,000 --> 00:00:05,200" in content


def test_json_write(tmp_path):
    """测试 JSON 文件写入"""
    segments = [
        {"start_sec": 0.0, "end_sec": 5.2, "text": "第一行"},
    ]
    output_file = tmp_path / "test.json"
    JSONWriter.write(segments, str(output_file))
    assert output_file.exists()
