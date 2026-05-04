# @Time    : 2026/4/28 17:36
# @Author  : hero
# @File    : 01快速入门.py

import asyncio
import gradio as gr
from typing import Literal
from tavily import TavilyClient
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from dotenv import load_dotenv
import os

load_dotenv()

zai_key = os.getenv("zhipu_key")
zai_url = os.getenv("zhipu_base_url")


#初始化tavily_client客户端
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def internet_search(
    query: str,#关键字
    max_results: int = 5,#条数
    topic: Literal["general", "news", "finance"] = "general",#类型
    include_raw_content: bool = False,#是否精简
):
    """Run a web search"""
    return tavily_client.search(
        query=query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


def init_model():
    return ChatOpenAI(
        model="glm-4",
        api_key=zai_key,
        base_url=zai_url,
        max_tokens=400,
        streaming=True,
    )


research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""

agent = create_deep_agent(
    model=init_model(),
    tools=[internet_search],
    system_prompt=research_instructions,
)


#直接调用,
# important:注意agent本质是用langgraph的,所以用langgraph的默认状态键messages
#下面是追溯到的源码
'''
class AgentState(TypedDict, Generic[ResponseT]):
    """State schema for the agent."""

    messages: Required[Annotated[list[AnyMessage], add_messages]]
    jump_to: NotRequired[Annotated[JumpTo | None, EphemeralValue, PrivateStateAttr]]
    structured_response: NotRequired[Annotated[ResponseT, OmitFromInput]]
    
    '''
demores=agent.invoke({
            "messages": [
                {"role": "user", "content": "今天沈阳和平区天气如何"}
            ]
        })

print(demores['messages'][-1]['content'])
#或者这里简单写
# res=agent.invoke(input="今天沈阳天气如何")



#下面的是写的用gradio结合异步生成器返回流式会话版本

#important：构建用来过滤消息的函数
def build_messages(message:list, history): #tips:因为传入的是{"messages":[{"role":"user","content":"xxx"}]}这样的形式
    messages = [] #构建消息列表

    for item in history:
        role = item.get("role")
        content = item.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": message})
    return messages


async def predict(message, history):
    total_resp = ""
    #important:关于构造inputs的格式,可以查看根目录下的彻底搞懂input的第五节,Agent和LangGraph通吃State
    # 由于Langgraph构造状态一般使用的是Annotated[list,add_messages],所以其常见输入如下
    '''
        {
            "messages": [
                {"role": "user", "content": "你好"}
            ]
        }'''
    inputs = {
        "messages": build_messages(message, history)#tips:这里返回的就是[{"role": "user", "content": "你好"}]这样的列表
    }

# =================================================================================


#tips:这里拿出一个示例看看设置了流模式为messages后输出的结果的结构
    """
    (AIMessageChunk(content='\n', additional_kwargs={}, response_metadata={'model_provider': 'openai'}, id='lc_run--019dd76e-fd04-7eb2-bb1e-4f39eec19c71', tool_calls=[], invalid_tool_calls=[], tool_call_chunks=[]), 
    
    {'ls_integration': 'langchain_chat_model', 'versions': {'deepagents': '0.5.3'}, 'lc_agent_name': None, 'langgraph_step': 2, 'langgraph_node': 'model', 'langgraph_triggers': ('branch:to:model',), 'langgraph_path': ('__pregel_pull', 'model'), 'langgraph_checkpoint_ns': 'model:93898834-f2c9-46d8-0bc3-1456bfc142e7', 'checkpoint_ns': 'model:93898834-f2c9-46d8-0bc3-1456bfc142e7', 'ls_provider': 'openai', 'ls_model_name': 'glm-4', 'ls_model_type': 'chat', 'ls_temperature': None})
    
    (AIMessageChunk(content='', additional_kwargs={}, response_metadata={'model_provider': 'openai'}, id='lc_run--019dd76e-fd04-7eb2-bb1e-4f39eec19c71', tool_calls=[{'name': 'internet_search', 'args': {'query': '沈阳故宫地址 地址', 'max_results': 3}, 'id': 'call_8decdd0ac8b3432f935b5d5c', 'type': 'tool_call'}], invalid_tool_calls=[], tool_call_chunks=[{'name': 'internet_search', 'args': '{"query":"沈阳故宫地址 地址","max_results":3}', 'id': 'call_8decdd0ac8b3432f935b5d5c', 'index': 0, 'type': 'tool_call_chunk'}]), {'ls_integration': 'langchain_chat_model', 'versions': {'deepagents': '0.5.3'}, 'lc_agent_name': None, 'langgraph_step': 2, 'langgraph_node': 'model', 'langgraph_triggers': ('branch:to:model',), 'langgraph_path': ('__pregel_pull', 'model'), 'langgraph_checkpoint_ns': 'model:93898834-f2c9-46d8-0bc3-1456bfc142e7', 'checkpoint_ns': 'model:93898834-f2c9-46d8-0bc3-1456bfc142e7', 'ls_provider': 'openai', 'ls_model_name': 'glm-4', 'ls_model_type': 'chat', 'ls_temperature': None})
    (AIMessageChunk(content='', additional_kwargs={}, response_metadata={'finish_reason': 'tool_calls', 'model_name': 'glm-4', 'model_provider': 'openai'}, id='lc_run--019dd76e-fd04-7eb2-bb1e-4f39eec19c71', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 6030, 'output_tokens': 27, 'total_tokens': 6057, 'input_token_details': {}, 'output_token_details': {}}, tool_call_chunks=[]), {'ls_integration': 'langchain_chat_model', 'versions': {'deepagents': '0.5.3'}, 'lc_agent_name': None, 'langgraph_step': 2, 'langgraph_node': 'model', 'langgraph_triggers': ('branch:to:model',), 'langgraph_path': ('__pregel_pull', 'model'), 'langgraph_checkpoint_ns': 'model:93898834-f2c9-46d8-0bc3-1456bfc142e7', 'checkpoint_ns': 'model:93898834-f2c9-46d8-0bc3-1456bfc142e7', 'ls_provider': 'openai', 'ls_model_name': 'glm-4', 'ls_model_type': 'chat', 'ls_temperature': None})
    (AIMessageChunk(content='', additional_kwargs={}, response_metadata={}, id='lc_run--019dd76e-fd04-7eb2-bb1e-4f39eec19c71', tool_calls=[], invalid_tool_calls=[], tool_call_chunks=[], chunk_position='last'), {'ls_integration': 'langchain_chat_model', 'versions': {'deepagents': '0.5.3'}, 'lc_agent_name': None, 'langgraph_step': 2, 'langgraph_node': 'model', 'langgraph_triggers': ('branch:to:model',), 'langgraph_path': ('__pregel_pull', 'model'), 'langgraph_checkpoint_ns': 'model:93898834-f2c9-46d8-0bc3-1456bfc142e7', 'checkpoint_ns': 'model:93898834-f2c9-46d8-0bc3-1456bfc142e7', 'ls_provider': 'openai', 'ls_model_name': 'glm-4', 'ls_model_type': 'chat', 'ls_temperature': None})
    (ToolMessage(content='{"query": "沈阳故宫地址 地址", "follow_up_questions": null, "answer": null, "images": [], "results": [{"url": "https://www.amap.com/place/B001809F61", "title": "沈阳故宫博物院- 沈阳市沈河区| 地址营业时间", "content": "沈阳故宫博物院位于沈阳市沈河区，详细地址：沈阳市沈河区沈阳路171号。在Amap查看沈阳故宫博物院的精确位置、周边设施、用户评价，获取最佳出行路线和实时导航服务，", "score": 0.9999658, "raw_content": null}, {"url": "https://www.sypm.org.cn/map.html", "title": "地理位置-沈阳故宫博物院", "content": "地址：中国辽宁省沈阳市沈河区沈阳路171号\u3000邮政编码：110011\u3000地铁站点：中街.", "score": 0.99986017, "raw_content": null}, {"url": "https://m.map.360.cn/m/search/detail/pid=b50545c110628e0d", "title": "【沈阳故宫】地址,电话,路线,周边设施", "content": "沈阳故宫位于辽宁省沈阳市沈河区沈阳路171号，始建于1625年，占地6万多平方米，建筑面积约9千平方米，是中国仅存的两大皇家宫殿建筑群之一，也是关外唯一的皇家建筑群，为国家一", "score": 0.9998579, "raw_content": null}], "response_time": 0.86, "request_id": "72bf1617-4d9a-4c41-a019-7e13527da466"}', name='internet_search', id='af6b703e-6436-456e-8a46-17c320df03b1', tool_call_id='call_8decdd0ac8b3432f935b5d5c'), {'ls_integration': 'deepagents', 'versions': {'deepagents': '0.5.3'}, 'lc_agent_name': None, 'langgraph_step': 4, 'langgraph_node': 'tools', 'langgraph_triggers': ('__pregel_push',), 'langgraph_path': ('__pregel_push', 0, False), 'langgraph_checkpoint_ns': 'tools:42e8be0a-0b64-d3a7-69c7-8501c5810dff'})
    (AIMessageChunk(content='\n', additional_kwargs={}, response_metadata={'model_provider': 'openai'}, id='lc_run--019dd76f-3b74-7492-bf5b-506b4c52884f', tool_calls=[], invalid_tool_calls=[], tool_call_chunks=[]), {'ls_integration': 'langchain_chat_model', 'versions': {'deepagents': '0.5.3'}, 'lc_agent_name': None, 'langgraph_step': 5, 'langgraph_node': 'model', 'langgraph_triggers': ('branch:to:model',), 'langgraph_path': ('__pregel_pull', 'model'), 'langgraph_checkpoint_ns': 'model:dba1bfdc-f988-68b5-ccc1-85e87aef99a0', 'checkpoint_ns': 'model:dba1bfdc-f988-68b5-ccc1-85e87aef99a0', 'ls_provider': 'openai', 'ls_model_name': 'glm-4', 'ls_model_type': 'chat', 'ls_temperature': None})
    (AIMessageChunk(content='沈阳', additional_kwargs={}, response_metadata={'model_provider': 'openai'}, id='lc_run--019dd76f-3b74-7492-bf5b-506b4c52884f', tool_calls=[], invalid_tool_calls=[], tool_call_chunks=[]), {'ls_integration': 'langchain_chat_model', 'versions': {'deepagents': '0.5.3'}, 'lc_agent_name': None, 'langgraph_step': 5, 'langgraph_node': 'model', 'langgraph_triggers': ('branch:to:model',), 'langgraph_path': ('__pregel_pull', 'model'), 'langgraph_checkpoint_ns': 'model:dba1bfdc-f988-68b5-ccc1-85e87aef99a0', 'checkpoint_ns': 'model:dba1bfdc-f988-68b5-ccc1-85e87aef99a0', 'ls_provider': 'openai', 'ls_model_name': 'glm-4', 'ls_model_type': 'chat', 'ls_temperature': None})'''
    

"""
    #tips:如果指定用messages的模式输出的话返回的就是(chunk,metadata)
    async for chunk, metadata in agent.astream(
        inputs,
        stream_mode="messages", #tips:忘记的话就去看langgraph高级特性中的Streaming
    ):
        content = getattr(chunk, "content", "") #tips:这里用getattr获取chunk中的content
        #上面相当于content=chunk['content']
        if not content:
            continue

        if isinstance(content, list): #如果返回的内容是列表的话就遍历列表拿出内容元素
            text = ""
            for item in content:
                if isinstance(item, dict):
                    text += item.get("text", "")
                else:
                    text += str(item)
        else:
            text = str(content)

        if text:
            total_resp += text
            yield total_resp
            await asyncio.sleep(0.01)


# async def predict(
#         message,history
# ):
#     full_resp=''
#     async for chunk,metadata in agent.astream(input=message,stream_mode='messages'):
#         full_resp+=chunk['content']
#         await asyncio.sleep(0.01)
#         yield full_resp



if __name__ == "__main__":
    demo = gr.ChatInterface(
        fn=predict,
        title="联网搜索 demo",
        examples=[
            "木苹果是什么?",
            "印度尼西亚的首都在哪里?",
            "牡丹花用英文怎么说",
        ],
        multimodal=False,
        autofocus=True,
    )

    demo.launch(
        server_name="127.0.0.1",
        server_port=5558,
        share=False,
        debug=True,
    )