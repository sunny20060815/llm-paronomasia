import json
import time
import random
import msvcrt
from typing import Dict, List, Optional
from datetime import datetime
import os
import sys

from models.character import Character
from models.room import Room
from models.memory_stream import MemoryStream
from utils.api_client import DeepSeekClient
from utils.renderer import Renderer

class VirtualTown:
    def __init__(self):
        self.renderer = Renderer()
        self.api_client = DeepSeekClient()
        self.characters: Dict[str, Character] = {}
        self.rooms: Dict[str, Room] = {}
        self.memory_streams: Dict[str, MemoryStream] = {}
        self.current_character: Optional[Character] = None
        self.current_room: Optional[Room] = None

    def load_config(self) -> None:
        """加载配置文件"""
        # 加载角色配置
        with open('config/characters.json', 'r', encoding='utf-8') as f:
            char_data = json.load(f)
            for char_info in char_data['characters']:
                char = Character.from_config(char_info)
                self.characters[char.id] = char
                self.memory_streams[char.id] = MemoryStream()

        # 加载房间配置
        with open('config/room_layout.json', 'r', encoding='utf-8') as f:
            room_data = json.load(f)
            for room_info in room_data['rooms']:
                room = Room.from_config(room_info)
                self.rooms[room.id] = room

    def initialize_game(self) -> None:
        """初始化游戏状态"""
        self.load_config()
        
        # 将角色放置到初始位置
        for char_id, char in self.characters.items():
            room = self.rooms[char.current_location]
            room.add_character(char_id)

        # 设置初始角色和房间
        first_char = list(self.characters.values())[0]
        self.switch_character(first_char.id)

    def switch_character(self, char_id: str) -> None:
        """切换当前控制的角色"""
        if char_id in self.characters:
            self.current_character = self.characters[char_id]
            self.current_room = self.rooms[self.current_character.current_location]
            self.renderer.clear_screen()
            self.renderer.render_system_message(f"切换到角色：{self.current_character.name}")

    def move_character(self, char_id: str, room_id: str) -> bool:
        """移动角色到指定房间"""
        if char_id not in self.characters or room_id not in self.rooms:
            return False

        char = self.characters[char_id]
        old_room = self.rooms[char.current_location]
        new_room = self.rooms[room_id]

        # 检查是否可以移动到目标房间
        if room_id not in old_room.connected_to:
            return False

        # 更新房间和角色状态
        old_room.remove_character(char_id)
        new_room.add_character(char_id)
        char.current_location = room_id

        # 记录移动事件
        self.add_memory(char_id, {
            'type': 'movement',
            'content': f"从{old_room.name}移动到{new_room.name}",
            'importance': 3,
            'timestamp': datetime.now().isoformat()
        })

        return True

    def add_memory(self, char_id: str, memory: Dict) -> None:
        """为角色添加记忆"""
        if char_id in self.memory_streams:
            self.memory_streams[char_id].add_memory(memory)

    def generate_character_action(self, char_id: str) -> str:
        """生成角色行动"""
        char = self.characters[char_id]
        room = self.rooms[char.current_location]
        
        # 获取角色描述和当前情境
        char_desc = f"{char.name}是一个{char.age}岁的{char.occupation}，{char.personality}"
        situation = f"现在在{room.name}，{room.get_current_description()}"
        
        # 获取可用行动
        available_actions = room.get_available_interactions()
        
        return self.api_client.generate_action(
            char_desc,
            situation,
            available_actions
        )

    def generate_dialogue(self, speaker_id: str, listener_id: str) -> str:
        """生成对话内容，考虑角色关系和历史互动"""
        speaker = self.characters[speaker_id]
        listener = self.characters[listener_id]
    
        # 获取双方的最近记忆
        speaker_memories = self.memory_streams[speaker_id].get_recent_memories(hours=24)
        listener_memories = self.memory_streams[listener_id].get_recent_memories(hours=24)
    
        # 找出涉及对方的记忆
        speaker_related_memories = [mem for mem in speaker_memories 
                                if listener.name in mem['content']]
        listener_related_memories = [mem for mem in listener_memories 
                                if speaker.name in mem['content']]
    
        # 构建对话提示
        prompt = f"作为{speaker.name}（{speaker.personality}），"
        prompt += f"你现在遇到了{listener.name}（{listener.personality}）。\n"
    
        # 添加关系信息
        relationship = speaker.relationships.get(listener_id, 50)
        if relationship >= 80:
            prompt += f"你们关系非常好。"
        elif relationship >= 60:
            prompt += f"你们是朋友。"
        elif relationship <= 20:
            prompt += f"你们关系不太好。"
        else:
            prompt += f"你们是普通关系。"
    
        # 添加最近互动记忆
        if speaker_related_memories:
            prompt += f"\n你最近与{listener.name}的互动：\n"
            for mem in speaker_related_memories[-2:]:
                prompt += f"- {mem['content']}\n"
    
        # 添加当前环境信息
        room = self.rooms[speaker.current_location]
        prompt += f"\n你们现在在{room.name}，"
        prompt += f"你想对{listener.name}说什么？"
    
        # 生成对话
        dialogue = self.api_client.generate_response(prompt)
    
        # 更新关系值
        relationship_change = random.randint(-5, 10)  # 倾向于略微提升关系
        speaker.update_relationship(listener_id, relationship_change)
        listener.update_relationship(speaker_id, relationship_change)
    
        return dialogue

    def update_game_state(self) -> None:
        """更新游戏状态"""
        current_time = datetime.now()

        # 更新所有角色状态
        for char in self.characters.values():
            # 更新心情
            recent_memories = self.memory_streams[char.id].get_recent_memories(hours=1)
            char.update_mood(recent_memories)

            # 更新精力值
            if current_time.hour >= 22 or current_time.hour < 6:
                char.rest(10)  # 夜间休息恢复精力
            else:
                char.consume_energy(1)  # 日间活动消耗精力

        # 更新房间状态
        for room in self.rooms.values():
            # 根据时间更新房间状态
            if 6 <= current_time.hour < 18:
                room.update_state({'lighting': 'bright'})
            else:
                room.update_state({'lighting': 'dim'})

    def run_game_loop(self) -> None:
        """运行游戏主循环"""
        # 初始化游戏
        self.initialize_game()
        
        while True:
            # 显示主菜单
            options = [
                "选择角色",
                "切换房间",
                "查看记忆",
                "生成行为",
                "生成对话",
                "观察模式",
                "添加记忆",
                "退出游戏"
            ]
            self.renderer.render_menu(options)
            
            # 获取用户输入
            choice = input("请选择操作 (1-8): ")
            
            # 根据用户选择执行相应操作
            if choice == '1':
                self.show_character_selection()
            elif choice == '2':
                self.show_room_selection()
            elif choice == '3':
                self.show_memories()
            elif choice == '4':
                if self.current_character:
                    action = self.generate_action_based_on_memory(self.current_character.id)
                    self.renderer.render_system_message(f"{self.current_character.name}的行为：{action}")
                    self.add_memory(self.current_character.id, {
                        'type': 'action',
                        'content': action,
                        'importance': 3
                    })
                    input("按回车键继续...")
            elif choice == '5':
                if self.current_character and self.current_room:
                    others = [char_id for char_id in self.current_room.characters if char_id != self.current_character.id]
                    if others:
                        target_id = random.choice(others)
                        dialogue = self.generate_dialogue(self.current_character.id, target_id)
                        self.renderer.render_dialogue(self.current_character.name, dialogue)
                        self.add_memory(self.current_character.id, {
                            'type': 'dialogue',
                            'content': f"与{self.characters[target_id].name}交谈: {dialogue}",
                            'importance': 5
                        })
                        input("按回车键继续...")
                    else:
                        self.renderer.render_system_message("当前房间没有其他角色可以对话")
                        input("按回车键继续...")
            elif choice == '6':
                self.renderer.render_system_message("进入观察模式 (按q键退出)")
                self.run_observation_mode()
            elif choice == '7':
                if self.current_character:
                    memory_content = input("请输入记忆内容: ")
                    importance = int(input("请输入重要性 (1-5): "))
                    self.add_memory(self.current_character.id, {
                        'type': 'custom',
                        'content': memory_content,
                        'importance': importance
                    })
                    self.renderer.render_system_message("记忆已添加")
                    input("按回车键继续...")
            elif choice == '8':
                self.renderer.render_system_message("退出游戏")
                break
            else:
                self.renderer.render_system_message("无效的选择")
                input("按回车键继续...")
            
            # 更新状态栏
            if self.current_character and self.current_room:
                status = {
                    'location': self.current_room.name,
                    'character_count': len(self.current_room.characters),
                    'system_status': '正常运行'
                }
                self.renderer.render_status_bar(status)

    def look_around(self) -> None:
        """查看周围环境"""
        if not self.current_room:
            return

        description = self.current_room.get_current_description()
        self.renderer.render_system_message(description)

        # 生成并显示当前角色的观察
        if self.current_character:
            observation = self.api_client.generate_response(
                f"作为{self.current_character.name}，描述你对{self.current_room.name}的观察感受。",
                character_desc=f"{self.current_character.personality}"
            )
            self.renderer.render_dialogue(self.current_character.name, observation)

    def talk_to_others(self) -> None:
        """与其他角色交谈"""
        if not self.current_character or not self.current_room:
            return

        # 获取同一房间的其他角色
        others = [
            char_id for char_id in self.current_room.characters
            if char_id != self.current_character.id
        ]

        if not others:
            self.renderer.render_system_message("房间里没有其他角色")
            return

        # 显示可交谈的角色
        self.renderer.render_system_message("可以交谈的角色：")
        for i, char_id in enumerate(others, 1):
            char = self.characters[char_id]
            print(f"{i}. {char.name}")

        choice = self.renderer.get_input("请选择交谈对象 (输入数字): ")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(others):
                listener_id = others[idx]
                dialogue = self.generate_dialogue(
                    self.current_character.id,
                    listener_id
                )
                self.renderer.render_dialogue(self.current_character.name, dialogue)

                # 记录对话
                self.add_memory(self.current_character.id, {
                    'type': 'dialogue',
                    'content': f"与{self.characters[listener_id].name}交谈: {dialogue}",
                    'importance': 5
                })
        except ValueError:
            self.renderer.render_error("无效的选择")

    def show_character_selection(self) -> None:
        """显示角色选择界面"""
        self.renderer.render_system_message("可选择的角色：")
        for i, (char_id, char) in enumerate(self.characters.items(), 1):
            print(f"{i}. {char.name} ({char.occupation})")

        choice = self.renderer.get_input("请选择角色 (输入数字): ")
        try:
            idx = int(choice) - 1
            char_ids = list(self.characters.keys())
            if 0 <= idx < len(char_ids):
                self.switch_character(char_ids[idx])
        except ValueError:
            self.renderer.render_error("无效的选择")

    def show_room_selection(self) -> None:
        """显示房间选择界面"""
        if not self.current_character or not self.current_room:
            return

        connected_rooms = [
            room_id for room_id in self.current_room.connected_to
            if room_id in self.rooms
        ]

        if not connected_rooms:
            self.renderer.render_system_message("没有可以移动到的房间")
            return

        self.renderer.render_system_message("可以移动到的房间：")
        for i, room_id in enumerate(connected_rooms, 1):
            room = self.rooms[room_id]
            print(f"{i}. {room.name}")

        choice = self.renderer.get_input("请选择目标房间 (输入数字): ")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(connected_rooms):
                target_room = connected_rooms[idx]
                if self.move_character(self.current_character.id, target_room):
                    self.current_room = self.rooms[target_room]
                    self.renderer.render_system_message(
                        f"移动到了{self.current_room.name}"
                    )
                else:
                    self.renderer.render_error("无法移动到该房间")
        except ValueError:
            self.renderer.render_error("无效的选择")

    def show_memories(self) -> None:
        """显示角色记忆"""
        if not self.current_character:
            return

        memory_stream = self.memory_streams[self.current_character.id]
        recent_memories = memory_stream.get_recent_memories(hours=24)

        if not recent_memories:
            self.renderer.render_system_message("没有最近的记忆")
            return

        self.renderer.render_system_message("最近的记忆：")
        for memory in recent_memories:
            self.renderer.render_memory(memory)

    def generate_action_based_on_memory(self, char_id: str) -> str:
        """根据角色的记忆生成行为决策"""
        character = self.characters[char_id]
        memory_stream = self.memory_streams[char_id]
        recent_memories = memory_stream.get_recent_memories(hours=24)
    
        # 构建提示，包含角色信息和最近记忆
        memory_summary = "\n".join([mem['content'] for mem in recent_memories[-5:]])
        prompt = f"作为{character.name}（{character.personality}），"f"根据最近的经历：\n{memory_summary}\n"
        prompt += f"现在你在{self.rooms[character.current_location].name}，考虑到你的性格和经历，你会做什么？"
    
        return self.api_client.generate_response(prompt)
    
    def update_mood_based_on_events(self, char_id: str) -> None:
        """根据最近事件更新角色心情"""
        character = self.characters[char_id]
        memory_stream = self.memory_streams[char_id]
        recent_memories = memory_stream.get_recent_memories(hours=6)
    
        if not recent_memories:
            return
    
        # 分析最近事件对心情的影响
        prompt = f"分析{character.name}最近的经历：\n"
        for mem in recent_memories[-3:]:
            prompt += f"- {mem['content']}\n"
        prompt += f"考虑到{character.personality}的性格，这些经历会让他/她感觉如何？"
    
        mood_analysis = self.api_client.generate_response(prompt)
        character.mood = mood_analysis[:10]  # 取前10个字符作为心情描述
    
    def run_observation_mode(self) -> None:
        """运行观察模式，让所有角色都能互动，并添加按q键退出功能"""
        if not self.current_character or not self.current_room:
            return
    
        # 让每个角色都有机会行动
        for char_id in list(self.characters.keys()):
            char = self.characters[char_id]
            current_room = self.rooms[char.current_location]
            
            # 生成并显示角色行为
            action = self.generate_action_based_on_memory(char_id)
            self.renderer.render_system_message(f"{char.name}的行为：{action}")
            
            # 记录行为
            self.add_memory(char_id, {
                'type': 'action',
                'content': action,
                'importance': 3
            })
            
            # 与同一房间的其他角色互动
            others = [other_id for other_id in current_room.characters if other_id != char_id]
            if others and random.random() < 0.7:  # 70%的概率进行互动
                target_id = random.choice(others)
                dialogue = self.generate_dialogue(char_id, target_id)
                self.renderer.render_dialogue(char.name, dialogue)
                
                # 记录对话
                self.add_memory(char_id, {
                    'type': 'dialogue',
                    'content': f"与{self.characters[target_id].name}交谈: {dialogue}",
                    'importance': 5
                })
            
            # 随机决定是否移动到其他房间
            connected_rooms = [room_id for room_id in current_room.connected_to if room_id in self.rooms]
            if connected_rooms and random.random() < 0.3:  # 30%的概率移动
                target_room = random.choice(connected_rooms)
                if self.move_character(char_id, target_room):
                    self.renderer.render_system_message(f"{char.name}移动到了{self.rooms[target_room].name}")
            
            # 更新角色心情
            self.update_mood_based_on_events(char_id)
            
            time.sleep(2)  # 暂停2秒，让用户能够观察到行为
            
            # 检查是否要退出观察模式
            if msvcrt.kbhit():  # 检查是否有按键输入
                key = msvcrt.getch()
                if key == b'q':  # 按q键退出观察模式
                    self.renderer.render_system_message("退出观察模式")
                    return

def main():
    game = VirtualTown()
    game.run_game_loop()

if __name__ == "__main__":
    main()