# @Time    : 2026/4/1 11:41
# @Author  : hero
# @File    : 26记忆缓存持续对话版.py
import asyncio

from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import  RunnableWithMessageHistory
from dotenv import load_dotenv
from loguru import logger
import os
load_dotenv()
langsmith_key =os.getenv('lang_smith_key')
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = f'{langsmith_key}'
zai_key = os.getenv('zhipu_key')
zai_url = os.getenv('zhipu_base_url')

llm_zai = ChatOpenAI(
    model='glm-4',
    api_key=zai_key,
    base_url=zai_url,
    temperature=0.6,
    max_retries=2
)

prompt_template=ChatPromptTemplate(
    messages=[
        ('system','你现在是一名五星级大厨师'),
        MessagesPlaceholder(variable_name='history'),
        ('human','{user_input}')

    ]
)

parser = StrOutputParser()

chain = prompt_template|llm_zai|parser

REDIS_DB_URL = 'redis://127.0.0.1:65522/6'
def get_session_history(session_id:str) -> RunnableWithMessageHistory:
    return RedisChatMessageHistory(
        session_id=session_id,
        url=REDIS_DB_URL,
        ttl=360 #tips:保存六分钟记录
    )


chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    history_messages_key='history',
    input_messages_key='user_input',
)

config=RunnableConfig(
    configurable={
        'session_id':'chat_1'
    }
)


async def chat_loop():
    print('\n👨‍🍳 新东方超级大厨已启动,输入"quit"退出')
    while True:
        user_quiz= input('\n输入你的问题>').strip()
        if user_quiz.lower()=='quit':
            break
        try:
            result = await chain_with_history.ainvoke({'user_input':user_quiz},config)
            if result:
                print(f'👨‍🍳{result}\n')
        except Exception as e:
            logger.error(f'\n出错了⚠️:{e}')


    #tips:清理
    logger.info('谢谢您的提问!🎉')


if __name__ == '__main__':
    asyncio.run(chat_loop())