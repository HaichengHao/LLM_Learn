# @Time    : 2026/3/26 16:39
# @Author  : hero
# @File    : 20runnable_with_fallbacks.py
from langchain_core.runnables  import RunnableBranch,RunnableLambda

def test1(x:int):
    return x+10
r1 = RunnableLambda(test1)
r2 = RunnableLambda(lambda x:int(x)+20)


#在加法计算中的后备选项,注意,传入的是runnable对象,传入的是列表形式

#tips:如果r1运行报错了就让r2接力
chain = r1.with_fallbacks([r2])

print(chain.invoke(2))


#tips:然后传入一个字符串数字来实验会不会触发with_fallbacks
print(chain.invoke('2'))
# 22 触发备用方案成功