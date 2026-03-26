# @Time    : 2026/3/26 11:16
# @Author  : hero
# @File    : demo3组合链.py

from langchain_core.runnables import RunnableLambda,RunnableParallel

def test1(x:int)->int:
    return x+1

r1 = RunnableLambda(test1)
r2 = RunnableLambda(lambda x:x+x)

chain = r1|r2 #串行运行的
resp = chain.invoke(1)
print(resp)
#4 ,拆解一下,r1-> 1+1作为输入传给r2,r2执行匿名函数x+x,所以就是2+2=4

chain2 = RunnableParallel(r1=r1,r2=r2)

resp=chain2.invoke(2,config={'max_concurrency':2})
print(resp)
print(chain2.get_graph().print_ascii()) #tips:打印链的图像描述,注意需要先安装包grandalf

'''
{'r1': 3, 'r2': 4}
  +----------------------+    
  | Parallel<r1,r2>Input |    
  +----------------------+    
         *        *           
       **          **         
      *              *        
+-------+         +--------+  
| test1 |         | Lambda |  
+-------+         +--------+  
         *        *           
          **    **            
            *  *              
 +-----------------------+    
 | Parallel<r1,r2>Output |    
 +-----------------------+   
 '''