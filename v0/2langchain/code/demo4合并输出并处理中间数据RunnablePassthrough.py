# @Time    : 2026/3/26 14:15
# @Author  : hero
# @File    : demo4合并输出并处理中间数据.py

from langchain_core.runnables import RunnablePassthrough,RunnableLambda

#important:RunnablePassthrough:允许传递输入数据,可以保持不变或添加额外的键
# 必须输入字典数据!!!!
# 还可以过滤

r1 = RunnableLambda(lambda x:{'key1':x})
r2 = RunnableLambda(lambda x:x['key1']+10)

chain=r1|r2
print(chain.invoke(2))
#12

#quiz 那么这时候问题来了,如果想要让其输出的也是一个字典，
# 换句话说让我们自己能够控制输出的的格式,该怎么做？这时候,RunnablePassthrough的作用就来了

#important:使用assign()向原样输出中添加键值对,相当于对原始的字典再新增一个键并赋予值
chain2 = r1|RunnablePassthrough.assign(new_key=r2) #tips:new_key是自己命名的，代表输出的key
print(chain2.invoke(2))
# {'key1': 2, 'new_key': 12}
# 对比发现使用了RunnabllePassthrough之后

chain3 = r1|RunnablePassthrough()|RunnablePassthrough.assign(new_key=r2)
print(chain3.invoke(2))
# {'key1': 2, 'new_key': 12}