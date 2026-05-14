"""音频格式转换

使用 ffmpeg 将各种格式转换为 ASR 标准格式：
- PCM 16-bit
- 16kHz 采样率
- 单声道
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class AudioConverter:
    """音频格式转换器"""

    SUPPORTED_INPUT_FORMATS = {
        "wav", "mp3", "m4a", "flac", "ogg", "aac", "wma", "mp4"
    }

    @staticmethod
    def check_ffmpeg() -> bool:
        """检查 ffmpeg 是否安装"""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def convert(
        audio_path: str,
        output_sample_rate: int = 16000,
        channels: int = 1,
    ) -> str:
        """转码为 ASR 标准格式

        Args:
            audio_path: 输入音频文件路径
            output_sample_rate: 输出采样率
            channels: 输出声道数 (1=单声道)

        Returns:
            转码后临时文件路径
        """
        input_path = Path(audio_path)

        # 创建临时输出文件
        suffix = ".wav"
        output_path = Path(tempfile.mktemp(suffix=suffix))

        # ffmpeg 命令
        cmd = [
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-acodec", "pcm_s16le",   # 16-bit PCM
            "-ar", str(output_sample_rate),  # 采样率
            "-ac", str(channels),     # 声道
            "-vn",                    # 移除视频流
            str(output_path),
        ]

        logger.debug(f"Running ffmpeg: {' '.join(cmd)}")

        try:
            subprocess.run(
                cmd,
                capture_output=True,
                check=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg conversion failed: {e.stderr}")
            raise RuntimeError(f"Failed to convert audio: {e.stderr}")

        return str(output_path)

    @staticmethod
    def get_duration(audio_path: str) -> float:
        """获取音频时长（秒）"""
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            check=True,
            text=True,
        )

        duration = float(result.stdout.strip())
        return duration
