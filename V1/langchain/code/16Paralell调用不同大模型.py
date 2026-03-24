# @Time    : 2026/3/24 16:10
# @Author  : hero
# @File    : 16Paralell调用不同大模型.py

from langchain_core.runnables import RunnableParallel
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import asyncio
import os


load_dotenv()

api_key = os.getenv('api_key')
base_url=os.getenv('base_url')

zhipu_key =os.getenv('zhipu_key')
zhipu_base_url=os.getenv('zhipu_base_url')


#tips:调用俩模型
model1 = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model='gpt-4o-mini'
)

model2 = ChatOpenAI(
    api_key=zhipu_key,
    base_url=zhipu_base_url,
    model='glm-5'
)

prompt = ChatPromptTemplate(
    messages=[
        ('system','你是一个数学家'),
        ('user','{user_instruction}')
    ]
)
parser=StrOutputParser()
'''
对于用户输入的同一个问题,我们想要调用不同的大模型进行回答,用户可以对比不同大模型回答的效果
'''

chain=prompt|RunnableParallel({'gpt4o-mini':model1,'zpqy':model2})

resp = chain.invoke({'user_instruction':'什么是L2范数?如何计算'})
print(resp)

# async def main():
#     resp = await chain.invoke({'user_instruction':'什么是L2范数?如何计算'})
#     print(resp)
#
# if __name__ == '__main__':
#     asyncio.run(main())