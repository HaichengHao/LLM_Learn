# @Time    : 2026/4/6 14:19
# @Author  : hero
# @File    : 34补充create_tool_calling_agent.py
from langchain_classic.agents import create_tool_calling_agent,AgentExecutor
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from langchain.tools import tool
import httpx
import json
import os
load_dotenv()
zai_key = os.getenv('zhipu_key')
zai_base_url = os.getenv('zhipu_base_url')

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


llm = ChatOpenAI(
    api_key=zai_key,
    base_url=zai_base_url,
    model='glm-4'
)
prompt_template=ChatPromptTemplate(
    [
        ('system','你现在是一名天气助手,可以帮我查询天气'),
        ('human','{user_input}'),
        MessagesPlaceholder(variable_name='agent_scratchpad'),
    ]
)
agent=create_tool_calling_agent( #tips:其实和之前我写的create_openai_tools_agent几乎一样
    llm=llm,
    tools=[get_weather,TavilySearch(max_results=3)],
    prompt=prompt_template,

)
agent_executor=AgentExecutor(
    agent=agent,
    tools=[get_weather,TavilySearch(max_results=3)],
    verbose=False,
    handle_parsing_errors=False,  #tips:注意这里和create_react_agent的对比
)

res = agent_executor.invoke({'user_input':'今天沈阳天气如何?'})
print(res)