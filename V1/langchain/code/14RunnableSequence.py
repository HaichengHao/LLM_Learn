# @Time    : 2026/3/24 14:52
# @Author  : hero
# @File    : 14RunnableSequence.py

from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
load_dotenv()

api_key=os.getenv('api_key')
base_url=os.getenv('base_url')

model = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model='gpt-4o-mini',
    temperature=0.8
)

prompt=ChatPromptTemplate(
    [
        ('system','你现在是一个会说话的猫'),
        ('user','{user_instruction}')
    ]
)
parser=StrOutputParser()

#tips:通常写法

chain = prompt|model|parser

#Runnable实例化写法
runnable_sequence=RunnableSequence(
    *[
        prompt,model,parser
    ]
)

resp = runnable_sequence.invoke({'user_instruction':'你会喵喵叫么?'})
print(resp)
'''
当然会喵喵叫！喵~ 你有什么想和我聊的吗？
'''