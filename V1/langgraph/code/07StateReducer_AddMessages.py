# @Time    : 2026/4/10 13:53
# @Author  : hero
# @File    : 07StateReducer_AddMessages.py

'''
这次用的不是默认更新策略而是add_messages,增加消息（消息列表专用,之前在02就用过一次）
'''

from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated


# 创建state_schema


class AddMessagesState(TypedDict):
    """
    引入的Annotated类型,它允许给类型添加额外的元数据，学fastapi那时候就学了
    messages:Annotated[list,add_messages]
    表示:
        - mesages 我的状态中有一个字段叫messages,类型是List列表类型
        - add_messages 这里add_messages是一个函数,用于修改messages列表
        每当节点返回对messages的“局部更新”时
        请用add_messages规约器(也就是reducer)把它合并到旧列表上(追加而不是覆盖)

    总结：
        节点永远return增量字典,不用手动把旧列表读出来再拼接
        add_messages在后台帮你完成追加动作:如果换成默认的规约器(reducer)消息就会被整个替换掉
    """
    messages: Annotated[list,add_messages]

def chat_node_1(state:AddMessagesState)->dict:
    return {
        'messages':[
            ('assistant','hello from node 1')
        ]
    }
def chat_node_2(state:AddMessagesState)->dict:
    return {
        'messages':[
            ('assistant','hello from node 2')
        ]
    }

def run_demo():
    print('2.add_messages Reducer(消息列表专用)演示')
    builder = StateGraph(state_schema=AddMessagesState)
    builder.add_node('n1',chat_node_1)
    builder.add_node('n2',chat_node_2)

    # builder.add_edge(START, 'n1')
    # builder.add_edge('n1', 'n2')
    # builder.add_edge('n2', END)
    #tips:我换种写法,
    builder.add_edge(START,'n1')
    builder.add_edge(START,'n2')

    builder.add_edge('n1',END)
    builder.add_edge('n2', END)


    grap = builder.compile()
    return grap

if __name__ == '__main__':
    graph = run_demo()
    print(graph.get_graph().print_ascii())
    res = graph.invoke(
        {
            'messages':[
                ('user','hi there')
            ]
        }
    )

    print(res)


'''
2.add_messages Reducer(消息列表专用)演示
+-----------+  
| __start__ |  
+-----------+  
      *        
      *        
      *        
    +----+     
    | n1 |     
    +----+     
      *        
      *        
      *        
    +----+     
    | n2 |     
    +----+     
      *        
      *        
      *        
 +---------+   
 | __end__ |   
 +---------+   
None

可以看到下面的输出,消息并未覆盖,而是进行了添加,节点1和节点2的小心都添加到messages列表中了
{'messages': [HumanMessage(content='hi there', additional_kwargs={}, 
response_metadata={}, id='a955edb8-a4a3-40bb-b33e-854683b905c0'), 
AIMessage(content='hello from node 1', additional_kwargs={}, response_metadata={},
 id='54ed2db2-d84a-4e2c-b696-a9c571913836', tool_calls=[], invalid_tool_calls=[]),
  AIMessage(content='hello from node 2', additional_kwargs={}, response_metadata={},
   id='d603f57f-9fec-4b69-9706-eefa1321dcff', tool_calls=[], invalid_tool_calls=[])]}'''



'''
2.add_messages Reducer(消息列表专用)演示
  +-----------+    
  | __start__ |    
  +-----------+    
      *     *      
     *       *     
    *         *    
+----+      +----+ 
| n1 |      | n2 | 
+----+      +----+ 
      *     *      
       *   *       
        * *        
    +---------+    
    | __end__ |    
    +---------+    
None
{'messages': [HumanMessage(content='hi there', additional_kwargs={}, response_metadata={},
 id='bcf5558a-8d17-4693-af97-f9fd767fa099'), 
 AIMessage(content='hello from node 1', additional_kwargs={}, response_metadata={}, 
 id='0fcbacbd-afb4-4348-8553-2ab1c899b4f2', tool_calls=[], invalid_tool_calls=[]),
  AIMessage(content='hello from node 2', additional_kwargs={}, response_metadata={}, 
  id='6f97d1c6-06d1-4af0-9d65-10091452be3a', tool_calls=[], invalid_tool_calls=[])]}'''