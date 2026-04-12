# @Time    : 2026/4/10 10:06
# @Author  : hero
# @File    : 01_state_schema.py

from langgraph.graph import StateGraph,START,END
from typing import TypedDict


#定义输入和输出状态

class InputState(TypedDict):
    question:str

class OutputState(TypedDict):
    answer:str


#定义主状态
class OverallSchema(InputState,OutputState):
    pass



#定义节点函数
def answer_node(state:InputState):
    """
    处理输入并生成答案的节点

    :param state: 输入状态
    :return: 包含答案的字典
    """
    print(f'执行了answer_node')
    print(f'输入了{state}')


    answer='Bye' if 'bye' in state['question'].lower() else "Hi"
    result = {
        'answer':answer,
        'question':state['question'],
    }
    print(result)
    return result



#定义整体状态