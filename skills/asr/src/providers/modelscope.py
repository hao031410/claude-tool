"""ModelScope 语音识别 Provider

基于达摩院 Paraformer 模型实现语音识别。
"""

import logging
from typing import List, Dict

from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

from .base import ASRProvider


logger = logging.getLogger(__name__)


# 模型映射表
MODELS = {
    "paraformer-v2": "damo/speech_paraformer-v2",
    "paraformer-zh": "damo/speech_paraformer-zh",
    "paraformer-large": "damo/speech_paraformer-large-vad-punc",
}


class ModelScopeProvider(ASRProvider):
    """ModelScope 语音识别 Provider"""

    def __init__(
        self,
        api_key: str,
        model: str = "paraformer-v2",
    ):
        """初始化

        Args:
            api_key: ModelScope API Key
            model: 模型名称，可选: paraformer-v2, paraformer-zh, paraformer-large
        """
        from modelscope.hub.api import HubApi

        # 设置 API Key
        if api_key:
            HubApi().set_api_key(api_key)

        # 获取模型 ID
        model_id = MODELS.get(model, model)

        logger.info(f"Initializing ModelScope ASR with model: {model_id}")

        # 创建 pipeline
        self.pipeline = pipeline(
            task=Tasks.SPEECH_RECOGNITION,
            model=model_id,
        )

    def transcribe(self, audio_path: str, language: str = "zh") -> List[Dict]:
        """识别单段音频"""
        result = self.pipeline(audio_path)

        # 解析结果，不同模型输出格式可能不同
        segments = []

        if "sentence_info" in result:
            # Paraformer 带时间戳输出
            for item in result["sentence_info"]:
                if item.get("text", "").strip():
                    segments.append({
                        "start_sec": float(item["start"]) / 1000,  # 毫秒转秒
                        "end_sec": float(item["end"]) / 1000,
                        "text": item["text"].strip(),
                    })
        elif "text" in result:
            # 简单文本输出，无法分段
            # 这种情况下整段作为一个结果
            if result["text"].strip():
                segments.append({
                    "start_sec": 0.0,
                    "end_sec": 0.0,  # 需要调用者根据音频时长填充
                    "text": result["text"].strip(),
                })

        return segments

    def transcribe_batch(
        self, audio_paths: List[str], language: str = "zh"
    ) -> List[List[Dict]]:
        """批量识别"""
        return [self.transcribe(path, language) for path in audio_paths]
