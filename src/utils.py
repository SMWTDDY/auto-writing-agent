"""
工具模块 - 提供文件操作、AI调用等通用功能
"""

import os
import json
import re
from pathlib import Path
from typing import Optional
import requests
from config import API_KEY, API_MODEL, API_BASE_URL


class FileManager:
    """文件管理类"""
    
    @staticmethod
    def read_file(filepath: str) -> str:
        """读取文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    @staticmethod
    def write_file(filepath: str, content: str) -> bool:
        """写入文件内容"""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"写入文件失败: {e}")
            return False
    
    @staticmethod
    def append_file(filepath: str, content: str) -> bool:
        """追加文件内容"""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"追加文件失败: {e}")
            return False
    
    @staticmethod
    def file_exists(filepath: str) -> bool:
        """检查文件是否存在"""
        return Path(filepath).exists()
    
    @staticmethod
    def get_files_in_dir(directory: str, pattern: str = "*") -> list:
        """获取目录下的文件列表"""
        dir_path = Path(directory)
        return sorted([f.name for f in dir_path.glob(pattern) if f.is_file()])


class AIClient:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or API_KEY
        self.model = model or API_MODEL
        self.base_url = API_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # 优化：使用 Session 复用底层 TCP 连接
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def call_api(self, messages: list, temperature: float = 0.7, max_tokens: int = 5000) -> str:
        """调用API"""
        try:
            if not self.api_key:
                error_msg = "❌ API KEY 未配置！请检查 .env 文件中的 api_key 或 api_key_glm"
                print(f"[ERROR] {error_msg}")
                return ""
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
                 
            # 优化：使用 self.session 替代 requests.post
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=360
            )
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                error_msg = f"❌ API 错误: HTTP {response.status_code}\n响应: {response.text}"
                print(f"[ERROR] {error_msg}")
                return ""
        except Exception as e:
            print(f"❌ API 调用失败: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def generate_text(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """生成文本"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        return self.call_api(messages, **kwargs)



class Logger:
    """日志记录类"""
    
    @staticmethod
    def log(message: str, level: str = "INFO"):
        """记录日志"""
        print(f"[{level}] {message}")
    
    @staticmethod
    def log_stage(stage: str, message: str):
        """记录阶段信息"""
        print(f"\n{'='*50}")
        print(f"【{stage}】{message}")
        print('='*50)
    
    @staticmethod
    def log_chapter(chapter_num: int, message: str):
        """记录章节信息"""
        print(f"\n[Chapter {chapter_num}] {message}")


class ContextManager:
    """上下文管理类"""
    
    def __init__(self, context_dir: str):
        self.context_dir = Path(context_dir)
    
    def load_context(self, chapter_num: int) -> dict:
        """加载章节上下文"""
        context_file = self.context_dir / f"Context_{chapter_num}.txt"
        if context_file.exists():
            return {"content": FileManager.read_file(str(context_file))}
        return {"content": ""}
    
    def save_context(self, chapter_num: int, context: str) -> bool:
        """保存章节上下文"""
        context_file = self.context_dir / f"Context_{chapter_num}.txt"
        return FileManager.write_file(str(context_file), context)
