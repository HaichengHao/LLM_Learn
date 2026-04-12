# @Time    : 2026/4/10 11:33
# @Author  : hero
# @File    : 06state的reducer更新策略.py

'''
https://docs.langchain.com/oss/python/langgraph/graph-api#reducers
规约函数决定了节点产生的更新如何作用到State.State中的每个字段拥有自己独立的规约函数
如果未显式指定,则默认对所有该字段的更新都会直接覆盖旧值
规约函数有很多类型:
- 默认类型(覆盖) 默认更新，新值覆盖旧值
- 合并
- 添加


Reducer函数在LangGraph中的作用
控制状态更新方式:决定新值如何与现有的合并
处理并行更新:当多个节点同时更新同一字段时,确保数据一致性
提供灵活性:支持不同的合并策略,如覆盖、追加、想加等
增强表达力:允许开发者根据业务需求定义合并逻辑

通过使用Reducer函数，可以构建1更强大和灵活的状态管理机制，特别是在处理复杂工作流和并行执行场景时

1.default:未指定Reducer时使用覆盖更新
2.add_messages:用于消息列表的添加
3.operator.add:将元素追加到现有元素中,支持列表、字符串、数值类型的追加
4.operator.mul:用于数值相乘
5.自定义Reducer:支持用户自定义合并逻辑

'''
from langgraph.graph import StateGraph,START,END
from typing import TypedDict


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
