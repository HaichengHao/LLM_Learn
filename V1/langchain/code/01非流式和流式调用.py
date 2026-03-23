# @Time    : 2026/3/23 10:00
# @Author  : hero
# @File    : 01非流式调用.py
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import time

load_dotenv()

openai_api_key =os.getenv('api_key')
openai_base_url =os.getenv('base_url')


openaillm=ChatOpenAI(
    model='gpt-4o-mini',
    api_key=openai_api_key,
    base_url=openai_base_url,
    temperature=1.0
)


chat_prompt_template = ChatPromptTemplate(
    [
        ('system','你是一个动物语言学家'),
        ('user','{user_input}')
    ]
)


parser = StrOutputParser()

chain = chat_prompt_template | openaillm | parser

#tips:非流式
# res = chain.invoke(
#     {'user_input':'小猫怎么叫?'}
# )


#tips:流式
res = chain.stream(
{'user_input':'小猫怎么叫?'}
)
#important:流式返回的是生成器可迭代对象,所以可以用遍历的方式取出,但是注意生成器只能迭代一次
for r in res:
    # print(r)  #tips:打印输出的是一个个分散的,所以需要拼装
    print(r,end='',flush=True)
    time.sleep(0.15)



