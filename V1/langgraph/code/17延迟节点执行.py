# @Time    : 2026/4/13 12:01
# @Author  : hero
# @File    : 17延迟节点执行.py

'''
延迟节点执行
'''

from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated,Any
import operator
import uuid

class MStateGraph(TypedDict):
    aggreate:Annotated[list,operator.add]

def a(state:MStateGraph):
    """
    启动分支
    :param state: 当前状态
    :return: 包含新结果的状态更新
    """
    print(f'Addding "A" to  {state["aggreate"]}')
    return {
        'aggreate':['A']
    }

def b(state:MStateGraph):
    print(f'Addding "B" to  {state["aggreate"]}')
    return {
        'aggreate': ['B']
    }

def b2(state:MStateGraph):
    print(f'Addding "B2" to  {state["aggreate"]}')
    return {
        'aggreate': ['B2']
    }

def c(state:MStateGraph):
    print(f'Addding "C" to  {state["aggreate"]}')
    return {
        'aggreate': ['C']
    }

def d(state:MStateGraph):
    print(f'Addding "D" to  {state["aggreate"]}')
    return {
        'aggreate': ['D']
    }

builder  = StateGraph(MStateGraph)


builder.add_node('a',a)
builder.add_node('b',b)
builder.add_node('b2',b2)
builder.add_node('c',c)
# builder.add_node('d',d,defer=True) #important:设置defer=True延迟执行
builder.add_node('d',d) #tips:尝试关掉等待会怎样


builder.add_edge(START,'a')
builder.add_edge('a','b')
builder.add_edge('a','c')
builder.add_edge('b','b2')
builder.add_edge('b2','d')
builder.add_edge('c','d')
builder.add_edge('d',END)

app = builder.compile()

res = app.invoke(
    {}
)
print(f'执行结果{res}')

print(app.get_graph().print_ascii())
# output_path = '../demoimgs/'+str(uuid.uuid4())[:8]+'.png'
# with open(output_path,'wb') as f:
#     f.write(app.get_graph().draw_mermaid_png())


'''
Addding "A" to  []
Addding "B" to  ['A']
Addding "C" to  ['A']
Addding "B2" to  ['A', 'B', 'C']
Addding "D" to  ['A', 'B', 'C', 'B2']
执行结果{'aggreate': ['A', 'B', 'C', 'B2', 'D']}
  +-----------+   
  | __start__ |   
  +-----------+   
        *         
        *         
        *         
      +---+       
      | a |       
      +---+       
     *     *      
     *      *     
    *        *    
+---+         *   
| b |         *   
+---+         *   
   *          *   
   *          *   
   *          *   
+----+     +---+  
| b2 |     | c |  
+----+     +---+  
      *    *      
      *   *       
       * *        
      +---+       
      | d |       
      +---+       
        *         
        *         
        *         
   +---------+    
   | __end__ |    
   +---------+    
None
'''


#important:如果关闭延迟等待会是这样的:

#tips:关闭延迟等待后，节点“上移",会出现多次添加的情况
'''
Addding "A" to  []
Addding "B" to  ['A']
Addding "C" to  ['A']
Addding "B2" to  ['A', 'B', 'C']
Addding "D" to  ['A', 'B', 'C']
Addding "D" to  ['A', 'B', 'C', 'B2', 'D']
执行结果{'aggreate': ['A', 'B', 'C', 'B2', 'D', 'D']}
  +-----------+   
  | __start__ |   
  +-----------+   
        *         
        *         
        *         
      +---+       
      | a |       
      +---+       
     *     *      
     *      *     
    *        *    
+---+         *   
| b |         *   
+---+         *   
   *          *   
   *          *   
   *          *   
+----+     +---+  
| b2 |     | c |  
+----+     +---+  
      *    *      
      *   *       
       * *        
      +---+       
      | d |       
      +---+       
        *         
        *         
        *         
   +---------+    
   | __end__ |    
   +---------+    
None

Process finished with exit code 0'''