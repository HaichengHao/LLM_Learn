# @Time    : 2026/4/10 22:13
# @Author  : hero
# @File    : 13state小案例.py


from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
import operator

#定义state_schema
class ChatState(TypedDict):
    messages: Annotated[list, add_messages]  # 消息历史
    tags: Annotated[List[str], operator.add]  # 标签列表
    score: Annotated[float, operator.add]     # 累计分数


#定义节点函数
def process_user_message(state: ChatState) -> dict:
    user_message = state["messages"][-1]  # 获取最新消息
    # 修复：正确访问消息内容
    return {
        "messages": [("assistant", f"Echo: {user_message.content}")],
        "tags": ["processed"],
        "score": 1.0
    }

def add_sentiment_tag(state: ChatState) -> dict:
    return {
        "tags": ["positive"],
        "score": 0.5
    }

# 构建图
builder = StateGraph(ChatState)

#添加节点
builder.add_node("process", process_user_message)
builder.add_node("sentiment", add_sentiment_tag)

#添加边条
builder.add_edge(START, "process")
builder.add_edge(START, "sentiment")
builder.add_edge("process", END)
builder.add_edge("sentiment", END)

graph = builder.compile()
print(graph.get_graph().print_ascii())
# 使用示例 -使用正确的消息格式
result = graph.invoke({
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "tags": ["greeting"],
    "score": 0.0
})

print(result)
'''
/home/nikofox/.local/bin/uv run /home/nikofox/LLMlearn/.venv/bin/python /home/nikofox/LLMlearn/V1/langgraph/code/13state小案例.py 
          +-----------+             
          | __start__ |             
          +-----------+             
          ***         ***           
         *               *          
       **                 **        
+---------+           +-----------+ 
| process |           | sentiment | 
+---------+           +-----------+ 
          ***         ***           
             *       *              
              **   **               
            +---------+             
            | __end__ |             
            +---------+             
None
{'messages': [HumanMessage(content='Hello, how are you?', additional_kwargs={}, response_metadata={}, id='f6f15ef2-724f-47fc-a1b7-de3cada7ee6f'), AIMessage(content='Echo: Hello, how are you?', additional_kwargs={}, response_metadata={}, id='97979700-80bc-49c7-bc55-bd1f808925ee', tool_calls=[], invalid_tool_calls=[])], 'tags': ['greeting', 'processed', 'positive'], 'score': 1.5}

Process finished with exit code 0
'''