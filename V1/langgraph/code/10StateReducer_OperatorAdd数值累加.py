# @Time    : 2026/4/10 15:52
# @Author  : hero
# @File    : 10StateReducer_OperatorAdd数值累加.py

from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
import operator


#创建状态schema

class NumAddState(TypedDict):
    count:Annotated[int,operator.add]


def addnum_1(state:NumAddState):
    return {
        'count':2
    }

def addnum_2(state:NumAddState):
    return {
        'count':3
    }


def main():
    builder = StateGraph(NumAddState)
    builder.add_node('a1',addnum_1)
    builder.add_node('a2',addnum_2)

    builder.add_edge(START,'a1')
    builder.add_edge(START,'a2')

    builder.add_edge('a1',END)
    builder.add_edge('a2',END)

    graph = builder.compile()

    return graph


if __name__ == '__main__':
    graph = main()
    res = graph.invoke({'count':1})
    print(res)
    print(graph.get_graph().print_ascii())

'''
{'count': 6} 确实实现了累加1+2+3
  +-----------+    
  | __start__ |    
  +-----------+    
      *     *      
     *       *     
    *         *    
+----+      +----+ 
| a1 |      | a2 | 
+----+      +----+ 
      *     *      
       *   *       
        * *        
    +---------+    
    | __end__ |    
    +---------+    
None

'''