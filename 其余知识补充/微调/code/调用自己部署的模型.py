# @Time    : 2026/5/2 20:40
# @Author  : hero
# @File    : 调用自己部署的模型.py
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model='Qwen3-0.6B-sft-lora',
    base_url='http://localhost:'
)