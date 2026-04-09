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


ollama_llm = ChatOllama(
  model="deepseek-r1:7b",
  base_url="http://your-ip:port",
)

messages = {"role": "user", "content": "你好，请介绍一下你自己"}
resp = ollama_llm.invoke(messages)
print(resp.content)