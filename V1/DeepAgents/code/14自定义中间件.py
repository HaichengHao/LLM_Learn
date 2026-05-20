# @Time    : 2026/5/19 16:54
# @Author  : hero
# @File    : 14自定义中间件.py
#

#tips:利用@wrap_tool_call实现自定义中间件

from langchain.agents.middleware import wrap_tool_call
from langgraph.store.memory import InMemoryStore
from langchain_core.tools import tool
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import SummarizationMiddleware,ModelCallLimitMiddleware,ToolCallLimitMiddleware
from dotenv import load_dotenv
from pathlib import Path
import os



load_dotenv()
store = InMemoryStore()

llm = init_chat_model(
    model='glm-4',
    model_provider='openai',
    api_key=os.getenv('zhipu_key'),
    base_url=os.getenv('zhipu_base_url')
)




@tool
def calc_n(a:int,b:int):
    """
    这是一个计算两数之间的乘法的工具，遇到计算乘法任务时，你可以调用它
    :param a:
    :param b:
    :return:
    """
    print('工具被调用')
    res = a*b
    print(f"执行操作{a}x{b}={res}")
    return res

#important：自定义中间件，监控工具的调用和结束
#1.定义一个函数即可->必须要有两个参数 request,handler
#2.函数上添加装饰器@wrap_tool_call
#3.自定义中间件的处理逻辑:日志/权限/访问次数设置
#4.只要是中间件，不管是langchain提供好的还是自己定义的，都要配置到deepagent的中间件列表中

@wrap_tool_call
def log_tool_call(request,handler):
    """
    中间件，监控工具的调用,进行日志前后的日志输出,
    :param request: 调用目标工具的参数
    :param handler: 执行目标工具的执行器
    :return: 最终的返回结果
    """
    print('---------------进入中间件---------------')
    print(f'request={request},handler={handler}')
    #这块代码，前置增强，可在执行目标工具之前修改参数


    res=handler(request) #tips:必须要做的一件事


    #这块代码,后置增强,修改目标工具的返回结果

    print(f"result={res}")
    print("--------------退出中间件----------------")
    return res






agent = create_deep_agent(
    model=llm,
    tools=[calc_n],
    system_prompt="回答使用中文,调用对应的工具实现对应的功能!",
    middleware=[log_tool_call,],
    checkpointer=InMemorySaver(),
)


if __name__ == '__main__':
    config={
        'configurable':{
            'thread_id':'demo1'
        }
    }

    result = agent.invoke(
        {
            'messages':[
                {'role':'user',
                 'content':'帮我计算100*2的结果'}
            ]
        },
        config=config
    )

    #输出最终结果
    print(result['messages'][-1].content)

'''
---------------进入中间件---------------
request=ToolCallRequest(
tool_call={'name': 'calc_n', 'args': {'a': 100, 'b': 2}, 
            'id': 'call_-7604236780069453057', 'type': 'tool_call'},
            tool=StructuredTool(name='calc_n',
            description='这是一个计算两数之间的乘法的工具，遇到计算乘法任务时，你可以调用它\n
            :param a:\n:param b:\n:return:',
            args_schema=<class 'langchain_core.utils.pydantic.calc_n'>, 
            func=<function calc_n at 0x789453ca7f60>), 
            state={'messages': 
                    [HumanMessage(content='帮我计算100*2的结果', 
                     additional_kwargs={}, 
                     response_metadata={}, 
                     id='4634eff6-a654-43cf-8377-ca7f31984adf'), 
                     AIMessage(
                        content='\n我来帮您计算100乘以2的结果。\n', 
                        additional_kwargs={'refusal': None}, 
                        response_metadata={'token_usage': {'completion_tokens': 33, 'prompt_tokens': 5924, 
                        'total_tokens': 5957, 'completion_tokens_details': None, 'prompt_tokens_details': None},
                        .....
handler=<function ToolNode._run_one.<locals>.execute at 0x7894541df6a0>

result=content='200' name='calc_n' tool_call_id='call_-7604236780069453057'
--------------退出中间件----------------
100乘以2的结果是200。

'''