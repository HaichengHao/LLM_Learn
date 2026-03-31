# @Time    : 2026/3/30 17:10
# @Author  : hero
# @File    : 05添加记忆.py

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver #important：注意这里使用的是langgraph的哦!!
from langchain_tavily import TavilySearch
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
import os
import datetime

load_dotenv()

api_key = os.getenv("api_key")
base_url = os.getenv("base_url")


model = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model="gpt-4o-mini"
)

custom_tool = [TavilySearch(max_result=3)]
agent=create_agent(
    model=model,
    tools=custom_tool,
    checkpointer=InMemorySaver(),

)

res1 = agent.invoke({'messages':[ #important:这里暂时必须写messages作为键,因为这是langgraph里默认的,之后学到langgraph之后就会明白
    {'role':'human','content':f'今天{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}辽宁省沈阳市和平区天气怎么样?',
     }
]},config={'configurable':{'thread_id':'demo1'}})
res2 = agent.invoke({'messages':[
    {'role':'human',
     'content':'那我要不要带伞呢?'}
]},config={'configurable':{'thread_id':'demo1'}})

print(res1)
print('*'*40)
print(res2)
print('*'*40)
print(res2['messages'])
print('*'*40)
print(res2['messages'][-1].content)
# 根据最新的天气预报，2026年3月30日在沈阳市和平区预计没有降水。因此，你不需要带伞。请放心出行！如果有其他问题或者需要了解更多信息，请告诉我。

#tips:res2成功识别到