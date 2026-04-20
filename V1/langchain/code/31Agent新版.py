# @Time    : 2026/4/1 22:08
# @Author  : hero
# @File    : 31Agent新版.py

'''
新版的写法就直接上来就是create_agent了
'''
from typing import TypedDict
from pydantic import BaseModel
from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
import os
import httpx
import json
from loguru import logger
import asyncio
from langchain_classic.agents import create_openai_tools_agent,AgentExecutor
load_dotenv()
langsmith_key =os.getenv('lang_smith_key')
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = f'{langsmith_key}'
zai_key = os.getenv('zhipu_key')
zai_url = os.getenv('zhipu_base_url')


@tool
def get_weather(city:str):
    """
    这是一个天气工具,基于openweathermap构建
    :param city:
    :return: 天气情况
    """
    url='https://api.openweathermap.org/data/2.5/weather'
    params={
        'q': city,
        'appid': os.getenv('OPENWEATHER_API_KEY'),
        'units': 'metric', #tips:使用摄氏度
        'lang': 'zh-CN' #输出语言使用简体中文
    }
    resp = httpx.get(url,params=params,timeout=10)
    data = resp.json()
    return json.dumps(data,ensure_ascii=False) #tips:ensure_ascii=False时候允许传入非ascii字符



model= ChatOpenAI(
    api_key=zai_key,
    base_url=zai_url,
    model='glm-4'
)

class WeatherCompareOutput(TypedDict):
    beijing_temp: float
    shanghai_temp: float
    hotter_city: str
    summary: str


agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt=(
        '你是一个天气播报员'
        '当用户询问多个城市天气时'
        '你需要分别调用工具获取数据,并进行比较分析'
    ),
    response_format=WeatherCompareOutput
)
#
result = agent.invoke(
    {"messages":[{"role":"human","content":"请问北京和上海今天的天气怎么样?哪个城市更热"}]}
)

# result = agent.invoke(
#     {"input": "请问今天北京和上海的天气怎么样，哪个城市更热？"}
# )
print(result)

print()

print(json.dumps(result["structured_response"], ensure_ascii=False, indent=2))


