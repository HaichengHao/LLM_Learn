#  State

##  基本的State定义
[langchain官网](https://docs.langchain.com/oss/python/langgraph/graph-api)
```text
状态State是一个贯穿整个工作流执行过程中的共享数据的结构,代表当前快照 <-important
State是图的记忆与血液.单一事实来源(SingleSourceofTruth)-所有数据通过State在节点间传递和更新,它是
LangGraph的核心
    -Reducer:定义状态如何被安全地、原子化地更新
状态存储了从工作流开始到结束的所有必要的信息(历史对话、检索到的文档、工具执行结果等)
在各个节点中共享，且每个节点都可以修改
状态包含两个部分

一是图的模式(Schema)
二是“规约函数”(reducer functions):后者指明如何把更新应用到状态上
```
```python
from typing import TypedDict
from langgraph.graph import StateGraph,START,END


class BaseStata(TypedDict):
    """
    基本的State定义
    """
    user_input: str
    response:str
    count: int
    process_data:dict


basicState=StateGraph(BaseStata)

basicState.add_edge(START,END)

app = basicState.compile()

#invoke()方法只接收状态字典作为核心参数
initial_state={
    "user_input":"a",
    "response":"resp",
    "count":25,
    "process_data":{
        "k1":"v1",
        "k2":"v2",
        "k3":"v3"
    }
}


result = app.invoke(initial_state)
print(result)
```

## state的schema
LangGraph 图输入输出模式和私有状态传递演示  

该演示展示了：  
**如何定义图的输入和输出模式**

```text
state_schema是图的完整内部状态，包含了所有节点可能读写的字段，必须指定，不能为空
特点:是图的“全局状态空间” 所有节点都可以访问和写入这个schema中的任何字段
```
```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict


# 定义输入状态模式
class InputState(TypedDict):
    question: str

# 定义输出状态模式
class OutputState(TypedDict):
    answer: str

# 定义整体状态模式，结合输入和输出
class OverallState(InputState, OutputState):
    pass


# 定义处理节点
def answer_node(state: InputState): #tips:传入的是输入schema格式的字典
    """
    处理输入并生成答案的节点
    Args:
        state: 输入状态
    Returns:
        dict: 包含答案的字典
    """
    print(f"执行 answer_node 节点:")
    print(f"  输入: {state}")

    # 示例答案
    answer = "再见" if "bye" in state["question"].lower() else "你好"
    result = {"answer": answer, "question": state["question"]}

    print(f"  输出: {result}")
    return result


def demo_input_output_schema():
    """演示输入输出模式"""
    print("=== 演示输入输出模式 ===")

    # 使用指定的输入和输出模式构建图
    builder = StateGraph(state_schema=OverallState, input_schema=InputState, output_schema=OutputState)
    builder.add_edge(START, "answer_node")  # 定义起始边
    builder.add_node("answer_node", answer_node)  # 添加答案节点
    builder.add_edge("answer_node", END)  # 定义结束边
    graph = builder.compile()  # 编译图

    # 使用输入调用图并打印结果
    result = graph.invoke({"question": "你好"})
    print(f"图调用结果: {result}")
    # 打印图的ascii可视化结构
    print(graph.get_graph().print_ascii())
    print()

```

## State的Reducer更新策略 
规约函数决定了节点产生的更新如何作用到State.State中的每个字段拥有自己独立的规约函数  
如果未显式指定,则默认对所有该字段的更新都会直接覆盖旧值  
规约函数有很多类型:  
- 默认类型(覆盖) 默认更新，新值覆盖旧值
- 合并
- 添加

Reducer函数在LangGraph中的作用  
- 控制状态更新方式:决定新值如何与现有的合并
- 处理并行更新:当多个节点同时更新同一字段时,确保数据一致性
- 提供灵活性:支持不同的合并策略,如覆盖、追加、想加等
- 增强表达力:允许开发者根据业务需求定义合并逻辑

**通过使用Reducer函数，可以构建1更强大和灵活的状态管理机制，特别是在处理复杂工作流和并行执行场景时**

1. default:未指定Reducer时使用覆盖更新
```python
# 1.默认reducer
# 未指定合并策略,默认覆盖，上一个节点的返回是下一个节点的输入值

class DefaltReducerState(TypedDict):
    foo:int
    bar:list[str]

def node_default_1(state:DefaltReducerState)-> dict:
    print(state['foo'])
    print(state['bar'])
    return {
        'foo':22
    }
def node_default_2(state:DefaltReducerState)-> dict:
    print()
    print(state['foo'])
    print(state['bar'])
    return {
        'bar':['bye1','bye2','bye3']
    }

def main():
    print("1.默认Reducer(覆盖更新演示)")
    builder = StateGraph(DefaltReducerState)
    builder.add_node('n1',node_default_1)
    builder.add_node('n2',node_default_2)
    builder.add_edge(START,'n1')
    builder.add_edge("n1",'n2')
    builder.add_edge("n2",END)

    app = builder.compile()

    return app

if __name__ == '__main__':
    app = main()
    print(app.get_graph().print_ascii())
    res = app.invoke(
        {
            'foo': 1,
            'bar': ['hi1', 'hi2']
        }
    )

    print(res)
    """
    1
['hi1', 'hi2']

22
['hi1', 'hi2']
{'foo': 22, 'bar': ['bye1', 'bye2', 'bye3']}
"""
```
2. add_messages:用于消息列表的添加
这里需要一个message中的add_messages方法
```python
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
```
```python
class AddMessagesState(TypedDict):
    """
    引入的Annotated类型,它允许给类型添加额外的元数据，学fastapi那时候就学了
    messages:Annotated[list,add_messages]
    表示:
        - mesages 我的状态中有一个字段叫messages,类型是List列表类型
        - add_messages 这里add_messages是一个函数,用于修改messages列表
        每当节点返回对messages的“局部更新”时
        请用add_messages规约器(也就是reducer)把它合并到旧列表上(追加而不是覆盖)

    总结：
        节点永远return增量字典,不用手动把旧列表读出来再拼接
        add_messages在后台帮你完成追加动作:如果换成默认的规约器(reducer)消息就会被整个替换掉
    """
    messages: Annotated[list,add_messages]
def chat_node_1(state:AddMessagesState)->dict:
    return {
        'messages':[
            ('assistant','hello from node 1')
        ]
    }
def chat_node_2(state:AddMessagesState)->dict:
    return {
        'messages':[
            ('assistant','hello from node 2')
        ]
    }

def run_demo():
    print('2.add_messages Reducer(消息列表专用)演示')
    builder = StateGraph(state_schema=AddMessagesState)
    builder.add_node('n1',chat_node_1)
    builder.add_node('n2',chat_node_2)

    # builder.add_edge(START, 'n1')
    # builder.add_edge('n1', 'n2')
    # builder.add_edge('n2', END)
    #tips:我换种写法,
    builder.add_edge(START,'n1')
    builder.add_edge(START,'n2')

    builder.add_edge('n1',END)
    builder.add_edge('n2', END)


    grap = builder.compile()
    return grap

if __name__ == '__main__':
    graph = run_demo()
    print(graph.get_graph().print_ascii())
    res = graph.invoke(
        {
            'messages':[
                ('user','hi there')
            ]
        }
    )

    print(res)

```
3. operator.add:将元素追加到现有元素中,支持列表、字符串、数值类型的追加

- 1. 数字追加
```python
from langgraph.graph import StateGraph,START,END
from typing import TypedDict ,Annotated
import operator

#tips:operator之前在构建ragchain的RAG/case/03 中做索引增强生成构造链的时候用过
class ListAddState(TypedDict):
    data:Annotated[list[int],operator.add] #tips:列表追加

def producer_1(state:ListAddState)->dict:
    return {
        'data':[1,2]
    }

def producer_2(state:ListAddState)->dict:
    return {
        'data':[3,4]
    }


def main():
    graph = StateGraph(ListAddState)
    graph.add_node('p1',producer_1)
    graph.add_node('p2',producer_2)

    graph.add_edge(START,'p1')
    graph.add_edge(START,'p2')
    graph.add_edge('p1',END)
    graph.add_edge('p2',END)

    APP = graph.compile()
    return APP

if __name__ == '__main__':
    APP = main()
    res = APP.invoke(
        {'data': [1, 3]}
    )

    print(res)

    print(APP.get_graph().print_ascii())

"""
{'data': [1, 3, 1, 2, 3, 4]}
"""
```
- 2. 字符串连接 
```python
# @Time    : 2026/4/10 15:36
# @Author  : hero
# @File    : 09StateReducer_OperatorAdd字符串连接.py
from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
import operator


#tips:定义状态schema

class StrConcatState(TypedDict):
    text:Annotated[str,operator.add]


def add_text_1(state:StrConcatState)->dict:
    return {
        "text":'hello'
    }
def add_text_2(state:StrConcatState)->dict:
    return {
        "text":'langgraph'
    }

def main():
    graph = StateGraph(StrConcatState)
    graph.add_node('t1',add_text_1)
    graph.add_node('t2',add_text_2)
    graph.add_edge(START,"t1")
    graph.add_edge(START,"t2")
    graph.add_edge("t1",END)
    graph.add_edge("t2",END)

    app = graph.compile()
    return app

if __name__ == '__main__':
    app = main()
    res = app.invoke({'text':'nikofox,'})
    print(res)
    print(app.get_graph().print_ascii())
'''
{'text': 'nikofox,hellolanggraph'} 
  +-----------+    
  | __start__ |    
  +-----------+    
      *     *      
     *       *     
    *         *    
+----+      +----+ 
| t1 |      | t2 | 
+----+      +----+ 
      *     *      
       *   *       
        * *        
    +---------+    
    | __end__ |    
    +---------+    
None

Process finished with exit code 0
'''
```
- 3. 数值累加
```python
from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
import operator


#创建状态schema

class NumAddState(TypedDict):
    count:Annotated[int,operator.add]


def addnum_1(state:NumAddState):
    return {
        'count':2
    }

def addnum_2(state:NumAddState):
    return {
        'count':3
    }


def main():
    builder = StateGraph(NumAddState)
    builder.add_node('a1',addnum_1)
    builder.add_node('a2',addnum_2)

    builder.add_edge(START,'a1')
    builder.add_edge(START,'a2')

    builder.add_edge('a1',END)
    builder.add_edge('a2',END)

    graph = builder.compile()

    return graph


if __name__ == '__main__':
    graph = main()
    res = graph.invoke({'count':1})
    print(res)
    print(graph.get_graph().print_ascii())

'''
{'count': 6} 确实实现了累加1+2+3
  +-----------+    
  | __start__ |    
  +-----------+    
      *     *      
     *       *     
    *         *    
+----+      +----+ 
| a1 |      | a2 | 
+----+      +----+ 
      *     *      
       *   *       
        * *        
    +---------+    
    | __end__ |    
    +---------+    
None

'''
```
4. operator.mul:用于数值相乘
```python
from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
import operator

#定义state_schema

class MultiplyState(StateGraph):
    factor:Annotated[float,operator.mul]


def multiplier(state:MultiplyState):
    return {
        'factor':2.0
    }

def multiplier2(state:MultiplyState):
    return {
        'factor':3.0
    }


def main():
    builder = StateGraph(MultiplyState)
    builder.add_node('m1',multiplier)
    builder.add_node('m2',multiplier2)
    builder.add_edge(START,'m1')
    builder.add_edge(START,'m2')
    builder.add_edge('m1',END)
    builder.add_edge('m2',END)

    app = builder.compile()
    return app

if __name__ == '__main__':
    app = main()
    res = app.invoke(
        {'factor':2.0},
    )

    print(res)
    print(app.get_graph().print_ascii())

```

```text
{'factor': 0.0} 关键错误来了,为啥是0.0？
  +-----------+    
  | __start__ |    
  +-----------+    
      *     *      
     *       *     
    *         *    
+----+      +----+ 
| m1 |      | m2 | 
+----+      +----+ 
      *     *      
       *   *       
        * *        
    +---------+    
    | __end__ |    
    +---------+    
None
'''

#important：
"""
这不是bug，是设计决策：LangGraph选择用类型默认值初始化状态字段
对于不同操作，需要不同处理：
加法：恒等元是0.0，所以operator.add可以直接用
乘法：恒等元是1.0，需要特殊处理初始的0.0
自定义reducer是标准做法：复杂的业务逻辑都应该使用自定义reducer

这是LangGraph使用中的一个常见陷阱！建议在使用乘法、除法等非加法操作时，总是使用自定义reducer来处理初始值问题

    在执行初始阶段（我们定义的第一个node前），会默认调用一次reducer（后面自定义reducer案例中进行了打印验证），
    用默认值与invoke传递的值进行计算：
    此案例中，invoke中传递了一个默认值5.0，由于会默认调用一次reducer，
    执行的计算是： 0.0（float默认值） * 5.0(invoke传递的初始值) = 0.0
    导致后续乘法结果一直都是0

    初始默认值: factor = 0.0
    invoke传入: factor = 5.0
    reducer计算: 0.0 * 5.0 = 0.0
    然后才执行你的multiplier节点...
operator.mul作为 LangGraph 归约器的执行逻辑是：
最终值 = 初始值 * 增量值1 * 增量值2 * ...
归约器会迭代节点返回的增量值并依次相乘，若直接返回单个数值（非可迭代），会被判定为「无增量」，最终按初始值 * 空处理，而乘法中「空累积」的默认结果是乘法单位元 0.0。

    解决方案： 使用自定义reducer
```
5. 自定义Reducer:支持用户自定义合并逻辑
```python
from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated


#important：自定义reducer

def CustomReducer(current:float,update:float)->float:
    '''
    自定义reducer,处理初始值，从0.0掰到1.0
    实现如果是第一次调用,current默认值为1.0
    :param current:
    :param update:
    :return:
    '''

    if current == 0.0:
        #对于乘法，恒等元应该是1.0或者return 1.0*update
        print(f'current is {current}')
        print(f'update is {update}')
        return 1.0*update
    else:
        return current*update #tips:这样就避免了首次相乘中langgraph自动将恒等元作为0.0的情况了


#定义state_schema

class MultiplyState(StateGraph):
    factor:Annotated[float,CustomReducer] #tips:这里不用reducer函数了,传我们自己的函数!


def multiplier(state:MultiplyState):
    return {
        'factor':2.0
    }

def multiplier2(state:MultiplyState):
    return {
        'factor':3.0
    }


def main():
    builder = StateGraph(MultiplyState)
    builder.add_node('m1',multiplier)
    builder.add_node('m2',multiplier2)
    builder.add_edge(START,'m1')
    builder.add_edge(START,'m2')
    builder.add_edge('m1',END)
    builder.add_edge('m2',END)

    app = builder.compile()
    return app

if __name__ == '__main__':
    app = main()
    res = app.invoke(
        {'factor':2.0},
    )

    print(res)
    print(app.get_graph().print_ascii())

'''
current is 0.0
update is 2.0
{'factor': 12.0}  成功,进行了自定义的reducer之后,将恒等元修改为了1*而不是0*，这样1*传入的update,也就是factor的值就是正常的开始做乘法了
  +-----------+    
  | __start__ |    
  +-----------+    
      *     *      
     *       *     
    *         *    
+----+      +----+ 
| m1 |      | m2 | 
+----+      +----+ 
      *     *      
       *   *       
        * *        
    +---------+    
    | __end__ |    
    +---------+    
None

Process finished with exit code 0


'''
```