# @Time    : 2026/3/26 16:08
# @Author  : hero
# @File    : demo6重复多次运行某个节点.py

from langchain_core.runnables import RunnableParallel,RunnableLambda

counter=-1
def test3(x):
    global counter
    counter+=1
    print(f'执行了{counter}次')
    return x/counter

r1=RunnableLambda(test3)

chain =r1.with_retry(stop_after_attempt=2)
chain.invoke(2)