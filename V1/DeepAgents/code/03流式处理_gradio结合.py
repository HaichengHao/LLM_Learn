# @Time    : 2026/4/29 17:08
# @Author  : hero
# @File    : 03流式处理_gradio结合.py

from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from dotenv import load_dotenv
from typing import Annotated, Literal
from tavily import TavilyClient
import os
import gradio as gr
import asyncio

load_dotenv()


def init_model():
    return init_chat_model(
        model='glm-4',
        model_provider='openai',
        api_key=os.getenv('zhipu_key'),
        base_url=os.getenv('zhipu_base_url')

    )


tavily_client = TavilyClient(os.getenv('TAVILY_API_KEY'))


def internet_serach(query: str,
                    max_results: int = 3,
                    topic: Literal["general", "news", "finance"] = "general",
                    include_raw_content:bool=False):
    """
    这是一个用于联网搜索的工具,你可以用它来进行联网搜索信息
    :param query:
    :param max_results:
    :param topic:
    :param include_raw_content:
    :return:
    """
    return tavily_client.search(
        query=query,
        max_results=max_results,
        topic=topic,
        include_raw_content=include_raw_content,
    )


research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""


deepagent = create_deep_agent(
    model=init_model(),
    tools=[internet_serach],
    system_prompt=research_instructions,
)


def build_messages(message:list, history): #tips:因为传入的是{"messages":[{"role":"user","content":"xxx"}]}这样的形式
    messages = [] #构建消息列表

    for item in history:
        role = item.get("role")
        content = item.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": message})
    return messages


async def predict(message,history):
    total_resp=""

    inputs={
        "messages":build_messages(message,history)
    }

    async for chunk,metadata in deepagent.astream(
        inputs,
        stream_mode="messages"
    ):
        content=getattr(chunk,'content','')

        if not content:
            continue

        if isinstance(content,list):
            text=""
            for item in content:
                if isinstance(item,dict):
                    text+=item.get("text","")

                else:
                    text+=str(item)

        else:
            text=str(content)

        if text:
            total_resp += text
            yield total_resp
            await asyncio.sleep(0.01)


if __name__ == '__main__':
    demo=gr.ChatInterface(
        predict,
        title="联网搜",
        examples=[
            "什么是LORA"
        ],
        multimodal=False,
        autofocus=True,

    )

    demo.launch(
        server_name="localhost",
        server_port=8080,
        share=False,
        debug=True

    )