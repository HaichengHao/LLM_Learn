# @Time    : 2026/4/13 17:04
# @Author  : hero
# @File    : 24条件入口点.py

#important：这个其实就是22的进一步引申,如果不明白回看22，不要有心理压力

'''
条件入口点，和刚才条件边的用法很相似，区别较大的点就在于条件入口点要求与START紧耦合，还有就是用来控制路由选择的函数不需要再作为节点添加 #important
条件入口点允许你根据自定义逻辑从不同的节点开始。你可以使用虚拟 START 节点的 add_conditional_edges 来实现此功能。
from langgraph.graph import START
graph.add_conditional_edges(START, routing_function)
你可以选择提供一个字典，将 routing_function 的输出映射到下一个节点的名称。
graph.add_conditional_edges(START, routing_function, {True: "node_b", False: "node_c"})
'''

'''
LangGraph中条件入口点的典型应用场景
完整展示了条件入口点的核心概念：根据输入内容动态决定从START节点去往哪个处理节点。
条件入口点和条件边写法几乎相同,但是条件入口点是“分岔”的，只要符合就都可以走,而条件边不是，它是有一个判断节点的

看看之前21中用到的条件边
              +-----------+               
              | __start__ |               
              +-----------+               
                    *                     
                    *                     
                    *                     
               +---------+                
               | check_x |                
               +---------+                
             ...          ..              
            .               ..            
          ..                  ..          
+-------------+           +------------+  
| handle_even |           | handle_odd |  
+-------------+           +------------+  
             ***          **              
                *       **                
                 **   **                  
               +---------+                
               | __end__ |                
               +---------+     
'''
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# 1. 定义简单的状态
class SimpleState(TypedDict):
    user_input: str
    response: str
    node_visited: str


# 2. 路由函数 - 决定从START去哪
def route_input(state: SimpleState) -> str:
    """根据用户输入决定去哪个节点"""
    text = state["user_input"].lower()

    if "hello" in text or "hi" in text:
        return "greeting"  # 返回路由键
    elif "bye" in text or "exit" in text:
        return "farewell"  # 返回路由键
    else:
        return "question"  # 返回路由键


# 3. 各个处理节点
def handle_greeting(state: SimpleState) -> SimpleState:
    """处理问候"""
    state["response"] = "你好！很高兴见到你！"
    state["node_visited"] = "greeting_node"
    return state


def handle_farewell(state: SimpleState) -> SimpleState:
    """处理告别"""
    state["response"] = "再见！祝你有个美好的一天！"
    state["node_visited"] = "farewell_node"
    return state


def handle_question(state: SimpleState) -> SimpleState:
    """处理问题"""
    state["response"] = "我听到了你的问题，需要更多帮助吗？"
    state["node_visited"] = "question_node"
    return state


# 4. 创建图
def create_simple_graph():
    """创建一个简单的图"""
    stateGraph = StateGraph(SimpleState)

    # 添加节点
    stateGraph.add_node("greeting_node", handle_greeting)
    stateGraph.add_node("farewell_node", handle_farewell)
    stateGraph.add_node("question_node", handle_question)

    '''条件入口点
     add_conditional_edges(START, route_function, mapping)
         START：从图的起点开始
         route_function：决定去哪里的函数，返回一个字符串（路由键）
         mapping（可选）：路由键到节点名的映射

    START → route_input()函数 → 返回"greeting" → 映射到"greeting_node" → 执行handle_greeting → END
    '''

    stateGraph.add_conditional_edges(
        START,  # 起点
        route_input,  # 路由函数
        # 路由映射（可选）：路由函数的返回值 -> 节点名
        {
            "greeting": "greeting_node",  # route_input返回"greeting"时，去greeting_node
            "farewell": "farewell_node",  # route_input返回"farewell"时，去farewell_node
            "question": "question_node"  # route_input返回"question"时，去question_node
        }
    )

    # 所有节点都到END
    stateGraph.add_edge("greeting_node", END)
    stateGraph.add_edge("farewell_node", END)
    stateGraph.add_edge("question_node", END)

    return stateGraph.compile()


# 5. 使用示例
def run_example():
    # 创建图
    graph = create_simple_graph()
    # 测试不同的输入
    test_inputs = [
        "Hello everyone!",
        "Goodbye now",
        "What time is it?"
    ]

    for user_input in test_inputs:
        print(f"\n输入: {user_input}")
        print("-" * 30)

        # 创建初始状态
        initial_state = SimpleState(
            user_input=user_input,
            response="",
            node_visited=""
        )

        # 执行图
        result = graph.invoke(initial_state)

        print(f"路由决策: {route_input(initial_state)}")
        print(f"访问的节点: {result['node_visited']}")
        print(f"响应: {result['response']}")

    print()
    # 打印图的ascii可视化结构
    print(graph.get_graph().print_ascii())
    print("=================================")
    print()
    # 打印图的可视化结构，生成更加美观的Mermaid 代码，通过processon 编辑器查看
    print(graph.get_graph().draw_mermaid())


# 运行示例
if __name__ == "__main__":
    print("简单条件入口点示例")
    print("=" * 40)
    run_example()

'''
简单条件入口点示例
========================================

输入: Hello everyone!
------------------------------
路由决策: greeting
访问的节点: greeting_node
响应: 你好！很高兴见到你！

输入: Goodbye now
------------------------------
路由决策: farewell
访问的节点: farewell_node
响应: 再见！祝你有个美好的一天！

输入: What time is it?
------------------------------
路由决策: question
访问的节点: question_node
响应: 我听到了你的问题，需要更多帮助吗？

                              +-----------+                                
                              | __start__ |.                               
                         .....+-----------+ .....                          
                     ....           .            ....                      
                .....               .                .....                 
             ...                    .                     ...              
+---------------+           +---------------+           +---------------+  
| farewell_node |           | greeting_node |           | question_node |  
+---------------+****       +---------------+        ***+---------------+  
                     ****           *            ****                      
                         *****      *       *****                          
                              ***   *    ***                               
                               +---------+                                 
                               | __end__ |                                 
                               +---------+                                 
None'''
