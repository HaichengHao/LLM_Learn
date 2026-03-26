# @Time    : 2026/3/24 15:18
# @Author  : hero
# @File    : 15RunnableParalell.py

#tips:Runnable是一个可以并行执行chain的一个类

from langchain_core.runnables import RunnableParallel

def fun1(a1):
    return a1+'__func1_output'
def fun2(a2):
    return a2+'__func2_output'

runnable_paralell=RunnableParallel({'key1':fun1,'key2':fun2})

res = runnable_paralell.invoke('你好',config={'max_concurrency':2})
#tips:调用后会把参数同时传递给两个函数fun1,func2,然后运行结束之后会把两个函数运行返回的结果封装为一个字典
#   传入的配置中的max_concurrency是最大并行运行数
print(res)
'''
{'key1': '你好__func1_output', 'key2': '你好__func2_output'}

可以发现其并行执行返回结果
'''