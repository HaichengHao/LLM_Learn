# @Time    : 2026/4/12 11:06
# @Author  : hero
# @File    : 14定义一个节点.py
'''
节点是langGraph中的一个 基本处理单元，代表工作流中的一个操作步骤,
可以是一个Agent、调用大模型、工具或一个函数(说白了就是绑定一个python函数,
具体逻辑可以干任何事情)

最佳实践:
单一职责(Single Responsibility)
纯函数优先(Prefer Pure Functions)

常见模式(Common Patterns)
LLM调用,工具调用

设计模式:
单一职责:每个节点应该只负责一项职责，避免功能过于复杂
无状态设计:节点本身不应该保存状态，所有数据都通过输入状态传递
幂等性：相同的输入应该产生相同的输出，确保可重试性
可测试性:节点逻辑应该易于单元测试


内置的__START__和__END__节点是非常实用的
之后会学到graph.set_entry_point('node_name')函数设置起始节点,等价于graph.add_edges(START,'node_name')
之后会学到graph.set_finish_point('node_name')函数设置终止点,等价于graph.add_edges('node_name',END)

'''
from functools import partial

from langgraph.graph import StateGraph,START,END
from typing   import TypedDict,Annotated

from langgraph.types import RetryPolicy
from requests import RequestException


#定义状态图 state_schema
class GraphState(TypedDict):
    process_data:dict


#定义节点函数,入参为state

def input_node(state:GraphState) -> GraphState:
    print(f'input_node收到的初始值为:{state}')
    return {
        'process_data':{
            'input':'input_value'
        }
    }


#定义带参数的节点
def process_node(state:dict,param1:int,param2:str) -> dict:
    print(state,param1,param2)
    return {
        'process_data':{
            "process":"process_value"
        }
    }

#重试策略,add_node方法时可选
retry_policy=RetryPolicy(
    max_attempts=3,
    initial_interval=1,#初始间隔
    jitter=True, #添加随机性避免重试风暴
    backoff_factor=2,#避免乘数(每次重试间隔时间的增长倍数)
    retry_on=[
        RequestException,
        TimeoutError,
    ] #只重试这些异常
)


#创建图
builder=StateGraph(GraphState)
#添加节点
builder.add_node('input',input_node)

#tips:给process_node节点绑定参数
process_with_params=partial(process_node,param1=100,param2='test')

#important:添加带参数的node节点
# 之前写的都省略了,譬如.add_node('nodename','node_function'),其实等价于.add_node(node='nodename',action='node_function')
builder.add_node(node='process',action=process_with_params,retry_policy=retry_policy)


#定义节点之间的执行顺序edges
#设置节点间的依赖关系,形成执行流程图
builder.add_edge(START,'input')
builder.add_edge('input','process')
builder.add_edge('process',END)

#编译图
graph=builder.compile()


#打印图的边和节点信息
print(builder.edges)
'''
{('input', 'process'), ('process', '__end__'), ('__start__', 'input')}  注意,要倒过来看,从最后一个元组往前推
'''
print(builder.nodes)
'''
'''
#打印图的可视化显示
print(graph.get_graph().print_ascii())


#定义一个初始化状态字典,包含在键值对"x":5
initial_state={
    'state':5
}
res=graph.invoke(
    initial_state
)
print(res)
'''
+-----------+  
| __start__ |  
+-----------+  
      *        
      *        
      *        
  +-------+    
  | input |    
  +-------+    
      *        
      *        
      *        
 +---------+   
 | process |   
 +---------+   
      *        
      *        
      *        
 +---------+   
 | __end__ |   
 +---------+   
None
input_node收到的初始值为:{}
{'process_data': {'input': 'input_value'}} 100 test
{'process_data': {'process': 'process_value'}}
'''