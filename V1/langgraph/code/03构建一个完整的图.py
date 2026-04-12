# @Time    : 2026/4/10 10:16
# @Author  : hero
# @File    : 03构建一个完整的图.py

from langgraph.graph import StateGraph,START,END
from typing import TypedDict


class GraphState(TypedDict):
    process_data:dict


def input_node(state:GraphState)->GraphState:
    print(f'input_node节点执行state.get("process_data")方法的结果:{state.get("process_data")}')
    return {
        'process_data':{
            'input':"input_value"
        }
    }

def process_node(state:dict)->dict:
    print(f'process_node节点执行state.get("process_data")方法的结果:{state.get("process_data")}')
    return {
        'process_data':{
            "process":"process_value9527"
        }
    }

def output_node(state:GraphState)->GraphState:
    print(f'output_node节点执行state.get("process_data")方法的结果:{state.get("process_data")}')
    return {
        "process_data":state.get("process_data")
    }


#构建状态图并指定状态
graph=StateGraph(GraphState)

#给图添加节点
graph.add_node("input_node",input_node)
graph.add_node("process_node",process_node)
graph.add_node("output_node",output_node)

#加边
graph.add_edge(START,"input_node")
graph.add_edge("input_node","process_node")
graph.add_edge("process_node","output_node")
graph.add_edge("output_node",END)


#编译图
app = graph.compile()


print(app.get_graph().print_ascii())
print(app.get_graph().draw_mermaid())

result = app.invoke(
    {
        "process_data":{
            'name':'测试数据',
            'value':123321
        }
    }
)

print(f"结果{result}")