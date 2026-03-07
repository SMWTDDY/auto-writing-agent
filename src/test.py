from openai import OpenAI
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# 初始化客户端
api_key = os.getenv("api_key_glm")
if not api_key:
    raise ValueError("API密钥未设置！请检查 .env 文件中是否有 api_key 配置")

client = OpenAI(
    api_key=api_key,  # 从环境变量获取
    base_url="https://open.bigmodel.cn/api/paas/v4"# DeepSeek的官方接口地址
)

def call_llm(prompt: str = "详细提示词", system_prompt: str = "背景提示词") -> str:
    response = client.chat.completions.create(
        model="glm-4-flash", 
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7, # 控制发散度
        stream=False 
    )
    return response.choices[0].message.content

# 测试
if __name__ == "__main__":
    result = call_llm("你好，你是谁？","")
    print(result)
