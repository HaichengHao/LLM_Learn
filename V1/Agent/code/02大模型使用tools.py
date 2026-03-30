# @Time    : 2026/3/30 11:21
# @Author  : hero
# @File    : 02大模型使用tools.py
# from gradio.mcp import tool
from langchain_core.tools import tool
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
import os

from openai import base_url

load_dotenv()
zai_key=os.getenv('zhipu_key')
zai_url = os.getenv('zhipu_base_url')
api_key=os.getenv('api_key')
base_url=os.getenv('base_url')

model =ChatOpenAI(
    api_key=zai_key,
    base_url=zai_url,
    model='glm-4'
)
# model =ChatOpenAI(
#     api_key=api_key,
#     base_url=base_url,
#     model='gpt-4o-mini'
# )

@tool
def calc_expo(base:int,exponent:int):
    """
    返回指数运算结果
    :param base:
    :param exponent:
    :return:
    """
    return base**exponent

#tips:接下来就是让大模型绑定tools使用.bind_tools

'''看看源码,要求传入的是BaseTool序列，刚好调用tool创建的工具返回的就是BaseTool
def bind_tools(self,
               tools: Sequence[dict[str, Any] | type | (...) -> Any | BaseTool],
               *,
               tool_choice: dict | str | bool | None = None,
               strict: bool | None = None,
               parallel_tool_calls: bool | None = None,
               response_format: dict[str, Any] | type | None | Any = None,
               **kwargs: Any) -> Runnable[PromptValue | str | Sequence[BaseMessage | list[str] | tuple[str, str] | str | dict[str, Any]], AIMessage]'''
mytools=[calc_expo]
model_with_tool=model.bind_tools(mytools)

res=model_with_tool.invoke(
   '计算2的5次方'
)
print(res)
"""content='' additional_kwargs={'refusal': None} response_metadata={'token_usage': {'completion_tokens': 21, 'prompt_tokens': 66, 'total_tokens': 87, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'gpt-4o-mini-2024-07-18', 'system_fingerprint': 'fp_eb37e061ec', 'id': 'chatcmpl-DOxndx3KBVVhRX9bGVdk5vpoju3kX', 'finish_reason': 'tool_calls', 'logprobs': None} id='lc_run--019d3cd5-65c4-7502-b306-640be8f43dde-0' tool_calls=[{'name': 'calc_expo', 'args': {'base': 2, 'exponent': 5}, 'id': 'call_FILAATKDRCkxUq7CEoGBJGKZ', 'type': 'tool_call'}] invalid_tool_calls=[] usage_metadata={'input_tokens': 66, 'output_tokens': 21, 'total_tokens': 87, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}}

"""
print(res.tool_calls)
# [{'name': 'calc_expo', 'args': {'base': 2, 'exponent': 5}, 'id': 'call_adFgwZ7UvI3QRyMXKcvtFBjP', 'type': 'tool_call'}]