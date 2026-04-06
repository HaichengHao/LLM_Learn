# @Time    : 2026/4/4 15:39
# @Author  : hero
# @File    : query_retriver_generate.py
'''
这次我将结合实际场景,利用大模型结合RAG
做出一个法律顾问智能体
'''
from langchain_core.output_parsers import StrOutputParser

'''
分步骤

1.构建retriver(实例化embedding模型,并构造retriver)
2.构建带历史记录的runnable对象
3.构建chain
4.构建agent
'''
import asyncio
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough,RunnableConfig
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory
import os
import torch
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


#step --------------构建提示词等-------------
# 构造提示词
prompt_template = ChatPromptTemplate(
    [('system','你是一个法律顾问助手,请根据上下文回答问题'),
    ('system','上下文{context}'),
    MessagesPlaceholder(variable_name='history'),
    ('human','{user_quiz}')]
)

# Define a function to format the retrieved documents important:或者直接把这个公布功能给提出来
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

#important:仔细看chain！！！！！
rag_chain = (
    {
        "context": itemgetter("user_quiz") | retriver | (
            lambda docs: "\n\n".join([d.page_content for d in docs])
        ),
        "user_quiz": itemgetter("user_quiz"),
        "history": itemgetter("history")   # 必须加这一行！！不然出莱格式文体
    }
    | prompt_template
    | llm
    | StrOutputParser()
)

#step --------------实现记忆模块-----------------

def get_session_history(session_id:str):
    return RedisChatMessageHistory(
        session_id=session_id,
        url='redis://127.0.0.1:65522/6',
        ttl=1200
    )

chain_with_history=RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key='user_quiz',
    history_messages_key='history'
)

config=RunnableConfig(
    configurable={
        'session_id':'chat_lawyer_v1'
    }
)

# async def chat_loop():
#     print('\n🥳爱情公寓最有种的男人来了!为您提供最优质的服务,鄙人张益达,你也可以叫我snake~~~🐍(输入quit退出)')
#     while True:
#         user_input=input('\n输入你想问的问题骚年>').strip()
#         if user_input.lower()=='quit':
#             break
#         try:
#             print('🕵️',end='',flush=True)
#             async for chunk in chain_with_history.astream(
#                    {'user_quiz':user_input},config
#             ):
#                 print(chunk,end='',flush=True)
#             print('\n')
#         except Exception as e:
#             logger.error(f'\n出错了:{e}')
#
#     logger.info('谢谢您的提问!🎉')
# def chat_loop():
#     print('\n🥳爱情公寓最有种的男人来了!为您提供最优质的服务,鄙人张益达,你也可以叫我snake~~~🐍(输入quit退出)')
#     while True:
#         user_input = input('\n输入你想问的问题骚年>').strip()
#         if user_input.lower() == 'quit':
#             break
#         try:
#             print('🕵️ 正在思考...', end='', flush=True)
#             # --- 关键修改：使用 ainvoke ---
#             result = chain_with_history.invoke(
#                 {'user_quiz': user_input}, config
#             )
#             print(f"\n✅ {result}\n") # 打印完整结果
#         except Exception as e:
#             logger.error(f'\n出错了:{e}')
#             import traceback
#             traceback.print_exc() # 打印完整的错误堆栈！
#
#     logger.info('谢谢您的提问!🎉')
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



