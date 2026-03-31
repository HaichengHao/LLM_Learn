# @Time    : 2026/3/30 17:31
# @Author  : hero
# @File    : 06添加记忆psql版.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_tavily import TavilySearch
# 引入 PostgresSaver
from langgraph.checkpoint.postgres import PostgresSaver

load_dotenv()

# 1. 初始化模型
api_key = os.getenv("api_key")
base_url = os.getenv("base_url")

model = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model="gpt-4o-mini"
)

# 2. 定义工具
custom_tool = [TavilySearch(max_results=3)]

# 3. 配置 PostgresSaver
# 格式: postgresql://用户:密码@主机:端口/数据库名
DB_URI = f"postgresql://nikofox:@localhost:5432/llmdb?sslmode=disable"

# 使用上下文管理器管理连接，或者在应用启动时初始化
# 注意：生产环境建议使用连接池，这里为了演示使用简单方式
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    # 这一行非常重要！它会自动在数据库中创建 checkpoint 相关的表
    checkpointer.setup()

    # 4. 创建 Agent
    agent = create_agent(
        model=model,
        tools=custom_tool,
        checkpointer=checkpointer
    )

    # 5. 调用 Agent
    # 关键点：使用 PostgresSaver 时，必须传入 config 配置 thread_id
    # thread_id 用于区分不同的会话，相同的 thread_id 会共享记忆
    config = {"configurable": {"thread_id": "user_session_001"}}

    print(">>> 第一轮对话：我叫张三")
    agent.invoke({"messages": [("user", "我叫张三")]}, config)

    print(">>> 第二轮对话：我叫什么名字？")
    # 此时 Agent 应该能记住你叫张三，因为状态被保存到了 Postgres 中
    response = agent.invoke({"messages": [("user", "我叫什么名字？")]}, config)

    print(response["messages"][-1].content)