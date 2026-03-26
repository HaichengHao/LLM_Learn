# @Time    : 2026/3/24 13:55
# @Author  : hero
# @File    : 11StrOutputParser.py
import asyncio
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()
base_url = os.getenv('base_url')
api_key = os.getenv('api_key')


model = ChatOpenAI(
    base_url=base_url,
    api_key=api_key,
    temperature=0.7,
    model='gpt-4o-mini'
)


prompt=ChatPromptTemplate(
    [
        ('system','你现在是一名笑话大师'),
        ('user','{user_input}')
    ]
)


parser=StrOutputParser()

chain=prompt|model|parser


async def main():
    user_input = input('请输入你要给笑话大师的对话>>>>')
    resp = await chain.ainvoke({'user_input', user_input})
    print(resp)


if __name__ == '__main__':
    asyncio.run(main())