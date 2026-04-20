# @Time    : 2026/4/18 10:30
# @Author  : hero
# @File    : main.py

import os
import json
import subprocess
from typing import Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_classic.agents import create_tool_calling_agent,AgentExecutor
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.tools import tool
from loguru import logger
load_dotenv()

zai_key=os.getenv('zhipu_key')
zai_url = os.getenv('zhipu_base_url')



## 构建可以调用技能的工具
@tool(description="调用自己技能的工具")

def tell_joke(joke_type:Literal["programming", "animal","general"]) ->str:
    """
    当用户要求讲个笑话、需要幽默内容或想放松一下时使用。
    支持生成编程笑话、动物笑话或通用笑话。
    :param joke_type:笑话类型，可选 "programming", "animal", "general"
    :return: 一个字符串格式的笑话。
    """
    logger.info('skill正在被调用')
    try:
        #构建命令调用,因为对技能的调用主要是通过运行技能脚本
        result = subprocess.run(
            args=[
                "python",
                "/home/nikofox/LLMlearn/V1/langgraph高级特性/06skills/demo1/joker_generator/scripts/generate_joke.py",
                "--type",
                joke_type,

            ],
            capture_output=True,
            text=True,
            timeout=10#防止脚本卡死
        )
        if result.returncode != 0:
            return "调用笑话生成出错了!稍后再用"

        #解析脚本输出的JSON
        output=json.loads(result.stdout)
        return output["joke"]
    except Exception as e:
        return f'生成时出错,{e}'

# 构建大模型
llm = ChatOpenAI(
    model="glm-4",
    api_key=zai_key,
    base_url=zai_url,
    temperature=0.6
)

#创建智能体
def get_agent():
    agent = create_tool_calling_agent(
        llm=llm,
        tools=[tell_joke],
        prompt=ChatPromptTemplate(
            [
                ('system','你是一个智能化助手，你可以自己调用工具'),
                ('human','{user_input}'),
                MessagesPlaceholder(variable_name='agent_scratchpad')
            ]
        )
    )
    agent_with_skill=AgentExecutor(
        agent=agent,
        tools=[tell_joke],
        verbose=False,
        handle_parsing_errors=False
    )

    return agent_with_skill


if __name__ == '__main__':
    user_input="请给我讲一个动物笑话"
    magent=get_agent()
    res = magent.invoke(
        {
            'user_input':user_input
        }
    )
    print(res)


