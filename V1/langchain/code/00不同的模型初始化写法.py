# @Time    : 2026/3/23 16:23
# @Author  : hero
# @File    : 00不同的模型初始化写法.py
# @Time    : 2026/3/23 15:25
# @Author  : hero
# @File    : 07提示词模板.py



import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model #tips:一种是引入init_chat_model
from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI #tips:另一种是直接从确定的模型接口引入

'''
1.了解什么是提示词模板:模块+变量值=完整的提示词
2.什么是(Langchain当中的)PromptTemplate
3.什么是ChatPromptTemplate
4.怎么去调用template


适用场景:
'''

load_dotenv()
api_key = os.getenv('api_key')
base_url = os.getenv('base_url')


model=ChatOpenAI(
    model='gpt-4o-mini',
    api_key=api_key,
    base_url=base_url,
    temperature=1.0
)
model1 = init_chat_model(
    model='gpt-4o-mini',
    api_key=api_key,
    temperature=1.0,
    base_url=base_url,
)

template=PromptTemplate(
    template='你是一个同声传译,帮助用户将{content}翻译成语言:{lang}',
    input_variables=['content','lang'],
)

parser=StrOutputParser()

chain = template|model|parser

res = chain.invoke(
    {'content':'春雨惊春青谷天','lang':'英语'}
)
print(res)
