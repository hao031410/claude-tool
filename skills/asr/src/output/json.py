"""JSON 格式输出

用于二次开发，结构化数据存储。
"""

import json
from typing import List, Dict


class JSONWriter:
    """JSON 结果写入器"""

    @staticmethod
    def write(segments: List[Dict], output_path: str) -> None:
        """写入 JSON 文件

        Args:
            segments: 分段列表，每个元素包含 start_sec, end_sec, text
            output_path: 输出文件路径
        """
        output_data = [
            {
                "start_sec": seg["start_sec"],
                "end_sec": seg["end_sec"],
                "text": seg["text"],
            }
            for seg in segments
        ]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
