# @Time    : 2026/4/18 12:07
# @Author  : hero
# @File    : v1.py
import os
import json
import subprocess
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from loguru import logger
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()

zai_key=os.getenv('zhipu_key')
zai_url=os.getenv('zhipu_base_url')
BASE_DIR = Path(__file__).resolve().parent
SCRIPT_PATH = BASE_DIR / "joker_generator" / "scripts" / "generate_joke.py"

@tool
def tell_joke(joke_type: Literal["programming", "animal", "general"]) -> str:
    """当用户要求讲笑话、想放松一下、需要幽默内容时使用。
    支持三种笑话类型：programming、animal、general。
    返回一个字符串格式的笑话内容。
    """
    try:
        result = subprocess.run(
            ["python", str(SCRIPT_PATH), "--type", joke_type],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return f"调用失败：{result.stderr.strip()[:200]}"

        data = json.loads(result.stdout.strip())
        return data["joke"]
    except Exception as e:
        return f"生成时出错：{e}"
model= ChatOpenAI(
    api_key=zai_key,
    base_url=zai_url,
    model='glm-4'
)
agent = create_agent(
    model=model,
    tools=[tell_joke],
    system_prompt="你是一个智能助手。遇到讲笑话请求时调用 tell_joke 工具。"
)

result = agent.invoke({
    "messages": [
        {"role": "user", "content": "请给我讲一个动物笑话"}
    ]
})

print(result['messages'][-1].pretty_print())