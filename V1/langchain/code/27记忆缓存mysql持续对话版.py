# @Time    : 2026/4/1 14:02
# @Author  : hero
# @File    : 27记忆缓存mysql版.py

from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory,RunnableConfig
from dotenv import load_dotenv
import os
from loguru import logger
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

#important: docker run -d -p 63306:3306 -e MYSQL_ROOT_PASSWORD=xxxxxxx mysql
mysql_url = f'mysql+pymysql://root:{os.getenv("MYSQL_DOCKER")}@127.0.0.1:63306/mem_llm' #tips:这里我用的是docker
def get_session_history(session_id:str):
    return SQLChatMessageHistory(
        session_id,
        connection=mysql_url,
        table_name='message_store',
    )
chain_with_history=RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key='user_input',
    history_messages_key='history'
)

config=RunnableConfig(
    configurable={
        'session_id':'chat_1'
    }
)

def chat_loop():
    print('\n👨‍🍳 新东方超级大厨已启动,输入"quit"退出')
    while True:
        user_quiz= input('\n输入你的问题>').strip()
        if user_quiz.lower()=='quit':
            break
        try:
            result = chain_with_history.invoke({'user_input':user_quiz},config)
            if result:
                print(f'👨‍🍳{result}\n')
        except Exception as e:
            logger.error(f'\n出错了⚠️:{e}')


    #tips:清理
    logger.info('谢谢您的提问!🎉')


if __name__ == '__main__':
    chat_loop()