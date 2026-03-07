"""
配置模块 - 存储系统配置和参数
"""

import os
from pathlib import Path
from typing import Union
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# API配置
API_KEY = os.getenv("api_key_glm")  # 使用清华智谱的 GLM API KEY
if not API_KEY:
    API_KEY = os.getenv("api_key")  # 备用 OpenAI key
API_MODEL = "GLM-4-Plus" # 清华智谱的 GLM 模型
#API_BASE_URL = "https://api.deepseek.com"
API_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"  # 清华智谱的 API 接口
PROJECT_ROOT = Path(__file__).parent.parent
BOOK_OUTPUT_DIR = PROJECT_ROOT / "book"  # /book 总目录
SRC_DIR = Path(__file__).parent

# 阶段一参数 - 初始化与大纲构建
OUTLINE_ITERATIONS = 3  # 大纲迭代次数（建议3-5次）

# 阶段二参数 - 章节迭代创作
X_CHAPTERS = 1  # 每次生成正文时加入的前x章节全文内容（范围1-2）
Y_CHAPTERS = 5  # 每次生成正文时加入的前y章节上下文大纲（范围5-10）
TEXT_CHECK_ITERATIONS = 2  # 每章节的正文自检次数

# 阶段三参数 - 发布
UPLOAD_THRESHOLD = 3  # 累积多少章节后触发上传

# 子目录列表（每本书下的子文件夹）
BOOK_SUBDIRS = ['Outline', 'Chapters', 'Context']


def get_book_folder(book_name: str) -> Path:
    """获取指定书籍的文件夹路径"""
    return BOOK_OUTPUT_DIR / book_name


def get_book_subdirs(book_folder: Union[str, Path]) -> dict:
    """获取书籍的各个子目录路径"""
    book_path = Path(book_folder)
    return {
        'outline': book_path / 'Outline',
        'chapters': book_path / 'Chapters',
        'context': book_path / 'Context'
    }


def create_book_structure(book_name: str) -> Path:
    """创建书籍的完整文件夹结构"""
    book_folder = get_book_folder(book_name)
    
    # 创建主文件夹
    book_folder.mkdir(parents=True, exist_ok=True)
    
    # 创建子目录
    for subdir in BOOK_SUBDIRS:
        (book_folder / subdir).mkdir(parents=True, exist_ok=True)
    
    return book_folder


# 确保输出目录存在
BOOK_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
