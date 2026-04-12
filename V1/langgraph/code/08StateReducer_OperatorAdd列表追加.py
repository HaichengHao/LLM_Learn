# @Time    : 2026/4/10 15:08
# @Author  : hero
# @File    : 08StateReducer_OperatorAdd列表追加.py
from langgraph.graph import StateGraph,START,END
from typing import TypedDict ,Annotated
import operator

#tips:operator之前在构建ragchain的RAG/case/03 中做索引增强生成构造链的时候用过

#构造state_schema

class ListAddState(TypedDict):
    data:Annotated[list[int],operator.add] #tips:列表追加

def producer_1(state:ListAddState)->dict:
    return {
        'data':[1,2]
    }

def producer_2(state:ListAddState)->dict:
    return {
        'data':[3,4]
    }


def main():
    graph = StateGraph(ListAddState)
    graph.add_node('p1',producer_1)
    graph.add_node('p2',producer_2)

    graph.add_edge(START,'p1')
    graph.add_edge(START,'p2')
    graph.add_edge('p1',END)
    graph.add_edge('p2',END)

    APP = graph.compile()
    return APP

if __name__ == '__main__':
    APP = main()
    res = APP.invoke(
        {'data': [1, 3]}
    )

    print(res)

    print(APP.get_graph().print_ascii())


'''
/home/nikofox/.local/bin/uv run /home/nikofox/LLMlearn/.venv/bin/python /home/nikofox/LLMlearn/V1/langgraph/code/08StateReducer_OperatorAdd列表追加.py 
{'data': [1, 3, 1, 2, 3, 4]}
  +-----------+    
  | __start__ |    
  +-----------+    
      *     *      
     *       *     
    *         *    
+----+      +----+ 
| p1 |      | p2 | 
+----+      +----+ 
      *     *      
       *   *       
        * *        
    +---------+    
    | __end__ |    
    +---------+    
None

Process finished with exit code 0
'''
