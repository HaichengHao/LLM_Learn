# @Time    : 2026/4/10 10:45
# @Author  : hero
# @File    : 04基本的State定义.py

'''
https://docs.langchain.com/oss/python/langgraph/graph-api
状态State是一个贯穿整个工作流执行过程中的共享数据的结构,代表当前快照 <-important
State是图的记忆与血液.单一事实来源(SingleSourceofTruth)-所有数据通过State在节点间传递和更新,它是
LangGraph的核心
    -Reducer:定义状态如何被安全地、原子化地更新
状态存储了从工作流开始到结束的所有必要的信息(历史对话、检索到的文档、工具执行结果等)
在各个节点中共享，且每个节点都可以修改
状态包含两个部分

一是图的模式(Schema)
二是“规约函数”(reducer functions):后者指明如何把更新应用到状态上
'''

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