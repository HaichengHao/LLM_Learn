# @Time    : 2026/3/30 15:02
# @Author  : hero
# @File    : 03Agent创建与使用.py

from langchain.agents import create_agent
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from datetime import datetime
load_dotenv()
#tips:注意配置TAVILY_API_KEY

api_key=os.getenv('api_key')
base_url=os.getenv('base_url')
zai_key = os.getenv('zhipu_key')
zai_url = os.getenv('zhipu_base_url')
tavily_tool_search=TavilySearch(
    max_results=2 #tips:最大搜索数量
)


# model = ChatOpenAI(
#     api_key=zai_key,
#     base_url=zai_url,
#     model='glm-4'
# )
model = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model='gpt-4o-mini'
)
tools = [tavily_tool_search]
agent=create_agent(
    model=model,
    tools=tools,
    system_prompt='你是一个职能助手,能够选择合适的工具帮助用户解决问题',

)

#important:agent不能直接传字符串了
res = agent.invoke({'messages':[{"role":"human","content":f"今天{datetime.now()}北京天气如何?"}]})
print(res['messages'][-1]['content']) #tips:至于为什么这么写,可以看看res的输出结构,是一个'messages'为键的字典，值是一个各种Message组成的一个列表,而这个列表的最后一个则是我们要的