# @Time    : 2026/4/28 17:36
# @Author  : hero
# @File    : 01快速入门.py

import asyncio
import gradio as gr
from typing import Literal
from tavily import TavilyClient
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from dotenv import load_dotenv
import os

load_dotenv()

zai_key = os.getenv("zhipu_key")
zai_url = os.getenv("zhipu_base_url")


#初始化tavily_client客户端
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def internet_search(
    query: str,#关键字
    max_results: int = 5,#条数
    topic: Literal["general", "news", "finance"] = "general",#类型
    include_raw_content: bool = False,#是否精简
):
    """Run a web search"""
    return tavily_client.search(
        query=query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


def init_model():
    return ChatOpenAI(
        model="glm-4",
        api_key=zai_key,
        base_url=zai_url,
        max_tokens=400,
        streaming=True,
    )


research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""

agent = create_deep_agent(
    model=init_model(),
    tools=[internet_search],
    system_prompt=research_instructions,
)


#直接调用,
# important:注意agent本质是用langgraph的,所以用langgraph的默认状态键messages
#下面是追溯到的源码
'''
class AgentState(TypedDict, Generic[ResponseT]):
    """State schema for the agent."""

    messages: Required[Annotated[list[AnyMessage], add_messages]]
    jump_to: NotRequired[Annotated[JumpTo | None, EphemeralValue, PrivateStateAttr]]
    structured_response: NotRequired[Annotated[ResponseT, OmitFromInput]]
    
    '''
demores=agent.invoke({
            "messages": [
                {"role": "user", "content": "今天沈阳和平区天气如何"}
            ]
        })

print(demores['messages'][-1]['content'])
#或者这里简单写
# res=agent.invoke(input="今天沈阳天气如何")



#下面的是写的用gradio结合异步生成器返回流式会话版本

#important：构建用来过滤消息的函数
def build_messages(message:list, history): #tips:因为传入的是{"messages":[{"role":"user","content":"xxx"}]}这样的形式
    messages = [] #构建消息列表

    for item in history:
        role = item.get("role")
        content = item.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": message})
    return messages


async def predict(message, history):
    total_resp = ""
    #important:关于构造inputs的格式,可以查看根目录下的彻底搞懂input的第五节,Agent和LangGraph通吃State
    # 由于Langgraph构造状态一般使用的是Annotated[list,add_messages],所以其常见输入如下
    '''
        {
            "messages": [
                {"role": "user", "content": "你好"}
            ]
        }'''
    inputs = {
        "messages": build_messages(message, history)#tips:这里返回的就是[{"role": "user", "content": "你好"}]这样的列表
    }


    #tips:如果指定用messages的模式输出的话返回的就是(chunk,metadata)
    async for chunk, metadata in agent.astream(
        inputs,
        stream_mode="messages", #tips:忘记的话就去看langgraph高级特性中的Streaming
    ):
        content = getattr(chunk, "content", "") #tips:这里用getattr获取chunk中的content
        #上面相当于content=chunk['content']
        if not content:
            continue

        if isinstance(content, list): #如果返回的内容是列表的话就遍历列表拿出内容元素
            text = ""
            for item in content:
                if isinstance(item, dict):
                    text += item.get("text", "")
                else:
                    text += str(item)
        else:
            text = str(content)

        if text:
            total_resp += text
            yield total_resp
            await asyncio.sleep(0.01)


# async def predict(
#         message,history
# ):
#     full_resp=''
#     async for chunk,metadata in agent.astream(input=message,stream_mode='messages'):
#         full_resp+=chunk['content']
#         await asyncio.sleep(0.01)
#         yield full_resp



if __name__ == "__main__":
    demo = gr.ChatInterface(
        fn=predict,
        title="联网搜索 demo",
        examples=[
            "木苹果是什么?",
            "印度尼西亚的首都在哪里?",
            "牡丹花用英文怎么说",
        ],
        multimodal=False,
        autofocus=True,
    )

    demo.launch(
        server_name="127.0.0.1",
        server_port=5558,
        share=False,
        debug=True,
    )