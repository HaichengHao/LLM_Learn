# @Time    : 2026/3/31 14:25
# @Author  : hero
# @File    : 07体验skills.py
# @Time    : 2026/3/30 15:02
# @Author  : hero
# @File    : 03Agent创建与使用.py

from langchain_classic.agents import create_tool_calling_agent,AgentExecutor
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptFormat, MessagesPlaceholder
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# === 配置 ===
api_key = os.getenv('api_key')
base_url = os.getenv('base_url')
# zai_key = os.getenv('zhipu_key')
# zai_url = os.getenv('zhipu_base_url')

# 原始工具（保留）
tavily_tool = TavilySearch(max_results=3)


# === Step 1: 定义我们的 "Weather Research Skill" ===
@tool
async def weather_research_skill(query: str) -> str:
    """
    智能天气调研技能：接收自然语言天气问题，返回结构化天气摘要。
    内部会调用搜索引擎，并用LLM解析结果。
    """
    from langchain_core.messages import HumanMessage
    import asyncio

    # 使用同一个模型做后处理（也可以换更强的模型）
    llm = ChatOpenAI(api_key=api_key, base_url=base_url, model='gpt-4o-mini')

    # 第一步：用 Tavily 搜索原始信息
    search_results = await tavily_tool.ainvoke({"query": f"site:weather.com OR site:accuweather.com {query} 实时天气"})

    # 提取文本内容（Tavily 返回的是 {'results': [...]}）
    raw_content = "\n".join([r.get("content", "") for r in search_results.get("results", [])])
    if not raw_content.strip():
        return "未找到可靠的天气信息。"

    # 第二步：让 LLM 解析并生成规范摘要
    parse_prompt = f"""
你是一位专业气象助手。请根据以下网络搜索到的天气信息，回答用户的问题。
要求：
- 只基于提供的信息，不要编造；
- 回答简洁，包含：城市、日期、天气状况（晴/雨等）、气温范围；
- 如果信息矛盾，说明“信息不一致”；
- 最后附上一句“信息来源于网络公开天气服务”。

用户问题：{query}

搜索到的信息：
{raw_content}
"""
    response = await llm.ainvoke([HumanMessage(content=parse_prompt)])
    return response.content


# === Step 2: 创建 Agent，只暴露这个 Skill（而不是原始 Tavily）===
model = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model='gpt-4o-mini'
)

# 注意：现在 tools 列表里只有我们封装好的 Skill
tools = [weather_research_skill]

# 使用新版 create_tool_calling_agent（推荐）
prompt = ChatPromptFormat.from_messages([
    ("system", "你是一个智能助手，能使用高级技能帮助用户获取准确信息。"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

#tips:该智能体是0.3版本通用写法!!!
agent = create_tool_calling_agent(model, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# === Step 3: 调用 ===
user_query = f"今天{datetime.now().strftime('%Y年%m月%d日')}北京天气如何？"
result = agent_executor.invoke({"input": user_query})
print("\n最终回答：")
print(result["output"])