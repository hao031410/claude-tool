"""SRT 字幕格式生成

SRT 是最常见的字幕格式，兼容绝大多数播放器。
"""

from datetime import timedelta
from typing import List, Dict


class SRTWriter:
    """SRT 字幕写入器"""

    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """格式化时间戳为 SRT 格式 (HH:MM:SS,mmm)

        Args:
            seconds: 秒数

        Returns:
            格式化的时间戳字符串
        """
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        millis = int((seconds - total_seconds) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def write(segments: List[Dict], output_path: str) -> None:
        """写入 SRT 文件

        Args:
            segments: 分段列表，每个元素包含 start_sec, end_sec, text
            output_path: 输出文件路径
        """
        with open(output_path, "w", encoding="utf-8") as f:
            for idx, seg in enumerate(segments, 1):
                start = SRTWriter.format_timestamp(seg["start_sec"])
                end = SRTWriter.format_timestamp(seg["end_sec"])
                text = seg["text"]
                f.write(f"{idx}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")
