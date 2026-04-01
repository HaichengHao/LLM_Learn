# @Time    : 2026/3/31 22:38
# @Author  : hero
# @File    : 25记忆缓存redis版.py

from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
load_dotenv()

zai_key = os.getenv('zhipu_key')
zai_url = os.getenv('zhipu_base_url')


llm_glm=ChatOpenAI(
    model='glm-4',
    api_key=zai_key,
    base_url=zai_url
)

prompt_template = ChatPromptTemplate(
    messages=[
        ('system','你现在是一心理专家'),
        MessagesPlaceholder(variable_name='history'),
        ('human','{user_input}')
    ]
)

parser = StrOutputParser()

chain=prompt_template|llm_glm|parser
#------从接下来这一块儿开始便是实现的方式了---------
# REDIS_URL='redis://127.0.0.1:6379/6'
REDIS_URL='redis://127.0.0.1:65522/6' #tips:测试docker redis/redis-stack-server
def get_session_history(session_id:str):
    return RedisChatMessageHistory(
        session_id=session_id,
        url=REDIS_URL,
        ttl=120 #tips:设置两分钟之后过期

    )

runnable_with_redis = RunnableWithMessageHistory(
    chain,
    get_session_history, #important:这里是必须要指定的,不然就无法根据sessionid来获取同一sessionid的上文
    input_messages_key='user_input',
    history_messages_key='history'
)

# -------------------------------------------
config = RunnableConfig(configurable={'session_id':'chat_1'})


resp1 = runnable_with_redis.invoke(
    {'user_input':'你好啊,我是hero，你叫什么名字?'},
    config
)

print(resp1)

print('***'*20)

resp2 = runnable_with_redis.invoke(
    {'user_input':'你还记得我叫什么名字么?'},
    config
)
print(resp2)