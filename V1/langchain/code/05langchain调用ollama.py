# @Time    : 2026/3/23 15:07
# @Author  : hero
# @File    : 05langchain调用ollama.py
from langchain_classic.chains.question_answering.map_reduce_prompt import messages
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

"""
本节代码我就不下包了,
几乎不会遇到调用ollama的
一般调也是用huggingface
"""

ollama = ChatOllama(
    model='qwen3',
    base_url = 'https://your_ip_address:port' #tips:如果是部署服务器的话
)

ollama.invoke('你好')