# @Time    : 2026/4/15 17:42
# @Author  : hero
# @File    : 04messages模式.py
'''
设置了为messages模式之后调用astream(inputs,stream_mode="messages")返回的将会是一个
(chunk,metadata)的二元数组!!!!!!!
'''

import os
import gradio as gr
from dotenv import load_dotenv
from langgraph.graph import StateGraph,START,END
from langchain.chat_models import init_chat_model
from typing import TypedDict
#tips:回顾一下四大类Message
from langchain.messages import AIMessage,HumanMessage,SystemMessage,ToolMessage

load_dotenv()
zai_key=os.getenv('zhipu_key')
zai_url = os.getenv('zhipu_base_url')

llm = init_chat_model(
    model='glm-4',
    model_provider='openai',
    api_key=zai_key,
    base_url=zai_url,
    temperature=0.6

)


class DemoState(TypedDict):
    query:str
    answer:str

def node(state:DemoState):
    print('开始调用node节点')
    llm_result = llm.invoke(
        [('human',state['query'])]
    )
    print('llm invoke结束')

    return {
        'answer':llm_result
    }

def main():
    graph = (
        StateGraph(DemoState)
        .add_node('n1',node)
        .add_edge(START,'n1')
        .add_edge('n1',END)
        .compile()
    )

    inputs={
        'query':'帮我写一个100字以内的小笑话'
    }

    for chunk,meta_data in graph.stream(inputs,stream_mode="messages"):
        # print(f'[chunk]:{chunk},[meta_data]:{meta_data}]')
        # print(type(chunk))  #tips:<class 'langchain_core.messages.ai.AIMessageChunk'>返回的是AIMessageChunk
        print(chunk.content,end='')

if __name__ == '__main__':
    main()

''' 只截取一条看看


[chunk]:content='小明'
 additional_kwargs={} 
 response_metadata={'model_provider': 'openai'}
 id='lc_run--019d909f-76cf-7bc3-bc01-5e8d94746429' 
 tool_calls=[] 
 invalid_tool_calls=[] 
 tool_call_chunks=[],
 [meta_data]:
 {'langgraph_step': 1, 
 'langgraph_node': 'n1', 
 'langgraph_triggers': ('branch:to:n1',),
 'langgraph_path': ('__pregel_pull', 'n1'), 
 'langgraph_checkpoint_ns': 'n1:eb8e9e86-1930-c907-8d60-52553910e52b', 
 'model': 'glm-4', 'model_name': 'glm-4', 
 'stream': False, 
 'temperature': 0.6, 
 '_type': 'openai-chat', 
 'checkpoint_ns': 'n1:eb8e9e86-1930-c907-8d60-52553910e52b', 
 'ls_provider': 'openai', 
 'ls_model_name': 'glm-4', 'ls_model_type': 'chat', 
 'ls_temperature': 0.6,
  'ls_integration': 'langchain_chat_model'}]'''