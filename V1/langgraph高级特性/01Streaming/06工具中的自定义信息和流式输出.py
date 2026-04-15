# @Time    : 2026/4/15 22:08
# @Author  : hero
# @File    : 06工具中的自定义信息和流式输出.py

from typing import TypedDict

from langchain.tools import tool
from langgraph.config import get_stream_writer
from langgraph.constants import START, END
from langgraph.graph import StateGraph


@tool  #important:回忆一下,tool装饰的函数返回的也是一个runnable对象！！
def query_database(query: str) -> str:
    """查询数据库工具"""
    # 访问流写入器以发送自定义数据
    writer = get_stream_writer()

    # 发送自定义数据（例如，进度更新）
    writer({"data": "开始查询数据库", "type": "info"})
    writer({"data": "Retrieved 0/100 records", "type": "progress"})

    # 模拟执行查询
    # 发送更多自定义数据
    writer({"data": "Retrieved 50/100 records", "type": "progress"})
    writer({"data": "Retrieved 100/100 records", "type": "progress"})
    writer({"data": "查询完成", "type": "info"})

    return f"查询'{query}'的结果: 找到25条匹配记录"

class GraphState(TypedDict):
    query: str
    result: str

def create_graph_with_tool():
    """创建使用工具的图"""
    def tool_node(state:GraphState):
        """工具节点"""
        result =query_database.invoke(state["query"])
        return {"result":result}

    builder = StateGraph(GraphState)
    builder.add_node("tool",tool_node)
    builder.add_edge(START,"tool")
    builder.add_edge("tool",END)

    return builder.compile()

graph = create_graph_with_tool()
input = {"query":"产品信息","result":""}
for mode,chunks in graph.stream(input,stream_mode=["updates","custom"]):
    if mode == "custom":
        print(f"这是自定义数据 {chunks}")
    if mode == "updates":
        print(f"这是更新的状态信息 {chunks}")
'''
这是自定义数据 {'data': '开始查询数据库', 'type': 'info'}
这是自定义数据 {'data': 'Retrieved 0/100 records', 'type': 'progress'}
这是自定义数据 {'data': 'Retrieved 50/100 records', 'type': 'progress'}
这是自定义数据 {'data': 'Retrieved 100/100 records', 'type': 'progress'}
这是自定义数据 {'data': '查询完成', 'type': 'info'}
这是更新的状态信息 {'tool': {'result': "查询'产品信息'的结果: 找到25条匹配记录"}}
'''