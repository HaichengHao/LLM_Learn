# @Time    : 2026/6/28 17:09
# @Author  : hero
# @File    : main.py
import os
import asyncio
from dotenv import load_dotenv
from langchain_core.tools import tool
import gradio as gr
from typing import  Literal
from tavily import TavilyClient
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

load_dotenv()

api_key = os.getenv('DASHSCOPE_API_KEY')
base_url = os.getenv('danshscope_url')
tavily_key = os.getenv('TAVILY_API_KEY')
# 初始化tavily_client客户端
tavily_client = TavilyClient(
    api_key=tavily_key
)


@tool()
def internet_search(
        query: str,
        max_results:int,
        topic:Literal["general",'news','finance']='general',
        include_raw_content:bool=False,
):
    '''
    这是一个网络搜索工具,可以通过网络搜索得到实际信息
    :param query:
    :param max_results:
    :param topic:
    :param include_raw_content:
    :return:
    '''
    return tavily_client.search(
        query=query,
        max_results=max_results,
        topic=topic
    )

def init_model():
    return init_chat_model(
        model_provider="openai",
        api_key=api_key,
        base_url=base_url,
        model='qwen3.6-plus-2026-04-02'
    )



agent = create_agent(
    model=init_model(),
    tools=[internet_search],
    system_prompt="""
        你现在是一个网络搜索智能体,你可以进行网络搜索,调用internet_search工具
    """
)



res = agent.invoke(
    {
        'messages':[
            {'role':'user','content':'今天沈阳天气如何?'}
        ]
    }
)

print(res['messages'][-1].content)