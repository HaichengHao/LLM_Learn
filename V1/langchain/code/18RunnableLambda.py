# @Time    : 2026/3/24 17:07
# @Author  : hero
# @File    : 17RunnableLambda.py

from langchain_core.runnables import RunnableLambda,RunnableParallel
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('api_key')
base_url=os.getenv('base_url')

zhipu_key =os.getenv('zhipu_key')
zhipu_base_url=os.getenv('zhipu_base_url')

#tips:简单理解例子如下
'''
runnable_lambda = RunnableLambda(lambda x:x+"__lambdax")
resp = runnable_lambda.invoke(
    'hello'
)
print(resp)
# hello__lambdax
'''
# tips:接下来我们用RunnableLambda来构造后执行函数,优化16Paralell调用不同大模型的输出

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

#tips:定义一个函数，从并行输出中提取 content
def extract_contents(results:dict)->dict:
    return {
        key:msg.content for key,msg in results.items()
    }


#tips:构建chain:prompt

chain=prompt|RunnableParallel(
    {'gpt4o-mini':model1,'zpqy':model2}
)|RunnableLambda(extract_contents)

resp = chain.invoke({
    'user_instruction':'什么是L2范数'
})

print(resp)
print(chain.get_graph().print_ascii()) #tips：打印链的图像描述
