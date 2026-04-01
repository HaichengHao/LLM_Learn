# @Time    : 2026/4/1 15:35
# @Author  : hero
# @File    : 28tool实现实时天气大模型.py
from langchain_core.runnables import RunnableConfig
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from dotenv import load_dotenv
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

#---------工具设置---------------

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





#--------链设置------------------
llm = ChatOpenAI(
    api_key=zai_key,
    base_url=zai_url,
    model='glm-4'
)

prompt_template = ChatPromptTemplate(
    messages=[
        ('system','你现在是一名天气播报员'),
        MessagesPlaceholder(variable_name='history'),
        ('human','{user_input}'),
        MessagesPlaceholder(variable_name='agent_scratchpad') #important:关键!让模型看到之前的工具调用
    ]
)

parser = StrOutputParser()

# ------------构建智能体---------------
agent=create_openai_tools_agent(
    llm,
    tools=[get_weather],
    prompt=prompt_template
)

agent_executor=AgentExecutor(
    agent=agent,
    tools=[get_weather],
    # verbose=True,
    verbose=False, #important:这样就可以不用看到详细的调用
    handle_parsing_errors='解析用户请求失败,请重新输入清晰的指令'

)


#-----------记忆设置-----------------
REDIS_URL = 'redis://127.0.0.1:65522/6'
def get_session_history(session_id:str):
    return RedisChatMessageHistory(
        session_id=session_id,
        url=REDIS_URL,
        ttl=600
    )
runnable_with_history=RunnableWithMessageHistory(
    agent_executor, #important:注意这里传入的是runnable对象,但是不再是chain了,而是agent_executor,它也是runnable对象
    get_session_history,
    input_messages_key='user_input',
    history_messages_key='history'
)
config = RunnableConfig(
    configurable={'session_id':'weather_agent_1'}
)

async def chat_loop():
    print('🧐天气助手加载成功!👋,输入"quit"退出!\n')
    while True:
        user_input=input('\n请输入你想咨询的天气问题:').strip()
        if user_input.lower() == 'quit':
            break
        try:
            res = await runnable_with_history.ainvoke({'user_input':user_input},config)
            if res:
                print(res['output'])
        except Exception as e:
            logger.error(f'\n出错了⚠️{e}')

    logger.info('拜拜🎊')

if __name__ == '__main__':
    asyncio.run(chat_loop())