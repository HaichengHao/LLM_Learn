'''
条件入口点，和刚才条件边的用法很相似，区别较大的点就在于条件入口点要求与START紧耦合，还有就是用来控制路由选择的函数不需要再作为节点添加 #important
条件入口点允许你根据自定义逻辑从不同的节点开始。你可以使用虚拟 START 节点的 add_conditional_edges 来实现此功能。
from langgraph.graph import START
graph.add_conditional_edges(START, routing_function)
你可以选择提供一个字典，将 routing_function 的输出映射到下一个节点的名称。
graph.add_conditional_edges(START, routing_function, {True: "node_b", False: "node_c"})
'''
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Annotated


# 定义状态
class DemoState(TypedDict):
    x: int

def addition1(state):
    """
    执行加法运算的节点函数
    参数:
        state (dict): 包含输入数据的状态字典，必须包含键"x"
    返回:
        dict: 返回更新后的状态字典，其中"x"的值增加1
    """
    print(f'加法节点addition1收到的初始值:{state}')
    return {"x": state["x"] + 1}

def addition2(state):
    print(f'加法节点addition2收到的初始值:{state}')
    return {"x": state["x"] + 2}

def addition3(state):
    print(f'加法节点addition3收到的初始值:{state}')
    return {"x": state["x"] + 3}

def route_by_sentiment(state: DemoState) -> str:
    # 路由逻辑...返回最终的条件
    flag = state["x"]
    if flag == 1:
        return "condition_1"
    elif flag == 2:
        return "condition_2"
    else:
        return "condition_3"

graph = StateGraph(DemoState)
graph.add_node("node1", addition1)
graph.add_node("node2", addition2)
graph.add_node("node3", addition3)

# 节点添加结束后来看看边
# 添加路由函数，参数：当前节点，路由函数，路由函数返回的条件与node的映射
graph.add_conditional_edges(
    source=START,
    path=route_by_sentiment,
    path_map={
        "condition_1": "node1",
        "condition_2": "node2",
        "condition_3": "node3"
    }
)

# 所有处理节点都连接到END
graph.add_edge("node1", END)
graph.add_edge("node2", END)
graph.add_edge("node3", END)
app = graph.compile()
# 定义一个初始状态字典，包含键值对"x": 具体数字
initial_state ={"x": 3}
# 调用graph对象的invoke方法，传入初始状态，执行图计算流程
result= app.invoke(initial_state)
print(f"最后的结果是:{result}")



# 打印图的边和节点信息
#print(graph.edges)
#print(graph.nodes)
# 打印图的ascii可视化结构
print(app.get_graph().print_ascii())
print("=================================")
print()
# 打印图的可视化结构，生成更加美观的Mermaid 代码，通过processon 编辑器查看
print(app.get_graph().draw_mermaid())
#important:其实这个案例讲的就是马上要说的条件入口点
'''
加法节点addition3收到的初始值:{'x': 3}
最后的结果是:{'x': 6}
                +-----------+                  
                | __start__ |                  {'x':3}
                +-----------+..                
             ...      .        ...             添加条件边,进入path,也就是进入route_by_sentiment进行判断
          ...         .           ...          然后拿到state[x]=3，所以前两条判断之后给到最后的else,返回condition_3,根据path_map
        ..            .              ..        确定下面走的节点是node3,然后走node3 返回{"x": state["x"] + 3},也就是{'x':6}
+-------+         +-------+         +-------+  然后走下一个END，结束
| node1 |*        | node2 |         | node3 |  
+-------+ ***     +-------+       **+-------+  
             ***      *        ***             
                ***   *     ***                
                   ** *   **                   
                 +---------+                   
                 | __end__ |                   
                 +---------+                   
None
================================='''