# @Time    : 2026/4/28 15:42
# @Author  : hero
# @File    : agent_version.py

import os
import gradio as gr
import asyncio
from operator import itemgetter
import torch
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import init_chat_model
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory, RunnableConfig
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
MODEL_PATH = '/home/nikofox/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/79e7739b6ab944e86d6171e44d24c997fc1e0116'
api_key = os.getenv('zhipu_key')
base_url = os.getenv('zhipu_base_url')

langsmith_key = os.getenv('lang_smith_key')
os.environ['LANGSMITH_TRACING'] = 'true'
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = f'{langsmith_key}'

# 构建embedding需要的模型
embed_model = HuggingFaceEmbeddings(
    model_name=MODEL_PATH,
    model_kwargs={
        'device': 'cuda:0' if torch.cuda.is_available() else 'cpu',
    }
)

# 从chroma加载向量数据

chroma_store = Chroma(
    persist_directory='./idol46_chroma',
    embedding_function=embed_model
)

# 构建索引器
retriver = chroma_store.as_retriever(search_kwargs={'k': 3})

# 定义大模型
llm = ChatOpenAI(
    model='glm-4',
    api_key=api_key,
    base_url=base_url
)

# 构建提示词

prompt_template = ChatPromptTemplate(
    [
        ('system',
         '你先在是偶像团体nogizaka46的其中一位超级偶像,你现在角色未被指定,不要自己猜测你自己是谁,只有被指定后,你才有自己的角色,才有“设定”,你需要按照用户给你指定的角色作为你自己的角色,并根据上下文回答问题'),
        ('system', '上下文\n{context}'),
        MessagesPlaceholder(variable_name='history'),
        ('user', '{user_quiz}')
    ]
)

rag_chain = (
        {
            'context': itemgetter('user_quiz') | retriver | (lambda docs: "\n\n".join(d.page_content for d in docs)),
            'user_quiz': itemgetter('user_quiz'),
            'history': itemgetter('history')
        } | prompt_template | llm | StrOutputParser()
)

REDIS_URL = 'redis://127.0.0.1:56379/6'


def get_redis_history(session_id):
    return RedisChatMessageHistory(
        session_id=session_id,
        url=REDIS_URL,
        ttl=1200
    )


chain_with_history = RunnableWithMessageHistory(
    rag_chain,
    get_session_history=get_redis_history,
    input_messages_key='user_quiz',
    history_messages_key='history'
)


async def predict_async(message, history, request: gr.Request):
    session_id = request.session_hash

    config_runnable = RunnableConfig(
        configurable={
            'session_id': session_id
        }
    )

    full_response = ''
    async for chunk in chain_with_history.astream(
            input={
                'user_quiz': message,
            }, config=config_runnable
    ):
        full_response += chunk
        await asyncio.sleep(0.01)
        yield full_response


if __name__ == '__main__':
    demo = gr.ChatInterface(
        fn=predict_async,
        title='IDOL46',
        description='第几次的蓝天',
        examples=[
            '井上哪里出身？',
            '第五单C位是谁?'
        ],
        multimodal=False,
        autofocus=True
    )

    demo.launch(
        server_name='127.0.0.1',
        server_port=6446,
        share=False,
        debug=True

    )
