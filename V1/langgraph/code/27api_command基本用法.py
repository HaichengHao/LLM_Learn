# @Time    : 2026/4/14 15:03
# @Author  : hero
# @File    : 27api_command基本用法.py

#important：如智能点餐,先定位,然后决策代理拿到位置信息后给订餐软件的定位api,之后再回到决策代理,用户决定要吃什么之后再匹配下一个节点功能

#tips:update的更新策略和字典一样的,就是不传则不动,传新则更新
'''
Command(
      update={
        "messages": [("system", "路由到数学代理")],
        "current_agent": "math_agent"
      },
      goto="math_agent"
    )
将控制流（边）和状态更新（节点）结合起来可能会很有用。例如，你可能希望在同一个节点中既执行状态更新，
又决定下一步前往哪个节点。LangGraph 提供了一种实现方式，即从节点函数返回一个 Command 对象。

借助Command，可以实现动态控制流行为（与条件边相同）：根据消息内容动态决定执行路径，并在节点中同时更新状态和控制流程。

command只能路由到一个节点,并且可以更新当前的状态,而send可以万箭齐发
'''


from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

# 定义状态
class AgentState(TypedDict):
  messages: Annotated[list, lambda x, y: x + y] #tips:这里做了一个列表合并操作，就是如果有新列表传入的话不进行覆盖，而是合并列表成为新列表
  current_agent: str
  task_completed: bool

# 节点函数：决策代理
def decision_agent(state: AgentState) -> Command[AgentState]:
  """决策代理节点，根据消息内容决定下一步操作"""
  print("执行节点: decision_agent")
  
  # 检查最新的消息
  last_message = state["messages"][-1] if state["messages"] else ""
  print(f"最新消息: {last_message}")
  
  # 根据消息内容决定下一步
  if "数学" in last_message:
    # 更新状态并跳转到数学代理
    return Command(
      update={
        "messages": [("system", "路由到数学代理")],
        "current_agent": "math_agent"
      },
      goto="math_agent"
    )
  elif "翻译" in last_message:
    # 更新状态并跳转到翻译代理
    return Command(
      update={
        "messages": [("system", "路由到翻译代理")],
        "current_agent": "translation_agent"
      },
      goto="translation_agent"
    )
  else:
    # 任务完成
    return Command(
      update={
        "messages": [("system", "任务完成")],
        "task_completed": True
      },
      goto=END
    )

# 节点函数：数学代理
def math_agent(state: AgentState) -> Command[AgentState]:
  """数学代理节点"""
  print("执行节点: math_agent")
  
  # 执行数学计算任务
  result = "2 + 2 = 4"
  print(f"计算结果: {result}")
  
  # 更新状态并返回决策代理
  return Command(
    update={
      "messages": [("assistant", f"数学计算结果: {result}")],
      "current_agent": "decision_agent"
    },
    goto="decision_agent"
  )

# 节点函数：翻译代理
def translation_agent(state: AgentState) -> Command[AgentState]:
  """翻译代理节点"""
  print("执行节点: translation_agent")
  
  # 执行翻译任务
  translation = "Hello -> 你好"
  print(f"翻译结果: {translation}")
  
  # 更新状态并返回决策代理
  return Command(
    update={
      "messages": [("assistant", f"翻译结果: {translation}")],
      "current_agent": "decision_agent"
    },
    goto="decision_agent"
  )

def main():
  """演示Command基础用法"""
  print("=== Command 基础演示 ===\n")
  
  # 创建图
  builder = StateGraph(AgentState)
  
  # 添加节点
  builder.add_node("decision_agent", decision_agent)
  builder.add_node("math_agent", math_agent)
  builder.add_node("translation_agent", translation_agent)
  
  # 设置入口点
  builder.add_edge(START, "decision_agent")

  # builder.add_edge("math_agent",'decision_agent')
  # builder.add_edge("translation_agent", 'decision_agent')
  # builder.add_edge("decision_agent", 'decision_agent')
  # builder.add_edge('decision_agent', END)


  # 编译图
  graph = builder.compile()
  print(graph.get_graph().print_ascii())
  with open('../demoimgs/command_graph.png', 'wb') as f:
      f.write(graph.get_graph().draw_mermaid_png())
      print('图片保存成功')
  # 执行图 - 测试数学任务
  print("测试1: 数学任务")
  initial_state = {
    "messages": [("user", "我需要计算数学题")],
    "current_agent": "user",
    "task_completed": False
  }
  print("初始状态:", initial_state)
  result = graph.invoke(initial_state)
  print("最终状态:", result)
  print("\n" + "="*50 + "\n")
  
  # 执行图 - 测试翻译任务
  print("测试2: 翻译任务")
  initial_state = {
    "messages": [("user", "我需要翻译文本")],
    "current_agent": "user",
    "task_completed": False
  }
  print("初始状态:", initial_state)
  result = graph.invoke(initial_state)
  print("最终状态:", result)
  print("\n" + "="*50 + "\n")
  
  # 执行图 - 测试完成任务
  print("测试3: 完成任务")
  initial_state = {
    "messages": [("user", "你好")],
    "current_agent": "user",
    "task_completed": False
  }
  print("初始状态:", initial_state)
  result = graph.invoke(initial_state)
  print("最终状态:", result)

if __name__ == "__main__":
  main()

'''
=== Command 基础演示 ===

测试1: 数学任务
初始状态: {'messages': [('user', '我需要计算数学题')], 'current_agent': 'user', 'task_completed': False}
执行节点: decision_agent
最新消息: ('user', '我需要计算数学题')
最终状态: {'messages': [('user', '我需要计算数学题'), ('system', '任务完成')], 'current_agent': 'user', 'task_completed': True}

==================================================

测试2: 翻译任务
初始状态: {'messages': [('user', '我需要翻译文本')], 'current_agent': 'user', 'task_completed': False}
执行节点: decision_agent
最新消息: ('user', '我需要翻译文本')
最终状态: {'messages': [('user', '我需要翻译文本'), ('system', '任务完成')], 'current_agent': 'user', 'task_completed': True}

==================================================

测试3: 完成任务
初始状态: {'messages': [('user', '你好')], 'current_agent': 'user', 'task_completed': False}
执行节点: decision_agent
最新消息: ('user', '你好')
最终状态: {'messages': [('user', '你好'), ('system', '任务完成')], 'current_agent': 'user', 'task_completed': True}
'''