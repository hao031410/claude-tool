"""音频分段

将长音频按指定时长分段，避免 API 一次性处理过大文件。
分段策略：5-10 秒一段，保持语义完整性。
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import List

from .converter import AudioConverter

logger = logging.getLogger(__name__)


class AudioSplitter:
    """音频分段器"""

    @staticmethod
    def split(
        audio_path: str,
        segment_duration: int = 10,
    ) -> List[str]:
        """按时长分段

        Args:
            audio_path: 输入音频文件（已转码为 WAV）
            segment_duration: 每段时长（秒）

        Returns:
            分段文件路径列表
        """
        audio_path = Path(audio_path)
        total_duration = AudioConverter.get_duration(audio_path)

        logger.info(f"Splitting audio {total_duration:.1f}s into {segment_duration}s segments")

        segments = []
        start = 0.0
        segment_idx = 0

        while start < total_duration:
            # 创建临时文件
            suffix = f"_seg{segment_idx:04d}.wav"
            segment_path = Path(tempfile.mktemp(suffix=suffix))

            cmd = [
                "ffmpeg", "-y",
                "-ss", f"{start:.3f}",
                "-i", str(audio_path),
                "-t", f"{segment_duration:.3f}",
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                "-ac", "1",
                str(segment_path),
            ]

            subprocess.run(
                cmd,
                capture_output=True,
                check=True,
                text=True,
            )

            segments.append(str(segment_path))
            start += segment_duration
            segment_idx += 1

        logger.info(f"Created {len(segments)} segments")
        return segments
