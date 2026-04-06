from langchain_classic.agents import create_react_agent,AgentExecutor
from langchain_core.prompts import PromptTemplate
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

# 使用标准的 ReAct 提示模板
template = """你是一个有用的助手。你可以使用以下工具:

{tools}

使用以下格式回答问题：
Question: 输入的问题
Thought: 你应该始终考虑该怎么做
Action: 要采取的操作，应该是 [{tool_names}] 中的一个
Action Input: 操作的输入
Observation: 操作的结果
... (这个 Thought/Action/Action Input/Observation 可以重复 N 次)
Thought: 我现在知道最终答案了
Final Answer: 原始输入问题的最终答案

开始!

Question: {input}
{agent_scratchpad}"""

prompt_template = PromptTemplate.from_template(template)#important:提示词要注意，和前面的不同,react_agent由于要将任务分为任务分块匹配合适的工具，所以会要求我们传入工具以及工具的名称

agent=create_react_agent(#important:它要求传入的prompt是BasePromptTemplate类的,它期望的是一个

    llm=llm,
    tools=[get_weather,TavilySearch(max_results=3)],
    prompt=prompt_template,
)

# 增加最大迭代次数，防止因迭代限制而停止
agent_executor=AgentExecutor(
    agent=agent,
    tools=[get_weather,TavilySearch(max_results=3)],
    verbose=True,  # 设为 True 来查看详细过程
    handle_parsing_errors=True,#important:这里也有要求的
    max_iterations=10  # 增加最大迭代次数
)

res = agent_executor.invoke({'input':'今天沈阳和平区天气如何?'})
print(res)

