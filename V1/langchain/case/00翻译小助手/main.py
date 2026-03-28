# @Time    : 2026/3/28 10:06
# @Author  : hero
# @File    : main.py
import time

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_tavily.tavily_search import TavilySearch
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()
api_key = os.getenv('api_key')
base_url = os.getenv('base_url')
# os.environ['OPENAI_API_KEY']=os.getenv('api_key')
# os.environ['BASE_URL']=os.getenv('base_url')
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = os.environ['lang_smith_key']

model = ChatOpenAI(model='gpt-4o-mini', api_key=api_key, base_url=base_url)
prompt_template = ChatPromptTemplate(
    messages=[
        ('system',
         '你现在是一名翻译助手，只会翻译用户指定的原文到指定的译文，其余无关于翻译的问题你都要回答“我只是一名翻译助手哦，其它领域的问题我不了解哈哈”'),
        ('human', '请你把{origin_language}翻译为{target_language}文')
    ]
)
parser = StrOutputParser()
demochain = prompt_template | model | parser


async def trans(o, t):
    resp = demochain.astream({
        'origin_language': o,
        'target_language': t,
    })

    async for r in resp:
        print(r, end='', flush=True)
        await asyncio.sleep(0.05)


if __name__ == '__main__':
    o = input('请输入你要翻译的句子>>>')
    t = input('请输入要翻译的目标文字(如英语，德语)>>')
    asyncio.run(trans(o, t))
