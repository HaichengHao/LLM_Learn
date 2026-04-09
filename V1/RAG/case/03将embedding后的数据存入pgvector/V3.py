# @Time    : 2026/4/7 23:04
# @Author  : hero
# @File    : V3.py
# ... (保持之前的导入和初始化部分不变) ...
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough,RunnableConfig
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory
import os
import torch
from langchain_core.output_parsers import StrOutputParser
from loguru import logger
from dotenv import load_dotenv
from operator import itemgetter #important：必须的

load_dotenv()
api_key=os.getenv('api_key')
base_url=os.getenv('base_url')
MODEL_PATH = '/home/nikofox/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/79e7739b6ab944e86d6171e44d24c997fc1e0116'
#step ------------------构建对话大模型-------------------
llm = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model='gpt-4o-mini'
)


#step ---------------构建retriver-----------------------
#实例化模型方法

embeddings_model=HuggingFaceEmbeddings(
        model_name=MODEL_PATH,
        model_kwargs={
            'device': 'cuda:0' if torch.cuda.is_available() else 'cpu'
        }
    )


vector_store= PGVector(
        connection=os.getenv('psql_url'),
        collection_name='demo_pgv1',
        embeddings=embeddings_model,
    )

retriver = vector_store.as_retriever(search_kwargs={'k':3})


# step --------------构建提示词等-------------
# 简化系统提示词，但仍可提示参考上下文
prompt_template = ChatPromptTemplate(
    [
        ("system", "你是一个法律顾问助手，请根据以下上下文信息准确回答用户的问题。"),
        ("system", "上下文信息:\n{context}"), # 只传递内容，不强制要求引用
        MessagesPlaceholder(variable_name="history"),
        ("human", "{user_quiz}")
    ]
)

# 定义一个函数来格式化检索到的文档内容
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 定义一个函数来提取来源信息
def extract_sources(docs):
    """
    从检索到的文档列表中提取来源信息。
    """
    sources = set() # 使用集合去重
    for doc in docs:
        metadata = doc.metadata or {}
        # 根据你的文档入库时的 metadata 键名调整，例如 'source', 'filename', 'title' 等
        source = metadata.get('source') or metadata.get('filename') or metadata.get('title') or "未知来源"
        # 如果 metadata 中有页码等其他信息，也可以一并添加
        page = metadata.get('page')
        if page is not None:
            source += f" (页码: {page})"
        sources.add(source)
    return "\n".join([f"- {s}" for s in sources])

# 修改 RAG chain，使其不仅返回 AI 的回答，还返回来源
# 为此，我们创建一个 chain，它返回一个字典
def create_rag_chain_with_sources(llm, retriever, prompt_template):
    # 内部 chain: 接收 user_quiz 和 history，返回 AI 回答
    ai_answer_chain = (
        {
            "context": itemgetter("user_quiz") | retriever | format_docs,
            "user_quiz": itemgetter("user_quiz"),
            "history": itemgetter("history")
        }
        | prompt_template
        | llm
        | StrOutputParser()
    )

    # 总 chain: 返回包含 AI 回答和来源的字典
    full_chain = (
        {
            "answer": ai_answer_chain,
            "sources": itemgetter("user_quiz") | retriever | extract_sources, # 获取来源
            "original_query": itemgetter("user_quiz") # 如果需要原始查询，也可以传入
        }
        | (lambda x: f"{x['answer']}\n\n参考资料:\n{x['sources']}") # 在这里合并答案和来源
    )
    return full_chain

# 创建新的 chain
rag_chain_with_sources = create_rag_chain_with_sources(llm, retriver, prompt_template)

# ... (保持记忆模块部分不变) ...
def get_session_history(session_id:str):
    return RedisChatMessageHistory(
        session_id=session_id,
        url='redis://127.0.0.1:65522/6',
        ttl=1200
    )
chain_with_history = RunnableWithMessageHistory(
    rag_chain_with_sources, # 使用新的 chain
    get_session_history,
    input_messages_key='user_quiz',
    history_messages_key='history'
)

# ... (保持 config 不变) ...
config=RunnableConfig(
    configurable={
        'session_id':'chat_lawyer_v1'
    }
)

async def chat_loop():
    print('\n🥳爱情公寓最有种的男人来了!为您提供最优质的服务,鄙人张益达,你也可以叫我snake~~~🐍(输入quit退出)')
    while True:
        user_input = input('> ').strip()
        if user_input == 'quit':
            break

        try:
            print('🕵️ 正在思考...', end='', flush=True)

            # result 现在包含了 AI 回答和来源
            result = chain_with_history.invoke(
                {'user_quiz': user_input}, config
            )

            print(f"\n✅ {result}\n") # 打印完整的回答和来源

        except Exception as e:
            logger.error(e)

if __name__ == '__main__':
    # 注意：这里调用了异步函数，如果主函数是同步的，需要使用 asyncio.run
    # asyncio.run(chat_loop())
    # 但你的 chat_loop 现在是同步的，所以直接调用即可
    chat_loop()