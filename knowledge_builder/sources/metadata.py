"""
佛学大师项目 - 来源分类与标签
"""
from typing import List, Dict, Any
from enum import Enum


class SourceType(str, Enum):
    """知识来源类型"""
    SUTRA = "sutra"           # 经典
    COMMENTARY = "commentary" # 论典
    MASTER = "master"         # 大师开示
    DICTIONARY = "dictionary" # 辞典


class Vehicle(str, Enum):
    """乘别分类"""
    MAHAYANA = "大乘"
    THERAVADA = "小乘"
    VAJRAYANA = "金刚乘"


class SchoolType(str, Enum):
    """宗派分类"""
    CHAN = "禅宗"
    PURE_LAND = "净土宗"
    TIANTAI = "天台宗"
    HUAYAN = "华严宗"
    MADHYAMAKA = "中观"
    YOGACARA = "唯识"
    PRECEPTS = "律宗"
    ESOTERIC = "密宗"


# 经典分类元数据
SUTRA_CATEGORIES = {
    "般若部": {
        "vehicle": Vehicle.MAHAYANA,
        "schools": [SchoolType.MADHYAMAKA],
        "examples": ["金刚经", "心经", "大般若经"],
    },
    "方等部": {
        "vehicle": Vehicle.MAHAYANA,
        "schools": [],
        "examples": ["维摩诘经", "楞严经"],
    },
    "法华部": {
        "vehicle": Vehicle.MAHAYANA,
        "schools": [SchoolType.TIANTAI],
        "examples": ["法华经"],
    },
    "华严部": {
        "vehicle": Vehicle.MAHAYANA,
        "schools": [SchoolType.HUAYAN],
        "examples": ["华严经"],
    },
    "净土部": {
        "vehicle": Vehicle.MAHAYANA,
        "schools": [SchoolType.PURE_LAND],
        "examples": ["阿弥陀经", "无量寿经", "观无量寿经"],
    },
    "阿含部": {
        "vehicle": Vehicle.THERAVADA,
        "schools": [],
        "examples": ["杂阿含经", "中阿含经", "长阿含经", "增一阿含经"],
    },
    "禅宗部": {
        "vehicle": Vehicle.MAHAYANA,
        "schools": [SchoolType.CHAN],
        "examples": ["六祖坛经", "楞伽经", "坛经"],
    },
}


# 核心概念标签
CONCEPT_TAGS = {
    "核心教义": ["四谛", "八正道", "十二因缘", "三法印"],
    "般若系": ["空性", "般若", "无住", "中道"],
    "唯识系": ["八识", "阿赖耶识", "唯识", "三性"],
    "佛性系": ["佛性", "如来藏", "涅槃", "真如"],
    "修行系": ["禅定", "念佛", "持戒", "布施", "忍辱", "精进"],
}


def get_source_metadata(source_type: SourceType) -> Dict[str, Any]:
    """获取来源类型的元数据"""
    return {
        "type": source_type.value,
        "categories": SUTRA_CATEGORIES if source_type == SourceType.SUTRA else {},
    }


def tag_concept(concept_name: str) -> List[str]:
    """为概念打标签"""
    tags = []
    for category, concepts in CONCEPT_TAGS.items():
        if concept_name in concepts:
            tags.append(category)
    return tags
