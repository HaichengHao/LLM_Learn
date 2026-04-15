# @Time    : 2026/4/15 11:50
# @Author  : hero
# @File    : 31运行时上下文.py

#important:就是让图能拿到不属于状态的信息
'''
创建Graph时，可以为传递给节点的运行时上下文指定一个context_schema。
这对于向节点传递`不属于图状态的信息`很有用。
例如，可以传递诸如模型名称或数据库连接之类的依赖项。

1）使用 context_schema 的优势：
（1）分离关注点：将运行时配置与图状态分离，保持状态的纯净性
（2）类型安全：通过定义数据类，提供类型检查和 IDE 自动补全支持
（3）易于管理：统一管理运行时依赖，如数据库连接、API密钥等
2）适用场景包括：
（1）传递模型配置信息（如模型名称、参数等）
（2）传递数据库连接、API密钥等敏感信息
（3）在不同环境中动态切换配置
（4）传递用户身份信息或其他运行时上下文
3）使用方式
（1）Context Schema（上下文结构）
important:使用 @dataclass 定义了一个 ContextSchema 类，定义的内容不属于图的状态，但在运行时需要被节点访问
（2）节点函数定义
tips 节点函数接收两个参数：state（图的状态）和 runtime（运行时上下文）
tips 通过 runtime.context 访问上下文信息，如 runtime.context.model_name
（3）图的创建和执行
tips 创建 StateGraph 时传入 context_schema=ContextSchema 参数
tips 调用 graph.invoke() 时通过 context 参数传递上下文数据
'''

"""
RuntimeContextDemo.py

LangGraph Context Schema 演示

演示如何在 LangGraph 1.0 中使用 context_schema 向节点传递不属于图表状态的信息。
这在传递模型名称、数据库连接等依赖项时非常有用。
"""

"""
关于@dataclass的一些小理解
Add dunder ("dunder" 是编程术语，源自英文 "double underscore" 的缩写，特指以双下划线开头和结尾的标识符
)methods based on the fields defined in the class.

    Examines PEP 526 __annotations__ to determine fields.

    If init is true, an __init__() method is added to the class. If repr
    is true, a __repr__() method is added. If order is true, rich
    comparison dunder methods are added. If unsafe_hash is true, a
    __hash__() method is added. If frozen is true, fields may not be
    assigned to after instance creation. If match_args is true, the
    __match_args__ tuple is added. If kw_only is true, then by default
    all fields are keyword-only. If slots is true, a new class with a
    __slots__ attribute is returned.
"""

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime #important:引入运行时
'''源码译文
一个便利类，它封装了运行作用域上下文和其他运行时实用程序。
    这个类被注入到图节点和中间件中。它提供了访问权限
    `context`、`store`、`stream_writer`、`previous` 以及 `execution_info`。'''
from langchain_core.messages import AIMessage, HumanMessage
from dataclasses import dataclass #important：注意本次要用到它


# 定义状态结构
class AgentState(TypedDict):
    messages: Annotated[list, lambda x, y: x + y]
    response: str


# 定义上下文结构
@dataclass
class ContextSchema:
    model_name: str
    db_connection: str
    api_key: str
#important:@dataclass本质上也是python定义类的一种方式
# 它本质上是这样的
"""
class ContextSchema(object):
    def __init__(self, model_name: str, db_connection: str, api_key: str):
        self.model_name = model_name
        self.db_connection = db_connection
        self.api_key = api_key
        
@dataclass 帮你省掉__init__/__repr__/__eq__的手写代码，专注业务逻辑即可
"""

# important:节点函数：处理用户消息，除了指定state之外再指定runtime运行时
def process_message(state: AgentState, runtime: Runtime[ContextSchema]) -> dict:
    """处理用户消息的节点，使用context中的信息"""
    print("执行节点: process_message")

    # 获取最新的用户消息
    last_message = state["messages"][-1].content if state["messages"] else ""
    print(f"用户消息: {last_message}")
    print("=========以下是从RuntimeContext中获得信息=========")
    # tips:使用runtime.context中的信息
    model_name = runtime.context.model_name
    db_connection = runtime.context.db_connection
    api_key = runtime.context.api_key

    print(f"使用的模型: {model_name}")
    print(f"数据库连接: {db_connection}")
    print(f"API密钥前缀: {api_key[:5]}***")  # 只显示前5位，隐藏其余部分

    # 模拟使用这些信息处理请求
    response = f"使用 {model_name} 处理了您的请求，已连接到 {db_connection}"

    return {
        "messages": [AIMessage(content=response)],
        "response": response
    }


# 节点函数：生成最终响应
def generate_response(state: AgentState, runtime: Runtime[ContextSchema]) -> dict:
    """生成最终响应的节点"""
    print("执行节点: generate_response")

    # 使用runtime.context中的信息
    model_name = runtime.context.model_name
    print(f"使用模型 {model_name} 生成最终响应")

    # 获取之前的结果
    previous_response = state["response"]

    # 生成更详细的响应
    final_response = f"{previous_response}\n\n这是使用 {model_name} 生成的完整响应。"

    return {
        "messages": [AIMessage(content=final_response)],
        "response": final_response
    }


def main():
    """演示 context_schema 的使用"""
    print("=== Context Schema 演示 ===\n")

    #tips: 实例化一个上下文对象context
    context = ContextSchema(
        model_name="gpt-4-turbo",
        db_connection="postgresql://user:pass@localhost:5432/orders_db",
        api_key="sk-abcdefghijklmnopqrstuvwxyz123456"
    )

    # important:创建图，指定state_schema和context_schema
    builder = StateGraph(state_schema=AgentState, context_schema=ContextSchema)

    # 添加节点
    builder.add_node("process_message", process_message)
    builder.add_node("generate_response", generate_response)

    # 添加边
    builder.add_edge(START, "process_message")
    builder.add_edge("process_message", "generate_response")
    builder.add_edge("generate_response", END)

    # 编译图
    graph = builder.compile()

    # 定义初始状态
    initial_state = {
        "messages": [HumanMessage(content="请帮我查询最新的订单信息")],
        "response": ""
    }

    print("初始状态:", initial_state)
    print()
    print("上下文信息:\n", {
        "model_name": context.model_name,
        "db_connection": context.db_connection,
        "api_key": f"{context.api_key[:5]}***"
    })
    print("\n" + "-" * 50 + "\n")

    # 执行图，通过context参数传递上下文
    result = graph.invoke(input=initial_state, context=context)

    print("\n" + "=" * 50)
    print("最终状态:", result)
    print("\n最终响应:")
    print(result["response"])


if __name__ == "__main__":
    main()
'''
步骤总结
定义@dataclass,编写ContextSchema
创建图(builder=StateGraph(state_schema=DemoState,context_schema=ContextSchema))的时候传入context_schema,将其指定为自己编写的ContextSchema

创建节点函数(def node_demo(state:DemoState,runtime:Runtime[ContextSchema]))的时候，如果节点函数需要传入上下文,那就给其指定runtime:Runtime[ContextSchema]]]

实例化ContextSchema对象
执行图(graph.invoke(input={},context=context))的时候，传入基于ContextSchema创建的上下文context

'''