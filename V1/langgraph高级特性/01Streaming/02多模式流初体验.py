# @Time    : 2026/4/15 16:57
# @Author  : hero
# @File    : 02多模式流.py
'''
将列表作为stream_mode参数传递，以同时流式传输多种模式。
流式输出将是(mode, chunk)形式的元组，其中mode是流模式的名称，chunk是该模式所流式传输的数据。
'''


from typing import TypedDict,Annotated
from langgraph.graph import StateGraph,START,END
from langgraph.types import Send,Command

#定义state_schema
class DemoState(TypedDict):
    topic:str
    joke:str

#定义节点函数
def refine_topic(state:DemoState):
    return {
        'topic':state['topic']+' and puppys'
    }

def generate_joke(state:DemoState):
    return {
        'joke':f'this is a joke about {state['topic']}'
    }

def main():
    graph = (
        StateGraph(DemoState)
        .add_node('ref_topic',refine_topic)
        .add_node('gen_joke',generate_joke)

        .add_edge(START,'ref_topic')
        .add_edge('ref_topic','gen_joke')
        .add_edge('gen_joke',END)

        .compile()
    )

    for mode,chunk in graph.stream({'topic':'watermelon'},stream_mode=['updates','values']):
        print(f'[{mode}]:{chunk}')

if __name__ == '__main__':
    main()
#important:盯过程用values,盯结果用updates,俩都盯就混合用
'''
[values]:{'topic': 'watermelon'}
[updates]:{'ref_topic': {'topic': 'watermelon and puppys'}}
[values]:{'topic': 'watermelon and puppys'}
[updates]:{'gen_joke': {'joke': 'this is a joke about watermelon and puppys'}}
[values]:{'topic': 'watermelon and puppys', 'joke': 'this is a joke about watermelon and puppys'}

'''