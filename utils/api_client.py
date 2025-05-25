import requests
import json
from typing import Dict, List, Optional, Union
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import API_KEY, API_BASE_URL, DEFAULT_TEMPERATURE, MAX_TOKENS

class DeepSeekClient:
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = API_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def _make_request(self, endpoint: str, payload: Dict) -> Dict:
        """发送API请求"""
        try:
            response = requests.post(
                f"{self.base_url}/{endpoint}",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求错误: {str(e)}")
            return {'error': str(e)}

    def generate_response(
        self,
        prompt: str,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = MAX_TOKENS,
        character_desc: Optional[str] = None
    ) -> str:
        """生成AI响应

        Args:
            prompt: 输入提示
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成token数
            character_desc: 角色描述（可选）

        Returns:
            生成的响应文本
        """
        # 构建系统提示
        system_prompt = "你是一个虚拟小镇中的居民。"
        if character_desc:
            system_prompt += f"\n{character_desc}"

        payload = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        response = self._make_request('chat/completions', payload)
        if 'error' in response:
            return f"生成响应时出错: {response['error']}"

        return response.get('choices', [{}])[0].get('message', {}).get('content', '')

    def analyze_emotion(
        self,
        text: str,
        context: Optional[str] = None
    ) -> Dict[str, Union[str, float]]:
        """分析文本情感

        Args:
            text: 需要分析的文本
            context: 上下文信息（可选）

        Returns:
            情感分析结果，包含情感类型和强度
        """
        prompt = f"分析以下文本的情感:\n{text}"
        if context:
            prompt += f"\n上下文信息:\n{context}"

        payload = {
            'model': 'deepseek-chat',
            'messages': [
                {
                    'role': 'system',
                    'content': '你是一个情感分析专家，请分析文本中表达的情感。'
                },
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.3  # 使用较低的温度以获得更稳定的分析结果
        }

        response = self._make_request('chat/completions', payload)
        if 'error' in response:
            return {'emotion': 'unknown', 'intensity': 0.0, 'error': response['error']}

        # 解析响应获取情感信息
        analysis = response.get('choices', [{}])[0].get('message', {}).get('content', '')
        # 这里可以添加更复杂的响应解析逻辑
        return {
            'emotion': self._extract_emotion(analysis),
            'intensity': self._extract_intensity(analysis)
        }

    def _extract_emotion(self, analysis: str) -> str:
        """从分析文本中提取情感类型"""
        # 这里可以实现更复杂的提取逻辑
        if '开心' in analysis or '快乐' in analysis:
            return 'happy'
        elif '悲伤' in analysis or '难过' in analysis:
            return 'sad'
        elif '愤怒' in analysis or '生气' in analysis:
            return 'angry'
        elif '害怕' in analysis or '恐惧' in analysis:
            return 'scared'
        elif '惊讶' in analysis:
            return 'surprised'
        else:
            return 'neutral'

    def _extract_intensity(self, analysis: str) -> float:
        """从分析文本中提取情感强度"""
        # 这里可以实现更复杂的强度计算逻辑
        intensity_words = {
            '非常': 1.0,
            '很': 0.8,
            '比较': 0.6,
            '有点': 0.4,
            '略微': 0.2
        }

        for word, value in intensity_words.items():
            if word in analysis:
                return value

        return 0.5  # 默认强度

    def generate_action(self, 
        character_desc: str,
        situation: str,
        available_actions: List[str]
    ) -> str:
        """生成角色行动

        Args:
            character_desc: 角色描述
            situation: 当前情境
            available_actions: 可用行动列表

        Returns:
            生成的行动描述
        """
        prompt = f"角色描述：{character_desc}\n"
        prompt += f"当前情境：{situation}\n"
        prompt += f"可用行动：{', '.join(available_actions)}\n"
        prompt += "请根据角色特点和当前情境，选择一个合适的行动并描述具体过程。"

        return self.generate_response(
            prompt,
            temperature=0.7,  # 使用较高的温度以获得更有创意的行动
            character_desc=character_desc
        )

    def generate_dialogue(
        self,
        speaker_desc: str,
        listener_desc: str,
        context: str,
        topic: Optional[str] = None
    ) -> str:
        """生成对话内容

        Args:
            speaker_desc: 说话者描述
            listener_desc: 听众描述
            context: 对话上下文
            topic: 对话主题（可选）

        Returns:
            生成的对话内容
        """
        prompt = f"说话者：{speaker_desc}\n"
        prompt += f"听众：{listener_desc}\n"
        prompt += f"上下文：{context}\n"
        if topic:
            prompt += f"主题：{topic}\n"
        prompt += "请生成一段自然的对话内容。"

        return self.generate_response(
            prompt,
            temperature=0.8,  # 使用较高的温度以获得更自然的对话
            character_desc=speaker_desc
        )