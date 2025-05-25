from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

class MemoryStream:
    def __init__(self, max_size: int = 100):
        self.memories: List[Dict] = []
        self.max_size = max_size

    def add_memory(self, memory: Dict) -> None:
        """添加新的记忆
        
        Args:
            memory: 包含记忆内容的字典，应该包含以下字段：
                - type: 记忆类型（如'interaction', 'observation', 'emotion'）
                - content: 记忆内容
                - importance: 重要性评分（1-10）
                - related_chars: 相关角色列表
        """
        memory['timestamp'] = datetime.now().isoformat()
        self.memories.append(memory)
        
        # 保持记忆流大小在限制范围内
        if len(self.memories) > self.max_size:
            # 根据重要性和时间进行过滤
            self._filter_memories()

    def _filter_memories(self) -> None:
        """根据重要性和时间对记忆进行过滤"""
        # 按重要性和时间排序
        self.memories.sort(key=lambda x: (
            x.get('importance', 0),
            datetime.fromisoformat(x['timestamp'])
        ))
        
        # 删除最不重要的旧记忆
        while len(self.memories) > self.max_size:
            self.memories.pop(0)

    def get_recent_memories(self, hours: int = 24) -> List[Dict]:
        """获取最近一段时间内的记忆"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            memory for memory in self.memories
            if datetime.fromisoformat(memory['timestamp']) > cutoff_time
        ]

    def get_memories_by_type(self, memory_type: str) -> List[Dict]:
        """获取特定类型的记忆"""
        return [
            memory for memory in self.memories
            if memory.get('type') == memory_type
        ]

    def get_memories_about_character(self, character_id: str) -> List[Dict]:
        """获取与特定角色相关的记忆"""
        return [
            memory for memory in self.memories
            if character_id in memory.get('related_chars', [])
        ]

    def get_important_memories(self, min_importance: int = 7) -> List[Dict]:
        """获取重要性超过特定值的记忆"""
        return [
            memory for memory in self.memories
            if memory.get('importance', 0) >= min_importance
        ]

    def summarize_memories(self, character_id: Optional[str] = None) -> str:
        """生成记忆摘要，可以选择性地针对特定角色"""
        memories_to_summarize = (
            self.get_memories_about_character(character_id)
            if character_id
            else self.get_recent_memories(hours=24)
        )

        if not memories_to_summarize:
            return "没有相关记忆。"

        # 按时间排序
        memories_to_summarize.sort(
            key=lambda x: datetime.fromisoformat(x['timestamp'])
        )

        # 生成摘要
        summary_parts = []
        for memory in memories_to_summarize:
            time_str = datetime.fromisoformat(memory['timestamp']).strftime('%H:%M')
            summary_parts.append(
                f"[{time_str}] {memory.get('content', '未知事件')}"
            )

        return "\n".join(summary_parts)

    def save_to_file(self, filepath: str) -> None:
        """将记忆流保存到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str) -> 'MemoryStream':
        """从文件加载记忆流"""
        memory_stream = cls()
        with open(filepath, 'r', encoding='utf-8') as f:
            memory_stream.memories = json.load(f)
        return memory_stream

    def clear_old_memories(self, days: int = 7) -> None:
        """清理指定天数之前的记忆"""
        cutoff_time = datetime.now() - timedelta(days=days)
        self.memories = [
            memory for memory in self.memories
            if datetime.fromisoformat(memory['timestamp']) > cutoff_time
        ]