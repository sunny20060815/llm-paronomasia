from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import random
from datetime import datetime

@dataclass
class Character:
    id: str
    name: str
    age: int
    occupation: str
    personality: str
    background: str
    interests: List[str]
    current_location: str
    daily_routine: Dict[str, str]
    memory_stream: List[Dict]  # 记忆流，存储角色的经历和互动
    mood: str = "平静"  # 当前心情
    energy: int = 100  # 精力值
    relationships: Dict[str, int] = None  # 与其他角色的关系值

    def __post_init__(self):
        if self.relationships is None:
            self.relationships = {}

    @classmethod
    def from_config(cls, char_data: Dict) -> 'Character':
        """从配置文件创建角色实例"""
        return cls(
            id=char_data['id'],
            name=char_data['name'],
            age=char_data['age'],
            occupation=char_data['occupation'],
            personality=char_data['personality'],
            background=char_data['background'],
            interests=char_data['interests'],
            current_location=char_data['initial_location'],
            daily_routine=char_data['daily_routine'],
            memory_stream=[],
        )

    def add_memory(self, event: Dict) -> None:
        """添加新的记忆"""
        event['timestamp'] = datetime.now().isoformat()
        self.memory_stream.append(event)
        # 保持记忆流在限定大小内
        if len(self.memory_stream) > 100:  # 可以从配置文件读取这个值
            self.memory_stream.pop(0)

    def update_relationship(self, other_id: str, value_change: int) -> None:
        """更新与其他角色的关系值"""
        current_value = self.relationships.get(other_id, 50)  # 默认关系值为50
        new_value = max(0, min(100, current_value + value_change))  # 确保值在0-100之间
        self.relationships[other_id] = new_value

    def get_current_routine(self) -> str:
        """根据当前时间获取日常活动"""
        hour = datetime.now().hour
        if 6 <= hour < 12:
            return self.daily_routine['morning']
        elif 12 <= hour < 18:
            return self.daily_routine['afternoon']
        else:
            return self.daily_routine['evening']

    def update_mood(self, events: List[Dict]) -> None:
        """根据最近发生的事件更新心情"""
        # 这里可以实现更复杂的心情计算逻辑
        moods = ["开心", "兴奋", "平静", "疲惫", "沮丧"]
        self.mood = random.choice(moods)

    def consume_energy(self, amount: int) -> bool:
        """消耗精力值，返回是否有足够的精力"""
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False

    def rest(self, amount: int) -> None:
        """恢复精力值"""
        self.energy = min(100, self.energy + amount)

    def can_interact_with(self, other_id: str) -> bool:
        """判断是否能与其他角色互动（基于关系值）"""
        relationship = self.relationships.get(other_id, 50)
        return relationship > 20  # 关系值需要超过20才能互动

    def get_memory_summary(self) -> List[Dict]:
        """获取最近记忆的摘要"""
        return self.memory_stream[-10:]  # 返回最近的10条记忆

    def to_dict(self) -> Dict:
        """将角色数据转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'occupation': self.occupation,
            'personality': self.personality,
            'background': self.background,
            'interests': self.interests,
            'current_location': self.current_location,
            'daily_routine': self.daily_routine,
            'mood': self.mood,
            'energy': self.energy,
            'relationships': self.relationships
        }