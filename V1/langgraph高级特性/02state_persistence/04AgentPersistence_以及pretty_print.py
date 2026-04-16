'''
其实这样的写法并不是最优的,因为langgraph的开发者希望它能够是一个全能的框架
但是过度的封装并不合适,还是之前那种agent结合runnable_with_history多一些

'''

from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langchain.agents import create_agent
from dotenv import load_dotenv
import os
import psycopg
load_dotenv()

zai_key = os.getenv('zhipu_key')
zai_url=os.getenv('zhipu_base_url')

# ==========定义大模型 ==========
llm = init_chat_model(
    model="glm-4",
    model_provider="openai",
    api_key=zai_key,
    temperature=0.0,
    base_url=zai_url
)

# 定义短期记忆使用内存（生产可以换 RedisSaver/PostgresSaver）
# checkpointer = InMemorySaver()

#tips:使用psql作检查点
psqlcheckpointer = PostgresSaver(
    conn=psycopg.connect(
        autocommit=True,
        dbname="lg_p1",
    )
)
psqlcheckpointer.setup()

# agent = create_agent(model=llm,checkpointer=checkpointer)
agent = create_agent(model=llm,checkpointer=psqlcheckpointer)
# 多轮对话配置，同一 thread_id 即同一会话
config = {"configurable": {"thread_id": "user-001"}}

msg1 = agent.invoke({"messages": [("user", "你好，我叫张三，喜欢足球，60字内简洁回复")]}, config)
print(msg1)
msg1["messages"][-1].pretty_print()

# 6. 第二轮（继续同一 thread）
msg2 = agent.invoke({"messages": [("user", "我叫什么？我喜欢做什么？")]}, config)
msg2["messages"][-1].pretty_print() #