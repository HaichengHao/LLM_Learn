# @Time    : 2026/3/25 09:57
# @Author  : hero
# @File    : 04ChatPromptTemplate.py

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai  import ChatOpenAI,OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser,JsonOutputParser
from langchain_core.runnables import RunnableLambda,RunnableParallel
from dotenv import load_dotenv
import os
load_dotenv()

zai_key = os.getenv('zhipu_key')
zai_base_url = os.getenv('zhipu_base_url')

model=ChatOpenAI( #tips:OpenAI()补全形式已经过时
    api_key=zai_key,
    base_url=zai_base_url,
    model='glm-4'
)


#
prompt_template = ChatPromptTemplate(
    messages=[
        ('system','你叫{uname}'),
        ('human','你好，我的问题是{instruction}')
    ]
)

str1 = prompt_template.format(uname='小言',instruction='土星有几个卫星')

print(str1)
'''
System: 你叫小言
Human: 你好，我的问题是土星有几个卫星
'''

prompt_template1 = ChatPromptTemplate.from_messages(
    messages=[
        ('system','你叫{uname}'),
        ('human','你好，我的问题是{instruction}')
    ]
)
str2=prompt_template1.format(
    uname='小白',
    instruction='西瓜在中国的适宜种植地区有哪些'
)
print(str2)
prompt_template2=ChatPromptTemplate.from_template(
    template='你叫{uname}'
)
str3=prompt_template2.format(uname='小花')
print(str3)
