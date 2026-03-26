# @Time    : 2026/3/26 10:43
# @Author  : hero
# @File    : demo2组件.py
import time

from langchain_core.runnables import RunnableLambda,RunnableParallel
# from langchain_openai import ChatOpenAI
# from dotenv import load_dotenv
# import os
# load_dotenv()


def test1(x:int) -> int:
    return x+10

def test2(prompt:str)->str:
    for item in prompt.split(' '):
        yield item

r1 = RunnableLambda(test1)
r2 = RunnableLambda(test2)
resp = r1.invoke(2)
print(resp)

resp2 = r1.batch(
    [1,3]
)
for res  in resp2:
    print(res)


resp3 = r2.stream(' where there is the well? there is the way! ')
for res in resp3:
    print(res,end='',flush=True)
    time.sleep(0.3)