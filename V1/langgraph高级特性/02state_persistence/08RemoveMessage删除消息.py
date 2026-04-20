# @Time    : 2026/4/19 21:43
# @Author  : hero
# @File    : 08RemoveMessage删除消息.py

"""
LangGraph 消息删除演示

该演示展示了如何使用 RemoveMessage 从图状态中删除消息。
当状态的 key 带有 add_messages 这个 reducer 时（例如 MessagesState），RemoveMessage 可以正常工作。
"""
import os
from dotenv import load_dotenv
from typing import Annotated
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    RemoveMessage, #important:主要的就是用这个
    BaseMessage
)
from langchain_core.messages.utils import count_tokens_approximately
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, MessagesState,END
from langgraph.checkpoint.memory import InMemorySaver
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
load_dotenv()


# 定义状态类型
class CustomMessagesState(TypedDict):
    messages: Annotated[list,add_messages]

model = init_chat_model(
    "glm-4",
    model_provider="openai",
    api_key=os.getenv('zhipu_key'),
    base_url = os.getenv('zhipu_base_url'),
    temperature=0.7
)

def call_llm(state: MessagesState):
    print("\\n执行节点: call_model")
    print(f"当前消息数量: {len(state['messages'])}")

    # 显示所有消息
    for i, msg in enumerate(state["messages"]):
        print(f"  消息 {i + 1}: {type(msg).__name__} - {msg.content[:50]}{'...' if len(msg.content) > 50 else ''}")
    response = model.invoke(state["messages"])
    print(f"生成的回复：{response.content}")
    return {"messages": state["messages"]}

def delete_node(state: MessagesState):
    print("\\n执行节点: delete_messages")
    messages = state["messages"]
    print(f"删除前消息数量: {len(messages)}")

    if len(messages) > 2:
        # 删除最早的两条消息
        to_remove = [RemoveMessage(id=m.id) for m in messages[:2]]  #important：自己设定的,大于两条就开始删,to_remove将传给大模型
        #tips:譬如现在已经有三条消息了,然后进入到if条件中去
        # 然后to_remove就是这样的存在to_remove=[RemoveMessage(id=msg1id),RemoveMessage(id=msg2id)]
        # 然后下面将这个列表返回给大模型,大模型拿到提示消息发现是RemoveMessage(),那么它就会去删除
        print(f"将删除 {len(to_remove)} 条消息")
        # 显示要删除的消息
        for i, msg in enumerate(messages[:2]):
            print(
                f"  删除消息 {i + 1}: {type(msg).__name__} - {msg.content[:50]}{'...' if len(msg.content) > 50 else ''}")
        return {"messages": to_remove}
    else:
        print("消息数量不足，无需删除")
        return {}

builder = StateGraph(MessagesState)

builder.add_node("call_llm",call_llm),
builder.add_node("delete",delete_node),
builder.add_edge(START,"call_llm")
builder.add_edge("call_llm","delete")
builder.add_edge("delete",END)
checkpointer = InMemorySaver()
# 编译图
app = builder.compile(checkpointer=checkpointer)

# 配置线程ID
config = {"configurable": {"thread_id": "1"}}

# 第一次调用 - 问候
print("1. 第一次调用 - 问候:")
for event in app.stream(
        {"messages": [HumanMessage(content="hi! I'm bob")]},
        config,
        stream_mode="values"
):
    print(f"当前状态中的消息数量: {len(event['messages'])}")
    if event["messages"]:
        last_message = event["messages"][-1]
        print(f"最新消息: {type(last_message).__name__} - {last_message.content}")

print("\\n" + "=" * 50 + "\\n")

# 第二次调用 - 询问名字
print("2. 第二次调用 - 询问名字:")
for event in app.stream(
        {"messages": [HumanMessage(content="what's my name?")]},
        config,
        stream_mode="values"
):
    print(f"当前状态中的消息数量: {len(event['messages'])}")
    if event["messages"]:
        last_message = event["messages"][-1]
        print(f"最新消息: {type(last_message).__name__} - {last_message.content}")

print("\\n" + "=" * 50 + "\\n")

# 第三次调用 - 请求写诗
print("3. 第三次调用 - 请求写诗:")
for event in app.stream(
        {"messages": [HumanMessage(content="write a short poem about cats")]},
        config,
        stream_mode="values"
):
    print(f"当前状态中的消息数量: {len(event['messages'])}")
    if event["messages"]:
        last_message = event["messages"][-1]
        print(f"最新消息: {type(last_message).__name__} - {last_message.content}")

print("\\n" + "=" * 50 + "\\n")

# 第四次调用 - 请求写诗（关于狗）
print("4. 第四次调用 - 请求写诗（关于狗）:")
for event in app.stream(
        {"messages": [HumanMessage(content="now do the same but for dogs")]},
        config,
        stream_mode="values"
):
    print(f"当前状态中的消息数量: {len(event['messages'])}")
    if event["messages"]:
        last_message = event["messages"][-1]
        print(f"最新消息: {type(last_message).__name__} - {last_message.content}")

print("\\n=== 演示完成 ===")

'''
1. 第一次调用 - 问候:
当前状态中的消息数量: 1
最新消息: HumanMessage - hi! I'm bob
\n执行节点: call_model
当前消息数量: 1
  消息 1: HumanMessage - hi! I'm bob
生成的回复：Hello Bob! It's nice to meet you. How can I help you today?
当前状态中的消息数量: 1
最新消息: HumanMessage - hi! I'm bob
\n执行节点: delete_messages
删除前消息数量: 1
消息数量不足，无需删除
\n==================================================\n
2. 第二次调用 - 询问名字:
当前状态中的消息数量: 2
最新消息: HumanMessage - what's my name?
\n执行节点: call_model
当前消息数量: 2
  消息 1: HumanMessage - hi! I'm bob
  消息 2: HumanMessage - what's my name?
生成的回复：Hi Bob! Your name is Bob.
当前状态中的消息数量: 2
最新消息: HumanMessage - what's my name?
\n执行节点: delete_messages
删除前消息数量: 2
消息数量不足，无需删除
\n==================================================\n
3. 第三次调用 - 请求写诗:
当前状态中的消息数量: 3
最新消息: HumanMessage - write a short poem about cats
\n执行节点: call_model
当前消息数量: 3
  消息 1: HumanMessage - hi! I'm bob
  消息 2: HumanMessage - what's my name?
  消息 3: HumanMessage - write a short poem about cats
生成的回复：A velvet paw, a silent tread,
A purring motor, softly fed.
They own the sunbeam, own the chair,
And cast a judgmental, knowing stare.

A leap, a pounce, a playful bound,
The quiet king of all they've found.
With eyes that gleam, a subtle grace,
They rule the house at their own pace.
当前状态中的消息数量: 3
最新消息: HumanMessage - write a short poem about cats
\n执行节点: delete_messages
删除前消息数量: 3
将删除 2 条消息
  删除消息 1: HumanMessage - hi! I'm bob
  删除消息 2: HumanMessage - what's my name?
当前状态中的消息数量: 1
最新消息: HumanMessage - write a short poem about cats
\n==================================================\n
4. 第四次调用 - 请求写诗（关于狗）:
当前状态中的消息数量: 2
最新消息: HumanMessage - now do the same but for dogs
\n执行节点: call_model
当前消息数量: 2
  消息 1: HumanMessage - write a short poem about cats
  消息 2: HumanMessage - now do the same but for dogs
生成的回复：A happy bark, a wagging tail,
A joyful, furry, gale.
A friend who waits by the door,
And asks for nothing more.
当前状态中的消息数量: 2
最新消息: HumanMessage - now do the same but for dogs
\n执行节点: delete_messages
删除前消息数量: 2
消息数量不足，无需删除
\n=== 演示完成 ==='''