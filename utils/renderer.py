from typing import Dict, List, Optional
from datetime import datetime
import os
import sys
from colorama import init, Fore, Back, Style

# 初始化colorama
init(autoreset=True)

class Renderer:
    def __init__(self, color_enabled: bool = True):
        self.color_enabled = color_enabled
        self.colors = {
            'room_name': Fore.CYAN,
            'character_name': Fore.YELLOW,
            'time': Fore.GREEN,
            'system': Fore.MAGENTA,
            'dialogue': Fore.WHITE,
            'description': Fore.BLUE,
            'error': Fore.RED
        }

    def clear_screen(self) -> None:
        """清空屏幕"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def _colorize(self, text: str, color_key: str) -> str:
        """为文本添加颜色"""
        if not self.color_enabled:
            return text
        return f"{self.colors.get(color_key, '')}{text}{Style.RESET_ALL}"

    def render_header(self) -> None:
        """渲染界面头部"""
        title = "=== 虚拟小镇 ==="
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("\n" + "=" * 50)
        print(self._colorize(title.center(50), 'system'))
        print(self._colorize(time_str.center(50), 'time'))
        print("=" * 50 + "\n")

    def render_room(self, room_data: Dict) -> None:
        """渲染房间信息

        Args:
            room_data: 房间信息字典，包含名称、描述、物品等
        """
        # 房间名称和边框
        border = "╔" + "═" * 48 + "╗"
        print("\n" + self._colorize(border, 'room_name'))
        name_line = f"║ {room_data['name']}" + " " * (47 - len(room_data['name'])) + "║"
        print(self._colorize(name_line, 'room_name'))
        print(self._colorize("╠" + "═" * 48 + "╣", 'room_name'))
        
        # 房间描述
        desc = room_data['description']
        desc_lines = [desc[i:i+46] for i in range(0, len(desc), 46)]
        for line in desc_lines:
            padded_line = f"║ {line}" + " " * (47 - len(line)) + "║"
            print(self._colorize(padded_line, 'description'))
        
        # 房间状态
        if 'state' in room_data:
            state = room_data['state']
            print(self._colorize("╠" + "═" * 48 + "╣", 'room_name'))
            status_line = f"║ 🌡️{state.get('temperature', '??')}℃ | 💡{state.get('lighting', '??')} | 🧹{state.get('cleanliness', '??')}/10"
            status_line = status_line + " " * (47 - len(status_line)) + "║"
            print(self._colorize(status_line, 'system'))

        # 显示物品
        if room_data.get('items'):
            print(self._colorize("╠" + "═" * 48 + "╣", 'room_name'))
            print(self._colorize("║ 📦 物品：" + " " * 39 + "║", 'system'))
            for item in room_data['items']:
                item_line = f"║   • {item}" + " " * (45 - len(item)) + "║"
                print(self._colorize(item_line, 'description'))

        # 显示在场角色
        if room_data.get('characters'):
            print(self._colorize("╠" + "═" * 48 + "╣", 'room_name'))
            print(self._colorize("║ 👥 在场角色：" + " " * 36 + "║", 'system'))
            for char in room_data['characters']:
                char_line = f"║   • {char}" + " " * (45 - len(char)) + "║"
                print(self._colorize(char_line, 'character_name'))

        # 底部边框
        print(self._colorize("╚" + "═" * 48 + "╝", 'room_name'))

    def render_character(self, char_data: Dict) -> None:
        """渲染角色信息

        Args:
            char_data: 角色信息字典
        """
        name = char_data.get('name', '未知角色')
        # 顶部边框
        print(self._colorize("\n┌" + "─" * 48 + "┐", 'character_name'))
        
        # 角色名称和职业
        title_line = f"│ 👤 {name} - {char_data.get('occupation', '未知')}"
        title_line = title_line + " " * (47 - len(title_line)) + "│"
        print(self._colorize(title_line, 'character_name'))
        print(self._colorize("├" + "─" * 48 + "┤", 'character_name'))
        
        # 状态信息
        mood = char_data.get('mood', '平静')
        energy = char_data.get('energy', 0)
        mood_emoji = {
            '开心': '😊',
            '平静': '😐',
            '疲惫': '😫',
            '兴奋': '😃',
            '专注': '🤔',
            '困扰': '😕'
        }.get(mood, '😐')
        
        energy_bar = "█" * (energy // 10) + "░" * (10 - energy // 10)
        status_line = f"│ {mood_emoji} 心情: {mood} | ⚡ 精力: [{energy_bar}] {energy}/100"
        status_line = status_line + " " * (47 - len(status_line)) + "│"
        print(self._colorize(status_line, 'description'))
        
        # 当前活动
        print(self._colorize("├" + "─" * 48 + "┤", 'character_name'))
        activity = char_data.get('current_activity', '无特定活动')
        activity_line = f"│ 🎯 当前活动: {activity}"
        activity_line = activity_line + " " * (47 - len(activity_line)) + "│"
        print(self._colorize(activity_line, 'description'))
        
        # 底部边框
        print(self._colorize("└" + "─" * 48 + "┘", 'character_name'))

    def render_dialogue(self, speaker: str, content: str) -> None:
        """渲染对话内容

        Args:
            speaker: 说话者名称
            content: 对话内容
        """
        print("\n" + self._colorize("┌─[ 对话 ]" + "─" * 39 + "┐", 'system'))
        speaker_line = f"│ 🗣️ {speaker}"
        speaker_line = speaker_line + " " * (47 - len(speaker_line)) + "│"
        print(self._colorize(speaker_line, 'character_name'))
        
        # 分割内容为多行
        content_lines = [content[i:i+45] for i in range(0, len(content), 45)]
        print(self._colorize("├" + "─" * 48 + "┤", 'system'))
        for line in content_lines:
            content_line = f"│ {line}" + " " * (47 - len(line)) + "│"
            print(self._colorize(content_line, 'dialogue'))
        print(self._colorize("└" + "─" * 48 + "┘", 'system'))

    def render_memory(self, memory: Dict) -> None:
        """渲染记忆内容

        Args:
            memory: 记忆信息字典
        """
        timestamp = datetime.fromisoformat(memory['timestamp']).strftime("%H:%M")
        importance = memory.get('importance', 0)
        importance_icons = {
            1: '📝',  # 普通记忆
            2: '📌',  # 重要记忆
            3: '⭐',  # 很重要
            4: '❗',  # 非常重要
            5: '❗❗'  # 极其重要
        }.get(importance, '📝')
        
        print("\n" + self._colorize("┌─[ 记忆 ]" + "─" * 40 + "┐", 'time'))
        time_line = f"│ ⏰ {timestamp} {importance_icons}"
        time_line = time_line + " " * (47 - len(time_line)) + "│"
        print(self._colorize(time_line, 'time'))
        
        # 分割内容为多行
        content_lines = [memory['content'][i:i+45] for i in range(0, len(memory['content']), 45)]
        print(self._colorize("├" + "─" * 48 + "┤", 'time'))
        for line in content_lines:
            content_line = f"│ {line}" + " " * (47 - len(line)) + "│"
            print(self._colorize(content_line, 'description'))
        print(self._colorize("└" + "─" * 48 + "┘", 'time'))

    def render_menu(self, options: List[str]) -> None:
        """渲染菜单选项

        Args:
            options: 选项列表
        """
        print("\n" + self._colorize("┌─[ 可用操作 ]" + "─" * 36 + "┐", 'system'))
        for i, option in enumerate(options, 1):
            option_line = f"│ {i}. {option}"
            option_line = option_line + " " * (47 - len(option_line)) + "│"
            print(self._colorize(option_line, 'system'))
        print(self._colorize("└" + "─" * 48 + "┘", 'system'))

    def render_error(self, message: str) -> None:
        """渲染错误信息

        Args:
            message: 错误信息
        """
        print("\n" + self._colorize("┌─[ ⚠️ 错误 ]" + "─" * 38 + "┐", 'error'))
        # 分割消息为多行
        message_lines = [message[i:i+45] for i in range(0, len(message), 45)]
        for line in message_lines:
            error_line = f"│ {line}" + " " * (47 - len(line)) + "│"
            print(self._colorize(error_line, 'error'))
        print(self._colorize("└" + "─" * 48 + "┘", 'error'))

    def render_system_message(self, message: str) -> None:
        """渲染系统消息

        Args:
            message: 系统消息
        """
        print("\n" + self._colorize("┌─[ 💬 系统消息 ]" + "─" * 34 + "┐", 'system'))
        # 分割消息为多行
        message_lines = [message[i:i+45] for i in range(0, len(message), 45)]
        for line in message_lines:
            system_line = f"│ {line}" + " " * (47 - len(line)) + "│"
            print(self._colorize(system_line, 'system'))
        print(self._colorize("└" + "─" * 48 + "┘", 'system'))

    def render_status_bar(self, status: Dict) -> None:
        """渲染状态栏

        Args:
            status: 状态信息字典
        """
        time_str = datetime.now().strftime("%H:%M")
        print("\n" + self._colorize("┌─[ 状态信息 ]" + "─" * 36 + "┐", 'time'))
        
        # 时间和位置
        location_line = f"│ ⏰ {time_str} | 📍 位置: {status.get('location', '未知')}"
        location_line = location_line + " " * (47 - len(location_line)) + "│"
        print(self._colorize(location_line, 'time'))
        
        # 角色数量和系统状态
        status_line = f"│ 👥 角色: {status.get('character_count', 0)} | 🔄 状态: {status.get('system_status', 'normal')}"
        status_line = status_line + " " * (47 - len(status_line)) + "│"
        print(self._colorize(status_line, 'time'))
        
        print(self._colorize("└" + "─" * 48 + "┘", 'time'))

    def render_help(self) -> None:
        """渲染帮助信息"""
        print("\n" + self._colorize("┌─[ ℹ️ 帮助信息 ]" + "─" * 35 + "┐", 'system'))
        
        help_sections = [
            ("基本操作", [
                "🔢 输入数字选择菜单选项",
                "❌ 输入 'q' 退出程序",
                "❓ 输入 'h' 显示此帮助"
            ]),
            ("颜色说明", [
                "🔵 蓝色: 描述文本",
                "💛 黄色: 角色名称",
                "💚 绿色: 时间信息",
                "❤️ 红色: 错误信息",
                "💜 紫色: 系统消息"
            ]),
            ("快捷键", [
                "⚡ Ctrl+C: 紧急退出",
                "🔄 Ctrl+L: 清屏"
            ])
        ]
        
        for i, (section, items) in enumerate(help_sections):
            if i > 0:
                print(self._colorize("├" + "─" * 48 + "┤", 'system'))
            
            # 打印分节标题
            section_line = f"│ 📚 {section}"
            section_line = section_line + " " * (47 - len(section_line)) + "│"
            print(self._colorize(section_line, 'system'))
            
            # 打印分节内容
            for item in items:
                item_line = f"│   {item}"
                item_line = item_line + " " * (47 - len(item_line)) + "│"
                print(self._colorize(item_line, 'description'))
        
        print(self._colorize("└" + "─" * 48 + "┘", 'system'))

    def get_input(self, prompt: str = "> ") -> str:
        """获取用户输入

        Args:
            prompt: 输入提示符

        Returns:
            用户输入的文本
        """
        try:
            return input(self._colorize(prompt, 'system'))
        except KeyboardInterrupt:
            print("\n")
            return 'q'  # 返回退出命令
        except EOFError:
            print("\n")
            return ''  # 返回空字符串