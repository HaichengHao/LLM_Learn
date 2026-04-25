# @Time    : 2026/4/6 15:59
# @Author  : hero
# @File    : app_with_hyde.py

'''
分步
加载向量数据
构建提示词
构建ragchain (已集成HyDE)
利用redis-stack-server做历史记录
用gradio做可视化
'''
import gradio as gr
import torch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_redis import RedisVectorStore, RedisConfig
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableWithMessageHistory, RunnableConfig
from dotenv import load_dotenv
from langchain_community.chat_message_histories import RedisChatMessageHistory
import os
from operator import itemgetter
import asyncio
import uuid

load_dotenv()

# --- 配置部分 ---
MODEL_PATH = '/home/nikofox/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/79e7739b6ab944e86d6171e44d24c997fc1e0116'
zai_key = os.getenv('zhipu_key')
zai_url = os.getenv('zhipu_base_url')

# --- 1. 初始化模型与向量库 ---
embed_model = HuggingFaceEmbeddings(
    model_name=MODEL_PATH,
    model_kwargs={"device": "cuda:0" if torch.cuda.is_available() else "cpu"},
)

chroma_store = Chroma(
    persist_directory='./idol46_chroma',
    embedding_function=embed_model,
)

# 修正原代码中的拼写错误：serarch_kwargs -> search_kwargs
retriever = chroma_store.as_retriever(search_kwargs={'k': 3})

llm = ChatOpenAI(
    model='glm-4',
    api_key=zai_key,
    base_url=zai_url,
    temperature=0  # HyDE通常建议使用较低温度以保持生成的稳定性
)

# --- 2. 定义 HyDE 相关组件 ---
# 定义 HyDE 的提示词：让模型基于问题生成一段假设性的回答
hyde_prompt_template = PromptTemplate.from_template(
    "请根据以下问题，撰写一段假设性的回答。"
    "这段回答应该包含可能的关键词和事实，用于帮助检索相关文档。"
    "不需要真的回答问题，只需要生成用于搜索的文本。\n\n问题: {question}\n假设性回答:"
)

# 构建 HyDE 链：输入问题 -> Prompt -> LLM -> 假设性文本
hyde_chain = hyde_prompt_template | llm | StrOutputParser()

# --- 3. 定义最终回答的 Prompt ---
prompt_template = ChatPromptTemplate.from_messages(
    [
        ('system',
         '你是偶像团体nogizaka46的其中一位超级偶像,你现在角色未被指定,不要自己猜测你自己是谁,只有被指定后,你才有自己的角色,才有“设定”,你需要按照用户给你指定的角色作为你自己的角色,并根据上下文回答问题'),
        ('system', '参考材料:\n{context}'),
        MessagesPlaceholder(variable_name='history'),
        ('human', '{user_quiz}')
    ]
)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# --- 4. 构建集成 HyDE 的 RAG Chain ---
# 逻辑流：
# 1. 从输入中提取 'user_quiz'
# 2. 将 'user_quiz' 传入 hyde_chain 生成假设文本
# 3. 使用假设文本进行向量检索 (retriever)
# 4. 格式化检索结果
rag_chain = (
        {
            # important:【核心修改】检索的输入不再是原始问题，而是经过 HyDE 链处理后的结果
            "context": itemgetter('user_quiz') | hyde_chain | retriever | format_docs,

            # 原始问题和历史记录直接透传
            'user_quiz': itemgetter('user_quiz'),
            'history': itemgetter('history')
        }
        | prompt_template
        | llm
        | StrOutputParser()
)


# --- 5. 历史记录与会话管理 ---
def get_session_history(session_id):
    return RedisChatMessageHistory(
        session_id=session_id,
        url='redis://127.0.0.1:65522/6',
        ttl=1200
    )


chain_with_history = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key='user_quiz',
    history_messages_key='history'
)


# --- 6. Gradio 交互接口 ---
async def predict_async(message, history, request: gr.Request):
    session_id = request.session_hash
    config_runnable = RunnableConfig(
        configurable={
            'session_id': session_id
        }
    )
    full_response = ''
    # 使用 astream 进行流式输出
    async for chunk in chain_with_history.astream(
            input={'user_quiz': message}, config=config_runnable
    ):
        full_response += chunk
        await asyncio.sleep(0.01)
        yield full_response


if __name__ == '__main__':
    demo = gr.ChatInterface(
        fn=predict_async,
        title='IDOL46 (HyDE Powered)',
        description='🎉Happy CheatDay (已启用HyDE假设文档增强检索)',
        examples=[
            "第5单曲Center是谁?",
            "井上和C了哪几单?"
        ],
        multimodal=True,
        autofocus=True,
    )

    demo.launch(
        server_name="127.0.0.1",
        server_port=6446,
        share=False,
        debug=True
    )