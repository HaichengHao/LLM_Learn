# @Time    : 2026/4/19 23:07
# @Author  : hero
# @File    : 09总结消息来优化消息队列.py
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
import os

load_dotenv()

# 创建主model
# 创建model,这里回顾一下，model构建好后就是一个runnable对象
model = init_chat_model(
    model='glm-4',
    model_provider='openai',
    api_key=os.getenv('zhipu_key'),
    base_url=os.getenv('zhipu_base_url'),
    temperature=0.6
)

# 构建总结用model
# tips:然后给model绑定参数,注意,它返回的是一个新的runnable对象
summarization_model = model.bind(max_tokens=128)


# 创建状态
class SummaryState(TypedDict):
    messages: Annotated[list, add_messages]
    summary: str


# 创建节点函数

def summarize_conversation(messages: list, current_summary: str = "") -> str:  # important:将用户发送的信息以及当前的总结作为输入提供给大模型
    """
    使用模型总结对话历史
    :param messages:
    :param current_summary:
    :return:
    """

    # tips:首次调用的时候没有messages,那么只需要返回当前的总结为空字符串就行了,直接设置默认值为空字符串
    if not messages:
        return current_summary

    # tips:如果非首次调用那就说明有messages了,那就走下面的逻辑
    if summarization_model:  # 如果有总结用的模型,那就走下面的逻辑
        try:
            # 构造总结提示
            summary_prompt = f'当前摘要:{current_summary}\n新对话:\n'
            for msg in messages:  # tips:接下来拼接总结消息要用的提示词
                """
                规范地拼接,让大模型能够知道哪个是人类发送的信息，哪个是ai返回的信息
                """
                if isinstance(msg, HumanMessage):
                    summary_prompt += f'人类:{msg.content}\n'
                elif isinstance(msg, AIMessage):
                    summary_prompt += f'AI:{msg.content}\n'

            summary_prompt += '\n请提供一个简洁的摘要,包含重要的信息和上下文:'  # tips:拼接完消息之后再拼接一条总结提示词，让大模型知道我们的意图是总结信息

            # tips:调用总结消息大模型,构造SystemMessage传入总结用提示词
            response = summarization_model.invoke(
                [SystemMessage(content=summary_prompt)]  # tips:以SystemMessage将这个上下文传入
            )
            return response.content  # 返回总结的消息
        except Exception as e:
            print(f'调用总结模型出错:{e}')
            # 出错时使用模拟摘要
            pass

    summary_content = ''.join([msg.content for msg in messages[-3:]])  # 取出最后三条消息
    return f'对话摘要:{summary_content[:100]}...'


# tips:定义节点函数

def summarize_node(state: SummaryState):
    """
    总结消息用的 节点函数
    :param state: 当前状态
    :return: 更新后的状态
    """

    print('\n执行节点:summarize_node')
    messages = state['messages']
    current_summary = state.get('summary', '')  # 获取状态中的当前总结,如果获取不到就默认为空字符串

    print(f'当前消息数量:{len(messages)}')
    print(f'当前摘要:{current_summary}')

    # 设置阈值，超过四条即开始总结
    if len(messages) > 4:
        print('消息数量超过阈值,触发总结历史对话...')
        recent_messages = messages[-4:]  # 获取最近的四条消息
        print(f'最近的四条消息{recent_messages}')
        new_summary = summarize_conversation(recent_messages, current_summary)
        print(f'生成的新摘要:{new_summary}')

        # 返回更新后的摘要和保留最近的几条消息
        return {
            'messages': messages[-2:],  # tips:保留最近的两条消息
            'summary': new_summary
        }
    else:
        print('消息数量未超阈值,无需总结')
        return {
            'summary': current_summary
        }


# tips：定义调用对话模型的节点函数

def call_model(state: SummaryState):
    """
    调用模型的函数
    :param state:
    :return:更新后的状态
    """

    print('\n执行节点:call_model')
    messages = state['messages']
    summary = state.get('summary', '')

    print(f'当前消息数量:{len(messages)}')
    print(f'当前摘要:{summary}')

    # 构造包含摘要的完整上下文
    context_messages = []

    # tips:如果摘要不为空
    if summary:
        context_messages.append(SystemMessage(content=f'之前的对话摘要:{summary}'))

        context_messages.extend(messages)

        # 显示所有消息
        for i, msg in enumerate(context_messages):
            print(f'消息{i + 1}:{type(msg).__name__}-{msg.content[:50]}{"..." if len(msg.content) > 50 else ""}')

        # 如果有模型则调用
        if model:
            try:
                response = model.invoke(input=context_messages)
                print(f'生成的回复:{response.content}')
                return {
                    'messages': [response]
                }
            except Exception as e:
                print(f'调用模型时出错:{e}')


def main():
    """主函数 - 演示对话总结功能"""
    print("=== LangGraph 对话总结演示 ===\\n")

    # 创建检查点保存器
    checkpointer = InMemorySaver()

    # 构建图
    builder = StateGraph(SummaryState)
    builder.add_node("summarize", summarize_node)
    builder.add_node("call_model", call_model)

    # 添加边
    builder.add_edge(START, "summarize")
    builder.add_edge("summarize", "call_model")

    # 编译图
    graph = builder.compile(checkpointer=checkpointer)

    # 配置线程ID
    config = {"configurable": {"thread_id": "1"}}

    # 第一次调用 - 问候
    print("1. 第一次调用 - 问候:")
    result1 = graph.invoke({
        "messages": [HumanMessage(content="hi, my name is bob")],
        "summary": ""
    }, config)
    print(f"回复: {result1['messages'][-1].content}")
    print(f"当前摘要: {result1.get('summary', '')}")

    print("\\n" + "=" * 50 + "\\n")

    # 第二次调用 - 请求写诗（关于猫）
    print("2. 第二次调用 - 请求写诗（关于猫）:")
    result2 = graph.invoke({
        "messages": [HumanMessage(content="write a short poem about cats")],
        "summary": result1.get("summary", "")
    }, config)
    print(f"回复: {result2['messages'][-1].content}")
    print(f"当前摘要: {result2.get('summary', '')}")

    print("\\n" + "=" * 50 + "\\n")

    # 第三次调用 - 请求写诗（关于狗）
    print("3. 第三次调用 - 请求写诗（关于狗）:")
    result3 = graph.invoke({
        "messages": [HumanMessage(content="now do the same but for dogs")],
        "summary": result2.get("summary", "")
    }, config)
    print(f"回复: {result3['messages'][-1].content}")
    print(f"当前摘要: {result3.get('summary', '')}")

    print("\\n" + "=" * 50 + "\\n")

    # 第四次调用 - 询问名字
    print("4. 第四次调用 - 询问名字:")
    result4 = graph.invoke({
        "messages": [HumanMessage(content="what's my name?")],
        "summary": result3.get("summary", "")
    }, config)
    print(f"回复: {result4['messages'][-1].content}")
    print(f"当前摘要: {result4.get('summary', '')}")

    print("\\n" + "=" * 50 + "\\n")

    # 第五次调用 - 添加更多对话以触发总结
    print("5. 第五次调用 - 添加更多对话以触发总结:")
    conversation_history = [
        HumanMessage(content="让我们聊聊天气"),
        AIMessage(content="好的，你想聊什么地区的天气？"),
        HumanMessage(content="北京的天气怎么样？"),
        AIMessage(content="我无法获取实时天气信息，但北京属于温带大陆性季风气候。"),
        HumanMessage(content="what's my name?")  # 再次询问名字
    ]

    result5 = graph.invoke({
        "messages": conversation_history,
        "summary": result4.get("summary", "")
    }, config)
    print(f"回复: {result5['messages'][-1].content}")
    print(f"当前摘要: {result5.get('summary', '')}")

    print("\\n=== 演示完成 ===")


if __name__ == "__main__":
    main()

'''
=== LangGraph 对话总结演示 ===\n
1. 第一次调用 - 问候:

执行节点:summarize_node
当前消息数量:1
当前摘要:
消息数量未超阈值,无需总结

执行节点:call_model
当前消息数量:1
当前摘要:
回复: hi, my name is bob
当前摘要: 
\n==================================================\n
2. 第二次调用 - 请求写诗（关于猫）:

执行节点:summarize_node
当前消息数量:2
当前摘要:
消息数量未超阈值,无需总结

执行节点:call_model
当前消息数量:2
当前摘要:
回复: write a short poem about cats
当前摘要: 
\n==================================================\n
3. 第三次调用 - 请求写诗（关于狗）:

执行节点:summarize_node
当前消息数量:3
当前摘要:
消息数量未超阈值,无需总结

执行节点:call_model
当前消息数量:3
当前摘要:
回复: now do the same but for dogs
当前摘要: 
\n==================================================\n
4. 第四次调用 - 询问名字:

执行节点:summarize_node
当前消息数量:4
当前摘要:
消息数量未超阈值,无需总结

执行节点:call_model
当前消息数量:4
当前摘要:
回复: what's my name?
当前摘要: 
\n==================================================\n
5. 第五次调用 - 添加更多对话以触发总结:

执行节点:summarize_node
当前消息数量:9
当前摘要:
消息数量超过阈值,触发总结历史对话...
最近的四条消息[AIMessage(content='好的，你想聊什么地区的天气？', additional_kwargs={}, response_metadata={}, id='d0ed55db-f914-4396-9bf2-62c95d19f278', tool_calls=[], invalid_tool_calls=[]), HumanMessage(content='北京的天气怎么样？', additional_kwargs={}, response_metadata={}, id='351b0f8c-6f26-4e97-b990-4e0ab9410f16'), AIMessage(content='我无法获取实时天气信息，但北京属于温带大陆性季风气候。', additional_kwargs={}, response_metadata={}, id='fd29bee4-289b-417d-a997-fda7a047d49d', tool_calls=[], invalid_tool_calls=[]), HumanMessage(content="what's my name?", additional_kwargs={}, response_metadata={}, id='32459957-6435-4465-b39b-8227fdfdbd8b')]
调用总结模型出错:Error code: 400 - {'error': {'code': '1214', 'message': 'messages 参数非法。请检查文档。'}}
生成的新摘要:对话摘要:北京的天气怎么样？我无法获取实时天气信息，但北京属于温带大陆性季风气候。what's my name?...

执行节点:call_model
当前消息数量:9
当前摘要:对话摘要:北京的天气怎么样？我无法获取实时天气信息，但北京属于温带大陆性季风气候。what's my name?...
消息1:SystemMessage-之前的对话摘要:对话摘要:北京的天气怎么样？我无法获取实时天气信息，但北京属于温带大陆性季风气候。w...
消息2:HumanMessage-hi, my name is bob
消息3:HumanMessage-write a short poem about cats
消息4:HumanMessage-now do the same but for dogs
消息5:HumanMessage-what's my name?
消息6:HumanMessage-让我们聊聊天气
消息7:AIMessage-好的，你想聊什么地区的天气？
消息8:HumanMessage-北京的天气怎么样？
消息9:AIMessage-我无法获取实时天气信息，但北京属于温带大陆性季风气候。
消息10:HumanMessage-what's my name?
生成的回复:
Your name is Bob.
回复: 
Your name is Bob.
当前摘要: 对话摘要:北京的天气怎么样？我无法获取实时天气信息，但北京属于温带大陆性季风气候。what's my name?...
\n=== 演示完成 ===

'''