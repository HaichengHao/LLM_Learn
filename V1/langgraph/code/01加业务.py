# @Time    : 2026/4/9 16:03
# @Author  : hero
# @File    : 01加业务.py
from langgraph.graph import START,END,StateGraph
from langgraph.constants import START,END


'''
构建一个加减法图工作流'''


#tips:这次不做State


#important:注意,这次我没写初始状态类，但是需要遵循一个规定，那么就是初始状态接收的是字典，且节点函数集成初始状态，也就是节点函数也要求传入字典
# 那么在传入的时候就要传入字典!!!!
def addition(state):
    print(f'加法节点收到的初始值{state}')
    return {
        "x":state['x']+1
    }

def subtraction(state):
    print(f'减法节点收到的初始值{state}')
    return {
        "x":state['x']-1
    }


#tips:构建图
graph=StateGraph(dict)


#向图中添加节点
graph.add_node('addition',addition)
graph.add_node('subtraction',subtraction)


#给图加边
graph.add_edge(START,'addition')
graph.add_edge('addition','subtraction')
graph.add_edge('subtraction',END)

#tips:打印出边和节点的情况
print(graph.edges)
print()
print(graph.nodes)

#编译图为一个runnable程序
app=graph.compile()


print(app.get_graph().print_ascii())

#tips:调用invoke方法,注意,invoke只接收状态字典为核心参数,定义一个初始状态字典

initial_state={'x':5}

#调用graph对象的invoke方法,传入初始状态,执行图计算流程
res = app.invoke(initial_state)
print(res)



'''
 +-----------+   
 | __start__ |   
 +-----------+   
        *        
        *        
        *        
  +----------+   
  | addition |   
  +----------+   
        *        
        *        
        *        
+-------------+  
| subtraction |  
+-------------+  
        *        
        *        
        *        
  +---------+    
  | __end__ |    
  +---------+    
None
加法节点收到的初始值{'x': 5}
减法节点收到的初始值{'x': 6}
{'x': 5}'''
