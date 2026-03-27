# @Time    : 2026/3/26 14:13
# @Author  : hero
# @File    : 19RunnablePassthrough.py

'''
RunnablePassthrough 接收输入并将其原样输出。
RunnablePassthrough 是 LangChain LCEL 体系中的“无操作节点”，
用于在流水线中透传输入或保留上下文，也可以用于向输出中添加键也可以选取需要的键。
'''


from langchain_core.runnables import RunnableParallel,RunnablePassthrough,RunnableLambda

#tips:直观的看一下RunnablePassthrough"做"了什么
chain =RunnableParallel(
    origin=RunnablePassthrough(),
    word_count=lambda x:len(x)
)

res = chain.invoke('hello world')
print(res)
# {'origin': 'hello world', 'word_count': 11}
#important:可以看到,如果RunnbalePassthrough什么参都不写的话,那就原样输出




#important:使用assign()向原样输出中添加键值对,相当于对原始的字典再新增一个键并赋予值

chain2 = {
    "text1":lambda x:x+'world',
    "text2":lambda x:x+',how are u?'
}|RunnablePassthrough().assign(word_count=lambda x:len(x['text1'])+len(x['text2']))
#important：runnable的__ror__实现了将字典也转为runnable对象的方法

result = chain2.invoke('hello')
print(result)
print(chain2.get_graph().print_ascii())

'''
{'text1': 'helloworld', 'text2': 'hello,how are u?', 'word_count': 26}
 +----------------------------+      
 | Parallel<text1,text2>Input |      
 +----------------------------+      
           **        **              
         **            **            
        *                *           
 +--------+          +--------+      
 | Lambda |          | Lambda |      
 +--------+          +--------+      
           **        **              
             **    **                
               *  *                  
 +-----------------------------+     
 | Parallel<text1,text2>Output |     
 +-----------------------------+     
                *                    
                *                    
                *                    
  +---------------------------+      
  | Parallel<word_count>Input |      
  +---------------------------+      
          **         ***             
        **              *            
       *                 **          
+--------+          +-------------+  
| Lambda |          | Passthrough |  
+--------+          +-------------+  
          **         ***             
            **      *                
              *   **                 
 +----------------------------+      
 | Parallel<word_count>Output |      
 +----------------------------+      
None'''


#tips:来个更绕的

r1 = RunnableLambda(lambda x:{'key1':x})
r2 = RunnableLambda(lambda x:x['key1']+10)

chain3 = r1|RunnableParallel(foo=RunnablePassthrough(),new_key=RunnablePassthrough.assign(key2=r2))
print(chain3.invoke(2))
# {'foo': {'key1': 2}, 'new_key': {'key1': 2, 'key2': 12}}
'''
来详细分析
invoke(2)
然后到r1,r1的输出为{'key1':2}
然后并行运行，输出为{'foo':{'key1':2},'new_key':{'key1':2,'key2':12}}
'''
print(chain3.get_graph().print_ascii())

'''
                        +-------------+                         
                        | LambdaInput |    2                     
                        +-------------+                         
                               *                                
                               *                                
                               *                                
                          +--------+                            
                          | Lambda |                            
                          +--------+                            
                               *                                
                               *                                
                               *                                
                +----------------------------+                  
                | Parallel<foo,new_key>Input |                  
                +----------------------------+                  
                       ***               *****                  
                     **                       ***               
                   **                            *****          
     +---------------------+                          **        
     | Parallel<key2>Input |                           *        
     +---------------------+                           *        
          **         ***                               *        
        **              *                              *        
       *                 **                            *        
+--------+          +-------------+                    *        
| Lambda |{'key2':12}| Passthrough |{'key1':2}         *        
+--------+          +-------------+                    *        
          **         ***                               *        
            **      *                                  *        
              *   **                                   *        
    +----------------------+                     +-------------+  
    | Parallel<key2>Output |{'key1':2,'key2':12} | Passthrough |  {'key1':2}
    +----------------------+                     *+-------------+  
                       ***               *****                  
                          **          ***                       
                            **     ***                          
                +-----------------------------+                 
                | Parallel<foo,new_key>Output |         {'foo':{'key1':2},'new_key':{'key1':2,'key2':12}}        
                +-----------------------------+                 
None'''

#important:过滤,譬如只想拿到new_key对应的值
chain4=r1|RunnableParallel(foo=RunnablePassthrough(),new_key=RunnablePassthrough.assign(key2=r2)).pick('new_key')
print(chain4.invoke(2))
# {'key1': 2, 'key2': 12}


#tips:当然也可以传入一个键列表,由于这里我们本来就只有俩键,那就俩都取出看看
# chain5 = r1|RunnableParallel(foo=RunnablePassthrough(),new_key=RunnablePassthrough.assign(key2=r2)).pick(['new_key','foo'])
chain5 = chain3.pick(['new_key','foo']) #tips:或者这样写,本身就是基于chain3改的,那么我们不用写一大堆了
print(chain5.invoke(2))
# {'new_key': {'key1': 2, 'key2': 12}, 'foo': {'key1': 2}}