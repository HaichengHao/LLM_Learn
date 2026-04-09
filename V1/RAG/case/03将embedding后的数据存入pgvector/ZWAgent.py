# @Time    : 2026/4/7 17:27
# @Author  : hero
# @File    : ZWAgent.py
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic import create_tool_calling_agent, AgentExecutor
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables import RunnableConfig
import asyncio
import os
import torch
from loguru import logger
from dotenv import load_dotenv
from operator import itemgetter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector

load_dotenv()
api_key = os.getenv('api_key')
base_url = os.getenv('base_url')
MODEL_PATH = '/home/nikofox/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/79e7739b6ab944e86d6171e44d24c997fc1e0116'

# Step 1: 构建对话大模型
llm = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model='gpt-4o-mini'
)

# Step 2: 构建retriever
embeddings_model = HuggingFaceEmbeddings(
    model_name=MODEL_PATH,
    model_kwargs={
        'device': 'cuda:0' if torch.cuda.is_available() else 'cpu'
    }
)

vector_store = PGVector(
    connection=os.getenv('psql_url'),
    collection_name='demo_pgv1',
    embeddings=embeddings_model,
)

retriever = vector_store.as_retriever(search_kwargs={'k': 3})

# Step 3: 定义检索工具
@tool
def legal_document_search(query: str) -> str:
    """搜索法律相关文档以获取相关信息"""
    docs = retriever.get_relevant_documents(query)
    return "\n\n".join([doc.page_content for doc in docs])

# Step 4: 定义其他可能需要的工具（可扩展）
@tool
def current_time() -> str:
    """获取当前时间"""
    import datetime
    return str(datetime.datetime.now())

# Step 5: 创建工具列表
tools = [legal_document_search, current_time]

# Step 6: 创建代理提示模板
system_prompt = """你是一个法律顾问助手。你可以：
1. 使用法律文档搜索工具查找相关信息
2. 获取当前时间
3. 根据上下文和检索到的信息回答用户问题

请合理使用工具来获取准确信息，再进行回答。"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Step 7: 创建工具调用代理
agent = create_tool_calling_agent(llm, tools, prompt)

# Step 8: 创建代理执行器
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

# Step 9: 添加历史记录功能
def get_session_history(session_id: str):
    return RedisChatMessageHistory(
        session_id=session_id,
        url='redis://127.0.0.1:65522/6',
        ttl=1200
    )

# Step 10: 创建带历史记录的代理
agent_with_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

config = RunnableConfig(
    configurable={
        'session_id': 'chat_lawyer_v1'
    }
)

def chat_loop():
    print('\n🥳爱情公寓最有种的男人来了!为您提供最优质的服务,鄙人张益达,你也可以叫我snake~~~🐍(输入quit退出)')
    while True:
        user_input = input('> ').strip()
        if user_input == 'quit':
            break

        try:
            print('🕵️ 正在思考...', end='', flush=True)

            result = agent_with_history.invoke(
                {'input': user_input}, config
            )

            print(f"\n✅ {result['output']}\n")  # 注意：代理的结果在'output'键中

        except Exception as e:
            logger.error(e)

if __name__ == '__main__':
    chat_loop()