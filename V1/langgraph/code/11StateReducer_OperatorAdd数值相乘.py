# @Time    : 2026/4/10 16:30
# @Author  : hero
# @File    : 11StateReducer_OperatorAdd数值相乘.py
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


'''
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
"""

