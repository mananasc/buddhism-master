"""
佛学大师项目 - 出处追踪
"""
from typing import List, Dict, Any


class EvidenceTracker:
    """
    出处追踪器

    追踪回答中引用的来源，确保可溯源
    """

    def __init__(self):
        self.evidence: List[Dict[str, Any]] = []

    def add_evidence(
        self,
        source_type: str,
        title: str,
        text: str,
        chapter: str = None,
    ):
        """添加证据"""
        self.evidence.append({
            "type": source_type,
            "title": title,
            "text": text,
            "chapter": chapter,
        })

    def get_evidence(self) -> List[Dict[str, Any]]:
        """获取所有证据"""
        return self.evidence.copy()

    def clear(self):
        """清空证据"""
        self.evidence.clear()
