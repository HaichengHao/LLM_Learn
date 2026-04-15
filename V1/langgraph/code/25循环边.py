# @Time    : 2026/4/13 17:48
# @Author  : hero
# @File    : 25循环边.py
'''
在创建带有循环的图时，需要一种终止执行的机制。最常见的做法是添加一条 条件边，当达到某个终止条件时，该边会路由到 END 节点。

递归限制设定了图在抛出错误之前允许执行的超级步骤数量，默认值 25，在 graph.invoke 的 config 参数中指定。
在某些应用中，我们无法保证会达到给定的终止条件。在这种情况下，我们可以设置图的递归限制。这将在经过指定数量的超级步骤后引发 GraphRecursionError 。
然后我们可以捕获并处理这个异常。
'''
import uuid
from typing import Annotated, Dict, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.errors import GraphRecursionError
from langchain_core.runnables.config import RunnableConfig
class LoopState(TypedDict):
    count: int
    result: str
    max_count: int

def node_a(state: LoopState) -> dict:
    """节点a：处理逻辑并更新计数"""
    print(f"执行节点a，当前计数: {state['count']}")
    return {
        'count': state['count'] + 1,
        'result': f"已处理{state['count']}次"
    }

def node_b(state: LoopState) -> dict:
    """节点b：辅助处理"""
    print(f"执行节点b，当前计数: {state['count']}")
    return {
        'result': f"已处理{state['count']}次 - 辅助处理"
    }

def route(state: LoopState) -> Literal["b", END]:
    """条件路由函数：决定是继续循环还是终止"""
    # 终止条件：当计数达到最大值时终止
    if state['count'] >= state['max_count']:
        print(f"满足终止条件，计数 {state['count']} >= {state['max_count']}，返回END")
        return END
    else:
        print(f"未满足终止条件，计数 {state['count']} < {state['max_count']}，返回b")
        return "b"

# 创建图
builder = StateGraph(LoopState)

# 添加节点
builder.add_node("a", node_a)
builder.add_node("b", node_b)

# 添加边
builder.add_edge(START, "a")
builder.add_conditional_edges("a", route)
builder.add_edge("b", "a")

# 编译图
graph = builder.compile()
print(graph.get_graph().print_ascii())
print(graph.get_graph().draw_mermaid())
store_path = '../demoimgs/'+str(uuid.uuid4())[:8]+'.png'
with open(store_path, 'wb') as f:
    f.write(graph.get_graph().draw_mermaid_png())
# 执行图
print("=== 开始执行工作流 ===")
try:
    result = graph.invoke(
        input={
            'count': 0,
            'result': '',
            'max_count': 3
        },
        # config={
        #     'recursion_limit': 6  # 设置递归限制
        # }
        #换一种规范写法
        config=RunnableConfig(    #important:别忘记了之前runnable对象做一系列方法如invoke,ainvoke,stream,astream等可以传入配置
            configurable={
                'recursion_limit':6
            }
        )

    )
    print("=== 执行结果 ===")
    print(result)
except GraphRecursionError as e:
    print(f"递归错误: {e}")

'''
关于invoke时候传入的config
  跟源码跟到这里,传入的是RunnableConfig，所以去它源码看了一下这个参数,这是循环调用限制
  recursion_limit: int
    """Maximum number of times a call can recurse.

    If not provided, defaults to `25`.
    """
    '''