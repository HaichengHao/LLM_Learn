# @Time    : 2026/3/31 21:35
# @Author  : hero
# @File    : 24记忆缓存内存版.py
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.history import RunnableWithMessageHistory #tips:需要用到这个
from langchain_core.chat_history import InMemoryChatMessageHistory #tips:还有这个内存对话历史
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_community.chat_message_histories import ChatMessageHistory,SQLChatMessageHistory,RedisChatMessageHistory

import os
load_dotenv()
langsmith_key =os.getenv('lang_smith_key')
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = f'{langsmith_key}'
api_key=os.getenv('api_key')
base_url=os.getenv('base_url')

zai_key = os.getenv('zhipu_key')
zai_url = os.getenv('zhipu_base_url')



llm_gpt=ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model='gpt-4o-mini'
)
llm_zhipu=ChatOpenAI(
    api_key=zai_key,
    base_url=zai_url,
    model='glm-4'
)


prompt=ChatPromptTemplate(
    messages=[
        ('system','你现在是一个老中医，擅长食疗'),
        MessagesPlaceholder(variable_name='history'),
        ('human','{user_input}')
    ]
)

parser=StrOutputParser()
chain = prompt|llm_zhipu|parser



history = InMemoryChatMessageHistory()
#tips:创建runnablewithmessagehistory对象，返回runnable对象
runnable =RunnableWithMessageHistory(
    chain,
    get_session_history=lambda session_id: history,
    input_messages_key='user_input',
    history_messages_key='history'
)

#tips:清空历史记录

history.clear()

#配置运行时参数,设置会话id

config = RunnableConfig(configurable={'session_id':'chat_1'})
res1 = runnable.invoke(
    {'user_input':'舌苔厚白，是不是湿气重?'},config
    # config={
    #     'configurable':{'session_id':'chat_1'}
    # }
)

print(res1)


res2 = runnable.invoke(
    {'user_input':'那我这种情况吃什么可以调理一下呢?'},config
    # config={
    #     'configurable':{'session_id':'chat_1'}
    # }

)
print('--**--'*10)
print(res2)

