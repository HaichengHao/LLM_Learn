# @Time    : 2026/4/7 22:56
# @Author  : hero
# @File    : query_retriver_generatev2.py
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
# 修改系统提示词，告知模型需要引用来源
prompt_template = ChatPromptTemplate(
    [
        ("system",
         "你是一个法律顾问助手。请根据提供的上下文回答问题，并在回答末尾以 '参考资料:' 开头列出所有使用的来源。"),
        ("system", "上下文:\n{context_with_metadata}"),  # 使用包含元数据的上下文
        MessagesPlaceholder(variable_name="history"),
        ("human", "{user_quiz}")
    ]
)


# 定义一个函数来格式化检索到的文档及其元数据
def format_docs_with_metadata(docs):
    """
    将检索到的文档内容和其元数据（如来源）组合成一个字符串。
    假设每个文档的 `metadata` 字典中有 'source' 或 'filename' 等字段。
    """
    formatted_parts = []
    sources_set = set()  # 使用集合去重，避免重复的来源

    for doc in docs:
        content = doc.page_content
        metadata = doc.metadata or {}  # 防止 metadata 为 None
        source_info = f"来源: {metadata.get('source', '未知')}"  # 根据你的实际元数据键调整
        page_info = f", 页码: {metadata.get('page', 'N/A')}" if 'page' in metadata else ""  # 如果有页码
        full_source_detail = f"{source_info}{page_info}"

        formatted_parts.append(f"---\n{full_source_detail}\n{content}\n---")
        sources_set.add(full_source_detail)

    context_str = "\n\n".join(formatted_parts)

    # 拼接所有唯一的来源信息
    all_sources = "\n".join(sources_set)

    return context_str, all_sources


# 修改 RAG chain 以包含元数据
rag_chain_from_docs = (
        {
            "context_with_metadata": lambda input_dict: format_docs_with_metadata(input_dict["docs"]),
            "all_sources": lambda input_dict: format_docs_with_metadata(input_dict["docs"])[1],  # 提取来源列表
            "user_quiz": itemgetter("user_quiz"),
            "history": itemgetter("history")
        }
        | prompt_template
        | llm
        | StrOutputParser()
)

# 重构主 chain，先检索再传递给处理函数
retrieval_chain = (
        {
            "docs": itemgetter("user_quiz") | retriver,
            "user_quiz": itemgetter("user_quiz"),
            "history": itemgetter("history")
        }
        | rag_chain_from_docs
)

# ... (保持记忆模块部分不变) ...
def get_session_history(session_id:str):
    return RedisChatMessageHistory(
        session_id=session_id,
        url='redis://127.0.0.1:65522/6',
        ttl=1200
    )
chain_with_history = RunnableWithMessageHistory(
    retrieval_chain,  # 使用修改后的 chain
    get_session_history,
    input_messages_key='user_quiz',
    history_messages_key='history'
)

# ... (保持 config 和 chat_loop 函数不变) ...
config=RunnableConfig(
    configurable={
        'session_id':'chat_lawyer_v1'
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

            result = chain_with_history.invoke(
                {'user_quiz': user_input}, config
            )

            print(f"\n✅ {result}\n")

        except Exception as e:
            logger.error(e)

if __name__ == '__main__':
    chat_loop()
