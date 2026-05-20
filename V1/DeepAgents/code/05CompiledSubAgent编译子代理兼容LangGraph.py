# @Time    : 2026/5/17 17:12
# @Author  : hero
# @File    : 05CompiledSubAgent编译子代理.py
from typing import TypedDict,Annotated

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from deepagents import create_deep_agent,CompiledSubAgent #tips:导入可以编译子代理的包
import asyncio
import os
from dotenv import load_dotenv, find_dotenv
import json

from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
load_dotenv()

# 极简初始化
llm = init_chat_model(
    model='glm-4',
    model_provider='openai',
    api_key=os.getenv('zhipu_key'),
    base_url=os.getenv('zhipu_base_url')
)


#定义一个LangGraph图节点

#1.定义一个State
class SubState(TypedDict):
    #important:graph图节点，想要兼容deepagents,那么必须包含一个messages属性,且reducer更新策略应该是累加结果
    messagss:Annotated[list,add_messages]
#2.定义节点函数和编译图结构
def processing_node(state:SubState):
    print(f"调用了graph的子节点,传入的参数为:{state}")
    print(f"子节点的业务逻辑...")
    return {
        'messages':[
            AIMessage(content=f"经过子节点处理后的结果!!原数据内容:{state['messagss'][-1].content}")
        ]
    }

workflow = StateGraph(SubState)

workflow.add_node('processing_node',processing_node)

workflow.set_entry_point("processing_node")
workflow.add_edge('processing_node',END)

graph = workflow.compile()


#包装成一个deepagent认识的subAgent

sub_agent1=CompiledSubAgent(
    name="sub_agent1",
    description="处理所有的业务逻辑",
    runnable=graph
)

#创建deepagent

deepagent = create_deep_agent(
    name="deepagent",
    subagents=[sub_agent1],
    system_prompt="你是一个指挥官,所有的业务动作都需要用graph_agent进行处理"
)


for chunk in deepagent.stream(
    {"messages":[{'role':'user','content':"处理一段复杂业务,并处理id=1的用户的数据是什么"}]}
):
    print(f"chunk结果:{chunk}")
