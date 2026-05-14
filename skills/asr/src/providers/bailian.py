"""阿里云百炼 ASR Provider (预留)

TODO: 待实现
"""

from typing import List, Dict
from .base import ASRProvider


class BailianProvider(ASRProvider):
    """阿里云百炼语音识别 Provider (预留)"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        # TODO: 初始化

    def transcribe(self, audio_path: str, language: str = "zh") -> List[Dict]:
        raise NotImplementedError("Bailian ASR provider not implemented yet")

    def transcribe_batch(
        self, audio_paths: List[str], language: str = "zh"
    ) -> List[List[Dict]]:
        raise NotImplementedError("Bailian ASR provider not implemented yet")
