# @Time    : 2026/4/9 17:41
# @Author  : hero
# @File    : 02LangGraphLLM.py
import os
from typing import TypedDict
from langchain_core.messages import HumanMessage
from langgraph.graph.message import add_messages #important:注意新来一个包
from langgraph.graph import StateGraph,START,END
from langchain_openai import ChatOpenAI
from typing import Annotated
from dotenv import load_dotenv
load_dotenv()
zai_key = os.getenv('zhipu_key')
zai_url = os.getenv('zhipu_base_url')

#===========定义状态=================
class ChatBotState(TypedDict):
    #tips:messages是一个消息列表,Annotated+add_messages表示支持自动追加消息
    messages:Annotated[list,add_messages] #important:现在暂时明白add_messages是固定写法,可以
    '''读一下源码,它就是合并列表成为一个新的列表
    Merges two lists of messages, updating existing messages by ID.
    '''
#===========定义大模型===============
llm = ChatOpenAI(
    api_key=zai_key,
    base_url=zai_url,
    model='glm-4'
)


#===========定义节点函数=============

#调用大模型,并将回复加入到State['messages']里面
def model_node(state:ChatBotState):
    reply = llm.invoke(state['messages']) #输入历史消息,调用模型
    return {
        'messages':[reply]  #tips:返回新消息，自动追加到state
    }


#===============构建图
graph = StateGraph(
    ChatBotState
)

#===============给图添加节点函数
graph.add_node("model_node",model_node)

#===============节点连线，添加边
graph.add_edge(START,"model_node")
graph.add_edge("model_node",END)


#==============编译图
app = graph.compile()

#==============启用!!!

resp = app.invoke(
    {
        'messages':'你好啊'
    }
)

#important:更详细的写法
# resp2 = app.invoke(
#     {
#         "messages":[HumanMessage(content="你好啊")]
#     }
# )

print(resp)
print(resp['messages'][-1].content) #从resp中的最messages的列表中取出最后一条,一般最后一条就是AIMessage,然后拿出其中的content
print(app.get_graph().print_ascii())

'''
/home/nikofox/.local/bin/uv run /home/nikofox/LLMlearn/.venv/bin/python /home/nikofox/LLMlearn/V1/langgraph/code/02LangGraphLLM.py 
{'messages': [HumanMessage(content='你好啊', additional_kwargs={}, response_metadata={}, id='dd715943-62d3-4767-b90b-9ca83f2a30c1'),
 AIMessage(content='你好！很高兴见到你！😊 有什么我可以帮你的吗？', 
 additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 16, 'prompt_tokens': 11,
  'total_tokens': 27, 'completion_tokens_details': None, 'prompt_tokens_details': None}, 'model_provider': 'openai',
   'model_name': 'glm-4', 'system_fingerprint': None, 'id': '20260409182202a1d572b1c331497e', 'finish_reason': 'stop', 'logprobs': None}, 
   id='lc_run--019d71c3-5ea7-7f11-962c-3a125cd5618a-0', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 11, 
   'output_tokens': 16, 'total_tokens': 27, 'input_token_details': {}, 'output_token_details': {}})]}
+-----------+  
| __start__ |  
+-----------+  
       *       
       *       
       *       
+------------+ 
| model_node | 
+------------+ 
       *       
       *       
       *       
  +---------+  
  | __end__ |  
  +---------+  
None

Process finished with exit code 0'''