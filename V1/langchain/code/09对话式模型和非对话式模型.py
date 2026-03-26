# @Time    : 2026/3/23 16:43
# @Author  : hero
# @File    : 08对话式模型和非对话式模型.py

import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate
from langchain_openai import ChatOpenAI,OpenAI
from langchain_core.output_parsers import StrOutputParser
load_dotenv()
api_key=os.getenv("api_key")
base_url=os.getenv("base_url")


#important:以下就是一个错误示例！！！langchain_openai下的 OpenAI是属于补全模型，而gpt-4o-mini是一个聊天模型,必须适用chatOpenAI
# client = OpenAI(
#     api_key=api_key,
#     base_url=base_url,
#     model='gpt-4o-mini'
# )
#
# client.invoke('你好')