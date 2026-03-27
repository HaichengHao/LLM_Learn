# @Time    : 2026/3/26 21:17
# @Author  : hero
# @File    : 22RunnableBranch可运行分支.py


from langchain_core.runnables import RunnableBranch

#tips:其实就很像case操作,或if..else..finally操作
branch=RunnableBranch(
    (lambda x:isinstance(x,str),lambda x:x.upper()),
    (lambda x:isinstance(x,int),lambda x:x+1),
    (lambda x:isinstance(x,float),lambda x:x*2),
    lambda x:'goodbye'
)

result = branch.invoke('hello')
print(result)



#tips:当调用invoke的时候会自上而下去判断，条件符合就执行,不符合就会依次判断,如果最终不符合就执行最后一条的默认
result2 = branch.invoke(None)
print(result2)

# HELLO
# goodbye