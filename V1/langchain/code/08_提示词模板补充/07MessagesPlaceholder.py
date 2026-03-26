# @Time    : 2026/3/25 11:32
# @Author  : hero
# @File    : 07MessagePlaceHolder.py
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_openai  import ChatOpenAI
import os
load_dotenv()

zai_key = os.getenv('zhipu_key')
zai_url = os.getenv('zhipu_base_url')

model = ChatOpenAI(
    api_key=zai_key,
    base_url=zai_url,
    model='glm-4'
)


#tips:当不确定消息模板使用什么角色时,或者希望在格式化过程中插入消息列表时,
#  就需要使用MessagePlaceholder,负责在特定位置添加消息列表
#  使用场景:多轮对话系统存储历史消息以及Agent的中间步骤处理



prompt_template = ChatPromptTemplate(
    [
        ('system','你是一个小说家'),
        MessagesPlaceholder('msgs')
    ]
)


prompt_template.format(
    msgs=[HumanMessage(content='你会写什么小说')]
)

#tips:当然也可以写多个
prompt_template.format(
    msgs=[
        SystemMessage(content='你擅长写科幻小说'),
        HumanMessage(content='你擅长写什么小说?')
    ]
)
# msgs=[HumanMessage(content='你会写什么小说')]
msgs = [
    SystemMessage(content='你擅长写科幻小说'),
    HumanMessage(content='你擅长写什么小说?')
]
resp=model.invoke(msgs)
print(resp)




