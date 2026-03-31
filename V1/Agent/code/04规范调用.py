from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.tools import TavilySearchResults
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

api_key = os.getenv('api_key')
base_url = os.getenv('base_url')

model = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model='gpt-4o-mini',
    temperature=0
)

tools = [TavilySearchResults(max_results=2)]

# 构建 prompt（必须包含 agent_scratchpad）
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能助手，可以使用工具解决问题。"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),  # 关键！
])

# 创建 agent（LangChain 1.x 支持此函数！）
agent = create_tool_calling_agent(model, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

query = f"今天{datetime.now().strftime('%Y-%m-%d')}北京天气如何？"
result = agent_executor.invoke({"input": query})

print("\n最终答案：")
print(result["output"])