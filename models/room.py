from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class Room:
    id: str
    name: str
    description: str
    connected_to: List[str]
    items: List[str]
    ambient_sounds: List[str]
    time_features: Dict[str, str]
    characters: List[str] = None  # 当前在房间中的角色ID列表
    state: Dict = None  # 房间状态（如光照、温度等）

    def __post_init__(self):
        if self.characters is None:
            self.characters = []
        if self.state is None:
            self.state = self._initialize_state()

    @classmethod
    def from_config(cls, room_data: Dict) -> 'Room':
        """从配置文件创建房间实例"""
        return cls(
            id=room_data['id'],
            name=room_data['name'],
            description=room_data['description'],
            connected_to=room_data['connected_to'],
            items=room_data['items'],
            ambient_sounds=room_data['ambient_sounds'],
            time_features=room_data['time_features']
        )

    def _initialize_state(self) -> Dict:
        """初始化房间状态"""
        return {
            'lighting': 'normal',  # 光照状态
            'temperature': 22,  # 温度（摄氏度）
            'cleanliness': 10,  # 清洁度（0-10）
            'noise_level': 'quiet',  # 噪音级别
            'atmosphere': 'normal'  # 氛围
        }

    def get_current_description(self) -> str:
        """根据当前时间和状态获取房间描述"""
        hour = datetime.now().hour
        time_of_day = (
            'morning' if 6 <= hour < 12
            else 'afternoon' if 12 <= hour < 18
            else 'evening'
        )

        description = [
            self.description,
            self.time_features[time_of_day],
            f"当前房间温度{self.state['temperature']}℃，"
            f"光照状态{self.state['lighting']}。"
        ]

        if self.characters:
            description.append(f"房间内有：{', '.join(self.characters)}")

        return '\n'.join(description)

    def add_character(self, character_id: str) -> None:
        """角色进入房间"""
        if character_id not in self.characters:
            self.characters.append(character_id)
            # 根据人数调整房间状态
            self._adjust_state_for_occupancy()

    def remove_character(self, character_id: str) -> None:
        """角色离开房间"""
        if character_id in self.characters:
            self.characters.remove(character_id)
            self._adjust_state_for_occupancy()

    def _adjust_state_for_occupancy(self) -> None:
        """根据房间占用情况调整状态"""
        num_characters = len(self.characters)
        
        # 调整噪音级别
        if num_characters == 0:
            self.state['noise_level'] = 'quiet'
        elif num_characters < 3:
            self.state['noise_level'] = 'normal'
        else:
            self.state['noise_level'] = 'noisy'

        # 调整温度（人多温度略微升高）
        base_temp = 22
        self.state['temperature'] = min(26, base_temp + (num_characters * 0.5))

    def update_state(self, updates: Dict) -> None:
        """更新房间状态"""
        for key, value in updates.items():
            if key in self.state:
                self.state[key] = value

    def get_available_interactions(self) -> List[str]:
        """获取当前可用的互动选项"""
        interactions = [f"查看{item}" for item in self.items]
        
        # 根据时间添加特定互动
        hour = datetime.now().hour
        if 6 <= hour < 12:
            interactions.extend(["打开窗帘", "整理房间"])
        elif 12 <= hour < 18:
            interactions.extend(["调整空调", "休息一会"])
        else:
            interactions.extend(["开灯", "准备休息"])

        return interactions

    def can_move_to(self, room_id: str) -> bool:
        """检查是否可以移动到指定房间"""
        return room_id in self.connected_to

    def get_ambient_sound(self) -> str:
        """获取当前环境音效"""
        hour = datetime.now().hour
        if 6 <= hour < 9:  # 清晨
            return "早晨的鸟鸣声"
        elif 9 <= hour < 18:  # 白天
            return self.ambient_sounds[0] if self.ambient_sounds else "安静"
        else:  # 夜晚
            return "夜晚的虫鸣声"

    def to_dict(self) -> Dict:
        """将房间数据转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'connected_to': self.connected_to,
            'items': self.items,
            'ambient_sounds': self.ambient_sounds,
            'time_features': self.time_features,
            'characters': self.characters,
            'state': self.state
        }