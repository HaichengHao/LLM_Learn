# @Time    : 2026/4/2 10:23
# @Author  : hero
# @File    : 32agent带记忆.py
# @Time    : 2026/4/2
# @Author  : hero (pure LangChain 1.0+ style)
# @File    : 31Agent新版_纯1.0带记忆.py
from langchain_core.runnables import RunnableConfig, RunnablePassthrough
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from dotenv import load_dotenv
import os
import httpx
import json
from loguru import logger
import asyncio

load_dotenv()
zai_key = os.getenv('zhipu_key')
zai_url = os.getenv('zhipu_base_url')


# ------------------ 工具 ------------------
@tool
def get_weather(city: str):
    url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {
        'q': city,
        'appid': os.getenv('OPENWEATHER_API_KEY'),
        'units': 'metric',
        'lang': 'zh_cn'
    }
    try:
        resp = httpx.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return json.dumps(resp.json(), ensure_ascii=False)
    except Exception as e:
        return f"查询失败: {e}"


# ------------------ 创建 1.0+ Agent ------------------
model = ChatOpenAI(api_key=zai_key, base_url=zai_url, model='glm-4')

# ⭐ 直接使用 create_agent（1.0+ 核心）
from langchain.agents import create_agent

agent = create_agent(
    model,
    tools=[get_weather],
    system_prompt="你是一个天气播报员，请使用工具查询天气并回答用户。"
)


# 注意：此时 agent 是一个 Runnable，输入应为 {"messages": [...]}
# 输出为 {"messages": [..., AIMessage]}

# ------------------ 记忆适配器 ------------------
# 我们需要把 {"input": "...", "chat_history": [...]} 转成 {"messages": [...]}

'''
def format_input(data):
    """将 RunnableWithMessageHistory 的输入转为 agent 所需的 messages 格式"""
    chat_history = data.get("chat_history", [])
    user_input = data["input"]
    # 合并历史 + 当前消息
    messages = chat_history + [HumanMessage(content=user_input)]
    return {"messages": messages}


# 构建带格式转换的 runnable
agent_with_format = RunnablePassthrough.assign(
    formatted_input=format_input
).assign(
    output=lambda x: agent.invoke({"messages": x["formatted_input"]["messages"]})
).pick("output") #tips:取出pic键的值
'''
# 但更简洁的方式：用 lambda 包装
from langchain_core.runnables import RunnableLambda

#important:封装一个带历史信息调用的方法
def invoke_agent_with_history(data):
    messages = data["chat_history"] + [HumanMessage(content=data["input"])]
    result = agent.invoke({"messages": messages})
    # 提取最后一条 AI 消息作为输出
    last_msg = result["messages"][-1]
    return {"output": last_msg.content if hasattr(last_msg, 'content') else str(last_msg)}


#important:利用RunnableLambda将其封装为runnable对象
agent_runnable = RunnableLambda(invoke_agent_with_history)

# ------------------ 添加记忆 ------------------
REDIS_URL = 'redis://127.0.0.1:65522/6'


def get_session_history(session_id: str):
    return RedisChatMessageHistory(session_id=session_id, url=REDIS_URL, ttl=600)


# ⭐ 关键：history_messages_key 必须是 "chat_history"
runnable_with_history = RunnableWithMessageHistory(
    agent_runnable, #tips:传入runnable对象
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)


# ------------------ 异步聊天循环 ------------------
async def chat_loop():
    config = {"configurable": {"session_id": "weather_1.0_v1"}}
    print("🌤️ 纯 LangChain 1.0+ 天气助手（带记忆）启动！输入 'quit' 退出。")

    while True:
        user_input = input("\n你: ").strip()
        if user_input.lower() == 'quit':
            break
        try:
            response = await runnable_with_history.ainvoke(
                {"input": user_input},
                config=config
            )
            print(f"\n🤖: {response['output']}")
        except Exception as e:
            logger.error(f"❌ 错误: {e}")
            print(f"⚠️ 出错了: {e}")


if __name__ == '__main__':
    asyncio.run(chat_loop())