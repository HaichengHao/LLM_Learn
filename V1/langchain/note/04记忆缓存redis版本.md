# 记忆缓存redis版本

关键就是`RunnableWithMessageHistory`实例的实现以及  
`get_session_history`的实现

```python
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
REDIS_URL='redis://127.0.0.1:6379/6'
def get_session_history(session_id:str):
    return RedisChatMessageHistory(
        session_id=session_id,
        url=REDIS_URL,
        ttl=120 #tips:设置两分钟之后过期

    )

runnable_with_redis = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key='user_input',
    history_messages_key='history'
)

#-----------------------------
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
```
由于选择的是6号数库,就得先选到6号库，而且设置了过期时间,可以看到剩下48s了，之后刷新已经没有了
![](./imgs/6.png)
![](./imgs/5.png)


## docker redis/redis-stack-server版

```shell
nikofox@MOSS:/etc/docker$ docker images
                                                                                                                                   i Info →   U  In Use
IMAGE                             ID             DISK USAGE   CONTENT SIZE   EXTRA
redis/redis-stack-server:latest   798ab84d9f26        834MB          298MB        
nikofox@MOSS:/etc/docker$ docker run -d -p 65522:6379 798ab
c002f34ce295472190b5f73ad1cd88bd6c79bf1c749914810212ede726a60cc9
nikofox@MOSS:/etc/docker$ docker images
                                                                                                                                   i Info →   U  In Use
IMAGE                             ID             DISK USAGE   CONTENT SIZE   EXTRA
redis/redis-stack-server:latest   798ab84d9f26        834MB          298MB    U   
nikofox@MOSS:/etc/docker$ docker ps
CONTAINER ID   IMAGE     COMMAND            CREATED         STATUS         PORTS                                           NAMES
c002f34ce295   798ab     "/entrypoint.sh"   9 seconds ago   Up 8 seconds   0.0.0.0:65522->6379/tcp, [::]:65522->6379/tcp   vigorous_margulis
nikofox@MOSS:/etc/docker$ 

```
就换一下url就行
```python
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
```

![](./imgs/7.png)

## 持续对话版  

```python
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
```

## 注意类型是list
![](./imgs/8.png)

## 一问一答是两条记录!
![](./imgs/9.png)