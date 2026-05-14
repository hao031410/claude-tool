"""ASR 核心流程

协调音频处理、识别调用、格式输出。
"""

import os
import logging
from typing import Dict, Optional
from pathlib import Path

from dotenv import load_dotenv

from .providers.base import ASRProvider
from .providers.modelscope import ModelScopeProvider
from .audio.converter import AudioConverter
from .audio.splitter import AudioSplitter
from .output.srt import SRTWriter
from .output.vtt import VTTWriter
from .output.json import JSONWriter

logger = logging.getLogger(__name__)


# 输出格式映射
FORMATTERS = {
    "srt": SRTWriter,
    "vtt": VTTWriter,
    "json": JSONWriter,
}

# 提供者映射
PROVIDERS = {
    "modelscope": ModelScopeProvider,
}


def load_config() -> Dict:
    """按优先级加载配置

    优先级：
    1. 系统环境变量（最高
    2. 项目根目录 .env 文件
    3. 默认值（最低

    Returns:
        配置字典

    Raises:
        ValueError: 如果缺少必需配置
    """
    # 加载 .env 文件，但不覆盖已存在的环境变量
    load_dotenv(override=False)

    config = {
        # API Keys
        "modelscope_api_key": os.getenv("MODELSCOPE_API_KEY"),
        "bailian_api_key": os.getenv("BAILIAN_API_KEY"),
        "volcano_api_key": os.getenv("VOLCANO_API_KEY"),
        # 默认配置
        "provider": os.getenv("ASR_DEFAULT_PROVIDER", "modelscope"),
        "model": os.getenv("ASR_DEFAULT_MODEL", "paraformer-v2"),
        "default_language": os.getenv("ASR_DEFAULT_LANGUAGE", "zh"),
        "default_output_format": os.getenv("ASR_DEFAULT_OUTPUT_FORMAT", "srt"),
        "default_segment_duration": int(os.getenv("ASR_SEGMENT_DURATION", "10")),
    }

    # 校验必填项
    if config["provider"] == "modelscope" and not config["modelscope_api_key"]:
        raise ValueError(
            "MODELSCOPE_API_KEY not found in environment or .env file. "
            "Please configure it in your project's .env file."
        )

    return config


def merge_segments(
    segments_list: list[list[Dict]],
    offset: float,
) -> list[Dict]:
    """合并多段识别结果，并校正时间偏移

    Args:
        segments_list: 每个分段的识别结果列表
        offset: 分段时长（秒）

    Returns:
        合并后的结果列表，时间已校正
    """
    merged = []
    current_offset = 0.0

    for segments in segments_list:
        for seg in segments:
            merged.append({
                "start_sec": seg["start_sec"] + current_offset,
                "end_sec": seg["end_sec"] + current_offset,
                "text": seg["text"],
            })
        current_offset += offset

    return merged


class ASRCore:
    """ASR 核心处理器"""

    def __init__(self, config: Dict):
        """初始化

        Args:
            config: 配置字典，来自 load_config()
        """
        self.config = config
        self.converter = AudioConverter()
        self.splitter = AudioSplitter()
        self.provider = self._create_provider()

    def _create_provider(self) -> ASRProvider:
        """创建 Provider 实例"""
        provider_name = self.config["provider"]

        if provider_name == "modelscope":
            return ModelScopeProvider(
                api_key=self.config["modelscope_api_key"],
                model=self.config["model"],
            )
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

    def transcribe(
        self,
        audio_path: str,
        output_format: Optional[str] = None,
        language: Optional[str] = None,
        segment_duration: Optional[int] = None,
    ) -> str:
        """完整语音识别流程

        Args:
            audio_path: 输入音频文件路径
            output_format: 输出格式 (srt/vtt/json)，默认使用配置
            language: 识别语言 (zh/en/auto)，默认使用配置
            segment_duration: 分段时长（秒），默认使用配置

        Returns:
            输出文件路径
        """
        # 使用默认值
        output_format = output_format or self.config["default_output_format"]
        language = language or self.config["default_language"]
        segment_duration = segment_duration or self.config["default_segment_duration"]

        # 检查 ffmpeg
        if not self.converter.check_ffmpeg():
            raise RuntimeError(
                "ffmpeg not found. Please install ffmpeg first:\n"
                "  macOS: brew install ffmpeg\n"
                "  Ubuntu/Debian: apt install ffmpeg\n"
                "  CentOS/RHEL: yum install ffmpeg"
            )

        # 检查输入文件
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Starting transcription: {audio_path}")

        # 1. 转码为标准格式
        converted = self.converter.convert(str(audio_path))
        logger.debug(f"Converted to: {converted}")

        # 2. 获取总时长
        total_duration = self.converter.get_duration(converted)

        # 3. 判断是否需要分段
        if total_duration > segment_duration * 2:
            # 需要分段
            segments = self.splitter.split(converted, segment_duration)
            # 批量识别
            results = self.provider.transcribe_batch(segments, language)
            # 合并并校正时间
            merged = merge_segments(results, segment_duration)
        else:
            # 不需要分段，直接识别
            result = self.provider.transcribe(converted, language)
            # 如果没有时间信息，填充整段
            if result and result[0]["end_sec"] == 0:
                result[0]["end_sec"] = total_duration
            merged = result

        logger.info(f"Transcription complete: {len(merged)} segments")

        # 4. 生成输出文件
        output_path = str(audio_path.parent / f"{audio_path.stem}.{output_format}")
        formatter = FORMATTERS.get(output_format, FORMATTERS["srt"])
        formatter.write(merged, output_path)

        logger.info(f"Output written to: {output_path}")
        return output_path
