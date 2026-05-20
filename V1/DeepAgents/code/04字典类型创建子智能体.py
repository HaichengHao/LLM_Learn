# @Time    : 2026/5/17 11:32
# @Author  : hero
# @File    : 04字典类型创建子智能体.py

from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent
from langchain.agents.middleware import SummarizationMiddleware,ModelCallLimitMiddleware
import asyncio
import os
from dotenv import load_dotenv, find_dotenv
import json

load_dotenv()

# 极简初始化
llm = init_chat_model(
    model='glm-4',
    model_provider='openai',
    api_key=os.getenv('zhipu_key'),
    base_url=os.getenv('zhipu_base_url')
)

"""
创建一个主智能体,它拥有三个助手
1.天气助手
2.计算助手
3.翻译助手

"""

# 1.创建一个天气助手

weather_agent = {
    "name": "weather_helper",  # 名称
    "description": "用于查询天气信息的智能助手,当用户查询天气的时候，调用此助手完成任务",  # 描述，给main_agent看的
    "system_prompt": "你是一个天气查询的助手,无论是用户查询哪个城市,你统一回复:'今日天气晴朗，气温28度'",  # 系统提示词,给llm看的
    "tools": [],  # 工具
    "middleware":[  #中间件,之后会详细写
        SummarizationMiddleware(
            model=llm,
            trigger=('tokens', 4000),
            keep=('messages', 20)

        )
    ]
}

# 2. 定义子智能体：计算助手
math_agent = {
    "name": "math_helper",
    "description": "用于处理数学计算问题。",
    "system_prompt": "你是一个严谨的数学助手。请帮助用户计算数学问题。",
    "tools": []
}

# 3. 定义子智能体：翻译助手
translate_agent = {
    "name": "translator",
    "description": "用于中英互译任务。",
    "system_prompt": "你是一个翻译助手。如果是中文请翻译成英文，如果是英文请翻译成中文。",
    "tools": []
}

# 创建主智能体

main_agent = create_deep_agent(
    name="main_agent",
    model=llm,
    subagents=[
        weather_agent,
        math_agent,
        translate_agent
    ],
    system_prompt="你是一个全能管家。你会根据用户的需求，调度不同的助手来解决问题。"

)


async def test_stream(query):
    """
    使用mainagent执行传入的问题
    :param query:
    :return:
    """
    stream = main_agent.astream({
        "messages": [
            {'role': 'user', 'content': query}
        ]
    }
    )

    async for chunk in stream:
        # chunk ->{"model/tools":{"messages":[{},{},{}]}}
        # model | {messages:[]}
        for node_name, state in chunk.items():  # .item()是将chunk转换成(k,v)列表[("model/tools","{'messages':[{},{},{}]}"]
            # 如果state是None,或者state没有messages就跳过
            if state is None or "messages" not in state:
                continue
            else:
                # 获取messages数据
                messages = state["messages"]
                if messages and isinstance(messages, list):  # tips:如果非空且是一个列表
                    last_msg = messages[-1]
                    # 决定如何处理
                    # 如果node_name=model 1.大模型决定调用工具了/大模型决定调用agent/大模型返回结果了

                    if node_name == 'model':
                        # model来决定返回的结果并决定调用哪些工具
                        if last_msg.tool_calls:
                            # 决定调用子工具或者subAgent
                            for tool_call in last_msg.tool_calls:
                                if tool_call['name'] == 'task':
                                    # 决定调用某个subAgent
                                    print(f'[model]决定调用子智能体{tool_call['args']['subagent_type']}')
                                else:
                                    # 决定调用某个工具
                                    print(f'[model]决定调用子工具{tool_call['name']}')

                        elif last_msg.content:
                            # 提取模型返回的最终结果
                            print(f'[model]返回最终结果{last_msg.content}')
                    elif node_name == 'tools':
                        # agent => 调用自己的工具了，并获取了结果
                        name = last_msg.name
                        content = last_msg.content
                        print(f'[Agent]调用了具体的工具{name},返回的结果为{content}')


# test_stream("北京今天的天气怎么样")
# test_stream("1+17等于多少?")
# test_stream("请将'fake it , until you make it '翻译成中文")


if __name__ == '__main__':
    async def batch_run():
    # 获取要并发执行的对象
        test1=test_stream("北京天气如何?")
        test2 = test_stream("999-876等于多少?")
        print(type(test1))
        print(type(test2))

        await asyncio.run(test1,test2)
    asyncio.run(batch_run())


