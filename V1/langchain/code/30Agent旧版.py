# @Time    : 2026/4/1 21:41
# @Author  : hero
# @File    : 30Agent旧版.py

'''
agent创建的方式有两种,这里有两种方式
v0.x方式
Model->Tools->Prompt->Agent->Executor
v1.x新方式
create_agent()->Agent

'''

from langchain_classic.agents import create_openai_tools_agent,AgentExecutor
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory, RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import RedisChatMessageHistory
from dotenv import load_dotenv
from loguru import logger
import os
import asyncio
from langchain_tavily import TavilySearch
from langchain_community.tools import tool
import json
import httpx


load_dotenv()

langsmith_key = os.getenv('lang_smith_key')
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


llm_zai = ChatOpenAI(
    model='glm-4',
    api_key=zai_key,
    base_url=zai_url,
    temperature=0.6,
    max_retries=2
)
prompt_template=ChatPromptTemplate(
    messages=[
        ('system','你现在是一天气播报员'),
        MessagesPlaceholder(variable_name='history'),
        ('human','{user_input}'),
        MessagesPlaceholder(variable_name='agent_scratchpad') #important:这里需要传入,获取到工具调用

    ]
)
agent = create_openai_tools_agent(
    llm=llm_zai,
    prompt=prompt_template,
    tools=[get_weather]
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=[get_weather],
    handle_parsing_errors=True,
    verbose=False
)


REDIS_URL=os.getenv('REDIS_DOCKER')
def get_session_history(session_id:str):
    return RedisChatMessageHistory(
        session_id=session_id,
        url=REDIS_URL,
        ttl=600
    )
chain_with_history = RunnableWithMessageHistory(
    agent_executor, #important：这里传入的是agent_executor,注意不是传入之前的chain
    get_session_history,
    input_messages_key='user_input',
    history_messages_key='history'

)


config=RunnableConfig(
    configurable={
        'session_id':'chat_v0_1'
    }
)

async def chat_loop():
    print('欢迎提问>>')
    while True:
        user_input=input('请输入你想问的问题>>>>>').strip()
        if user_input.lower()=='quit':
            break
        try:
            res = await chain_with_history.ainvoke(
                {'user_input':user_input},config
            )
            if res:
                print(res['output'])
        except Exception as e:
            logger.error(f'出现了如下问题>{e}')
    logger.info('拜拜')


if __name__ == '__main__':
    asyncio.run(chat_loop())
