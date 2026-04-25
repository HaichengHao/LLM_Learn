# @Time    : 2026/4/6 18:47
# @Author  : hero
# @File    : app.py


'''
分步
加载向量数据
构建提示词
构建ragchain
利用redis-stack-server做历史记录
用gradio做可视化
'''
import gradio as gr
import torch
from langchain_core.output_parsers import StrOutputParser

from langchain_redis import RedisVectorStore, RedisConfig
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory, RunnableConfig
import os
from operator import itemgetter
import asyncio
import uuid  #important:准备实现会话隔离
load_dotenv()
MODEL_PATH = '/home/nikofox/.cache/huggingface/hub/models--BAAI--bge-large-zh-v1.5/snapshots/79e7739b6ab944e86d6171e44d24c997fc1e0116'

zai_key = os.getenv('zhipu_key')
zai_url = os.getenv('zhipu_base_url')

embed_model = HuggingFaceEmbeddings(
    model_name=MODEL_PATH,
    model_kwargs={"device": "cuda:0" if torch.cuda.is_available() else "cpu"},
)

chroma_store = Chroma(
    persist_directory='./idol46_chroma',
    embedding_function=embed_model,
)
retriver = chroma_store.as_retriever(search_kwargs={'k': 3})

llm = ChatOpenAI(
    model='glm-4',
    api_key=zai_key,
    base_url=zai_url
)

prompt_template = ChatPromptTemplate(
    messages=[
        ('system',
         '你先在是偶像团体nogizaka46的其中一位超级偶像,你现在角色未被指定,不要自己猜测你自己是谁,只有被指定后,你才有自己的角色,才有“设定”,你需要按照用户给你指定的角色作为你自己的角色,并根据上下文回答问题'),
        ('system', '上下文\n{context}'),
        MessagesPlaceholder(variable_name='history'),
        ('human', '{user_quiz}')
    ]
)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
        {
            "context": itemgetter('user_quiz') | retriver | (
                lambda docs: "\n\n".join([d.page_content for d in docs])),
            'user_quiz': itemgetter('user_quiz'),
            'history': itemgetter('history')
        }
        | prompt_template
        | llm
        | StrOutputParser()
)

def generate_session_id():
    return str(uuid.uuid4())

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


async def predict_aysnc(message, history,request:gr.Request):
    session_id = request.session_hash  #tips:做不同用户之间的隔离
    config_runnable = RunnableConfig(
        configurable={
            'session_id': session_id
        }
    )
    full_response = ''
    async for chunk in chain_with_history.astream(
            input={'user_quiz': message}, config=config_runnable

    ):
        full_response += chunk
        await asyncio.sleep(0.01)
        yield full_response


if __name__ == '__main__':
    demo=gr.ChatInterface(
        fn=predict_aysnc,
        title='IDOL46',
        description='🎉Happy CheatDay',
        examples=[
            "第5单曲Center是谁?",
            "井上和C了哪几单?"
        ],
        multimodal=False,
        autofocus=True,
    )

    demo.launch(
        server_name="127.0.0.1",
        server_port=6446,
        share=False,
        debug=True
    )