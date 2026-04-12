# @Time    : 2026/4/10 15:36
# @Author  : hero
# @File    : 09StateReducer_OperatorAdd字符串连接.py
from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
import operator


#tips:定义状态schema

class StrConcatState(TypedDict):
    text:Annotated[str,operator.add]


def add_text_1(state:StrConcatState)->dict:
    return {
        "text":'hello'
    }
def add_text_2(state:StrConcatState)->dict:
    return {
        "text":'langgraph'
    }

def main():
    graph = StateGraph(StrConcatState)
    graph.add_node('t1',add_text_1)
    graph.add_node('t2',add_text_2)
    graph.add_edge(START,"t1")
    graph.add_edge(START,"t2")
    graph.add_edge("t1",END)
    graph.add_edge("t2",END)

    app = graph.compile()
    return app

if __name__ == '__main__':
    app = main()
    res = app.invoke({'text':'nikofox,'})
    print(res)
    print(app.get_graph().print_ascii())
'''
{'text': 'nikofox,hellolanggraph'} 
  +-----------+    
  | __start__ |    
  +-----------+    
      *     *      
     *       *     
    *         *    
+----+      +----+ 
| t1 |      | t2 | 
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