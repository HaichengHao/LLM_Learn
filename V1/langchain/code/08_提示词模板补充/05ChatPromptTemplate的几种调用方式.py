# @Time    : 2026/3/25 10:18
# @Author  : hero
# @File    : 05ChatPromptTemplate的几种调用方式.py

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai  import ChatOpenAI,OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser,JsonOutputParser
from langchain_core.runnables import RunnableLambda,RunnableParallel
from dotenv import load_dotenv
import os
load_dotenv()

zai_key = os.getenv('zhipu_key')
zai_base_url = os.getenv('zhipu_base_url')

model=ChatOpenAI( #tips:OpenAI()补全形式已经过时
    api_key=zai_key,
    base_url=zai_base_url,
    model='glm-4'
)


#
prompt_template = ChatPromptTemplate(
    messages=[
        ('system','你叫{uname}'),
        ('human','你好，我的问题是{instruction}'),
        ('ai','我是你的个人助手,我将尽我所能回答问题')
    ]
)

#theway 1传入的是参数对应的值,返回的是字符串
str1 = prompt_template.format(uname='小言',instruction='土星有几个卫星')
print(type(str1))
print(str1)
'''
<class 'str'>
System: 你叫小言
Human: 你好，我的问题是土星有几个卫星
'''
str2 = prompt_template.invoke({'uname':'小白','instruction':'木星的构成'})
print(str2)
print(type(str2))
'''
messages=[
SystemMessage(content='你叫小白', additional_kwargs={}, response_metadata={}), 
HumanMessage(content='你好，我的问题是木星的构成', additional_kwargs={}, response_metadata={})
]
<class 'langchain_core.prompt_values.ChatPromptValue'>
'''