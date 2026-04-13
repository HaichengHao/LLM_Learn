# @Time    : 2026/4/13 17:00
# @Author  : hero
# @File    : 23入口点.py

'''
之前已经了解过START和END的替代方式,不再赘述
'''
from langgraph.graph import StateGraph
from typing import Annotated,TypedDict

class DemoState(StateGraph):
    a:int

def in_node(state:DemoState):
    return {
        'a':state['a']+1
    }

def out_node(state:DemoState):
    return {
        'a':state['a']
    }

builder = StateGraph(DemoState)

builder.add_node('innode',in_node)
builder.add_node('outnode',out_node)

builder.set_entry_point('innode')
builder.add_edge(
    'innode',
    'outnode'
)
builder.set_finish_point('outnode')

app = builder.compile()

print(app.invoke({'a':3}))

print(app.get_graph().print_ascii())