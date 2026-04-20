# @Time    : 2026/4/19 20:37
# @Author  : hero
# @File    : 07修剪消息.py


"""
大多数大语言模型都有一个最大支持的上下文窗口（以token为单位）。
决定何时截断消息的一种方法是计算消息历史中的token数量，并在其接近该限制时进行截断。
如果您使用LangChain，可以使用修剪消息工具，并指定要从列表中保留的token数量，
以及用于处理边界的strategy（例如，保留最后的max_tokens）。 要修剪消息历史，请使用trim_messages函数
"""
"""


LangGraph 消息修剪演示 

展示了如何使用 trim_messages 函数来管理消息历史，
确保消息历史不会超过模型的最大上下文窗口限制。
如果环境中配置了API密钥，将使用glm-4大模型；否则使用模拟响应。
"""

import os
from dotenv import load_dotenv
from typing import List
from langchain_core.messages import HumanMessage, AIMessage

# important:注意一定要导入包

from langchain_core.messages.utils import (
  trim_messages, 
  count_tokens_approximately 
)
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

load_dotenv()

# ================初始化模型===============
model = None
try:
  # 尝试初始大模型
  api_key = os.getenv('zhipu_key')
  model = init_chat_model(
    "glm-4",
    model_provider="openai", # 使用openai提供者，但配置为智谱平台
    api_key=api_key,
    base_url=os.getenv('zhipu_base_url'),
    temperature=0.7
  )
  print("成功初始化智谱平台的通义大模型")
except Exception as e:
  print(f"初始化模型失败: {e}")
  print("将使用模拟响应模式")
#=========================================


#=========定义模型调用节点函数===================

def call_model(state: MessagesState): #tips:这次我们不用自定义状态,而是传入默认的message状态
  """
  调用模型的节点函数
  
  Args:
    state: 当前状态，包含消息历史
    
  Returns:
    dict: 更新后的状态
  """
  print("\\n执行节点: call_model")
  
  # 显示原始消息数量
  print(f"原始消息数量: {len(state['messages'])}")
  
  # important:修剪消息历史，保留最后的128个token
  messages = trim_messages(  #tips:trim_messages将返回一个list[BaseMessage],所以我们invoke的时候就可以传入
    state["messages"],
    strategy="last",
    token_counter=count_tokens_approximately,
    max_tokens=128,
    start_on="human",   #tips:裁减的起始位置,从human开始,因为要让llm知道刚才人说了什么
    end_on=("human", "tool"), #tips:裁减的结束位置,指定到human以及tool,要让llm知道结束位置在哪里,一定是[Human,Human],或者[Human,tool],这样才是一个完整的对话周期
  )
  
  # 显示修剪后的消息数量
  print(f"修剪后消息数量: {len(messages)}")
  
  # 如果有模型则调用，否则使用模拟响应
  if model:
    try:
      response = model.invoke(input=messages)
      print(f"生成的回复: {response.content}")
      return {"messages": [response]}
    except Exception as e:
      print(f"调用模型出错: {e}")
      # 出错时使用模拟响应
      pass

def main():
  """主函数 - 演示消息修剪功能"""
  print("=== LangGraph 消息修剪演示 (基于参考资料) ===\\n")
  
  # 创建检查点保存器
  checkpointer = InMemorySaver()
  # conn = sqlite3.connect(database='./demo_trim.db', check_same_thread=False)
  # checkpointer_sqlite = SqliteSaver(conn=conn)

  
  # 构建图
  builder = StateGraph(MessagesState)
  builder.add_node(call_model)
  builder.add_edge(START, "call_model")
  
  # 编译图
  graph = builder.compile(checkpointer=checkpointer)
  
  # 配置线程ID
  config = {"configurable": {"thread_id": "1"}}
  
  # 第一次调用 - 问候
  print("1. 第一次调用 - 问候:")
  result1 = graph.invoke({
    "messages": [HumanMessage(content="hi, my name is bob")]
  }, config)
  print(f"回复: {result1['messages'][-1].content}")
  
  # 第二次调用 - 请求写诗（关于猫）
  print("\\n2. 第二次调用 - 请求写诗（关于猫）:")
  result2 = graph.invoke({
    "messages": [HumanMessage(content="write a short poem about cats")]
  }, config)
  print(f"回复: {result2['messages'][-1].content}")
  
  # 第三次调用 - 请求写诗（关于狗）
  print("\\n3. 第三次调用 - 请求写诗（关于狗）:")
  result3 = graph.invoke({
    "messages": [HumanMessage(content="now do the same but for dogs")]
  }, config)
  print(f"回复: {result3['messages'][-1].content}")
  
  # 第四次调用 - 询问名字
  print("\\n4. 第四次调用 - 询问名字:")
  final_response = graph.invoke({
    "messages": [HumanMessage(content="what's my name?")]
  }, config)
  print(f"回复: {final_response['messages'][-1].content}")
  
  # 模拟大量消息以展示修剪效果
  print("\\n5. 模拟大量消息以展示修剪效果:")
  # 添加大量消息
  many_messages: List[HumanMessage] = []
  for i in range(20):
    many_messages.append(HumanMessage(content=f"这是第{i+1}条测试消息，内容很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长"))
  
  result5 = graph.invoke({
    "messages": many_messages + [HumanMessage(content="what's my name?")]
  }, config)
  print(f"回复: {result5['messages'][-1].content}")
  
  print("\\n=== 演示完成 ===")
  # conn.close()

if __name__ == "__main__":
  main()