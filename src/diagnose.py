"""
诊断脚本 - 检查配置和 API 连接是否正常
"""

import os
from pathlib import Path
from dotenv import load_dotenv

print("="*60)
print("自动写作系统 - 诊断检查")
print("="*60)

# 1. 检查 .env 文件
print("\n【1】检查 .env 文件...")
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    print(f"✓ .env 文件存在: {env_path}")
    load_dotenv(env_path)
    
    api_key = os.getenv("api_key")
    api_key_glm = os.getenv("api_key_glm")
    
    if api_key:
        print(f"✓ 找到 api_key (OpenAI): {api_key[:20]}...")
    else:
        print("✗ 未找到 api_key (OpenAI)")
    
    if api_key_glm:
        print(f"✓ 找到 api_key_glm (清华智谱): {api_key_glm[:20]}...")
    else:
        print("✗ 未找到 api_key_glm (清华智谱)")
else:
    print(f"✗ .env 文件不存在!")
    exit(1)

# 2. 检查配置
print("\n【2】检查 config.py 配置...")
from config import API_KEY, API_MODEL, API_BASE_URL

if API_KEY:
    print(f"✓ API_KEY 已加载: {API_KEY[:20]}...")
else:
    print("✗ API_KEY 未加载！")
    exit(1)

print(f"✓ API_MODEL: {API_MODEL}")
print(f"✓ API_BASE_URL: {API_BASE_URL}")

# 3. 检查 book 文件夹
print("\n【3】检查 /book 文件夹...")
from config import BOOK_OUTPUT_DIR

if BOOK_OUTPUT_DIR.exists():
    print(f"✓ /book 文件夹存在: {BOOK_OUTPUT_DIR}")
    files = list(BOOK_OUTPUT_DIR.iterdir())
    if files:
        print(f"  已有 {len(files)} 个书籍文件夹:")
        for f in files:
            print(f"    - {f.name}")
    else:
        print("  (空文件夹)")
else:
    print(f"✗ /book 文件夹不存在，将自动创建")
    BOOK_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ 已创建: {BOOK_OUTPUT_DIR}")

# 4. 测试 API 连接
print("\n【4】测试 API 连接...")
from utils import AIClient

client = AIClient()
test_prompt = "请回答：1+1等于几？只需回答数字。"

print(f"发送测试请求: \"{test_prompt}\"")
response = client.generate_text(test_prompt)

if response and response.strip():
    print(f"✓ API 连接成功！")
    print(f"  响应: {response}")
else:
    print(f"✗ API 连接失败！")
    print("请检查上面的错误信息")
    exit(1)

# 5. 测试文件创建
print("\n【5】测试文件创建...")
from config import create_book_structure

test_book_name = "测试书籍"
test_folder = create_book_structure(test_book_name)

if test_folder.exists():
    print(f"✓ 书籍文件夹创建成功: {test_folder}")
    subdirs = list(test_folder.iterdir())
    print(f"  子目录数量: {len(subdirs)}")
    for subdir in subdirs:
        print(f"    - {subdir.name}")
else:
    print(f"✗ 书籍文件夹创建失败")
    exit(1)

print("\n" + "="*60)
print("✓ 所有诊断检查通过！系统可以正常使用。")
print("="*60)
