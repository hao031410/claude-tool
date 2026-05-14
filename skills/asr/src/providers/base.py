"""ASR Provider 抽象基类

定义统一的语音识别接口，支持多平台扩展。
"""

from abc import ABC, abstractmethod
from typing import List, Dict


class ASRProvider(ABC):
    """ASR Provider 抽象基类"""

    @abstractmethod
    def transcribe(self, audio_path: str, language: str = "zh") -> List[Dict]:
        """识别单段音频文件

        Args:
            audio_path: 音频文件路径
            language: 识别语言 (zh/en/auto)

        Returns:
            识别结果列表，每个元素包含:
            {
                'start_sec': 开始时间(秒),
                'end_sec': 结束时间(秒),
                'text': 识别文本
            }
        """
        pass

    @abstractmethod
    def transcribe_batch(
        self, audio_paths: List[str], language: str = "zh"
    ) -> List[List[Dict]]:
        """批量识别多个音频片段

        Args:
            audio_paths: 音频文件路径列表
            language: 识别语言

        Returns:
            识别结果列表，每个元素是一个音频的结果
        """
        pass
