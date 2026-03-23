# @Time    : 2026/3/23 13:44
# @Author  : hero
# @File    : 03同步调用和异步调用.py

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import asyncio
load_dotenv()

openai_api_key = os.getenv('api_key')

openai_base_url = os.getenv('base_url')


# 定义大模型
openaillm = ChatOpenAI(
    model='gpt-4o-mini',
    api_key=openai_api_key,
    base_url=openai_base_url,
    temperature=1.0
)


prompt = ChatPromptTemplate.from_messages(
    [
        ('system','你现在是一个超级伟大的诗人'),
        ('user','{instruction}')
    ]
)

parser = StrOutputParser()


#tips:构造LCEL
chain = prompt|openaillm|parser

user_input = {"instruction": "写一首七言诗赞美春天"}


#important:使用异步调用
async def main():
    result = await chain.ainvoke(user_input) #important:ainvok期望的是一个字典
    print(result)

if __name__ == '__main__':
    asyncio.run(main())