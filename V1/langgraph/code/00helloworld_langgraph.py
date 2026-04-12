# @Time    : 2026/4/7 18:00
# @Author  : hero
# @File    : 00helloworld_langgraph.py

from typing import Annotated,List,Dict,TypedDict

from langgraph.graph import StateGraph,START,END
import uuid




#step 定义状态State(可选)
class HelloState(TypedDict):
    name: str
    greeting: str

#step 定义节点函数Node(它们其实就是给我们干活儿的)
def greet(helloState:HelloState)->dict:
    name=helloState['name']
    return {'greeting':f'你好 {name}'}

def add_emoji(helloState:HelloState)->dict:
    greeting=helloState['greeting']
    return {'greeting':greeting+'.......👋'}

#step 构建图graph,传入的是状态
graph=StateGraph(HelloState)


#step 给图添加节点(想象一下在白纸上画俩点)，下面的参数理解为k v键值对,k我们是可自定义的,v的话是我们定义的节点函数的名字
graph.add_node("greeting",greet)
graph.add_node("addemoji",add_emoji)

#step 构造边，想象一下两点(Node)连线(add_edge)，然后有START点和END点分别作为启止点
graph.add_edge(START,"greeting")
graph.add_edge("greeting","addemoji")
graph.add_edge("addemoji",END)


#step 编译图为一个runnable程序
app = graph.compile()
'''Compiles the StateGraph into a CompiledStateGraph object. 源码中的解释,
    compile可以将一个图编译为一个**被编译后的图对象**   
    
    其中我跟了一下源码，看到它有个祖宗类对象lass PregelProtocol(Runnable[InputT, Any], 继承Runnable了  
    所以它也是可以调用Runnable的哪些方法,譬如invoke,stream那些
'''

#step 编译结束后可以运行

result = app.invoke({'name':'nikofox'})
print(result)
print(result['greeting'])
print(app.get_graph().print_ascii())
print(app.get_graph().draw_mermaid()) #tips:打印mermid绘图码,复制下来到https://mermaid-live.nodejs.cn/粘贴进去，其实如果用的是jupyter的话会直接画出来的


#还有生成图片保存的方式
output_path = "../demoimgs/"+str(uuid.uuid4())[:8]+'.png'
with open(output_path,'wb') as f:
    f.write(app.get_graph().draw_mermaid_png(max_retries=2,retry_delay=2.0))

print(f'保存图成功,路径{output_path}')

'''
{'name': 'nikofox', 'greeting': '你好 nikofox.......👋'}
你好 nikofox.......👋
+-----------+  
| __start__ |  {'name':'nikofox'}
+-----------+  
      *        
      *        
      *        
+----------+    
| greeting |   对应greet方法,取出name,返回{'greeting':'你好 nikofox'}
+----------+   
      *        
      *        
      *        
+----------+   
| addemoji |   对应add_emoji方法,取出{'greeting':'你好nikofox'}中键'greeting'对应的值'你好nikofox',然后返回{'greeting':'你好 nikofox.......👋'}
+----------+   
      *        
      *        
      *        
 +---------+   
 | __end__ |   {'greeting':'你好 nikofox.......👋'}
 +---------+   
None
'''
