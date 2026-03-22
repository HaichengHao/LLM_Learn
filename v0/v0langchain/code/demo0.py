# @Time    : 2026/3/22 10:19
# @Author  : hero
# @File    : demo0.py
import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser,JsonOutputParser #tips:除了字符串解析器之外和还有别的解析器



load_dotenv()
from langchain_openai  import ChatOpenAI
from langchain_core.prompts  import ChatPromptTemplate

api_key = os.getenv('api_key')
base_url = os.getenv('base_url')

glm_api_key = os.getenv('zhipu_key')
glm_base_url = os.getenv('')

#tips:如果用国内的直接换成国内的api_key和base_url就行

#step 1:选择大模型
llm_openai = ChatOpenAI(
    model="gpt-3.5-turbo",
    api_key=api_key,
    base_url=base_url,
    temperature=1.0
)

# llm_glm = ChatOpenAI(
#     model="gpt-3.5-turbo",
#     api_key=api_key,
#     base_url=base_url,
#     temperature=1.0
# )

#step 2创建提示词模板
prompt=ChatPromptTemplate.from_messages(
    messages=[
        ('system','把下面的语句翻译成{language}'),
        ('user','{user_text}')
    ]
)

#step 3 定义解析器,使用字符串输出解析器

parser =  StrOutputParser(

)
#tips:如果不想要字符串解析器也可以写别的解析器,譬如JSON解析器
# json_parser = JsonOutputParser(
#
# )

#tips:初级写法需要固定死写法,理解即可
"""
prompt1=[
        SystemMessage('把下面的语句翻译成英文'),
        HumanMessage('春眠不觉晓')
    ]

res = llm_openai.invoke(
    prompt1
)
print(res)
print(parser.invoke(res))
"""


#important:设置LCEL
chain = prompt | llm_openai | parser
#tips 提示词->大模型->解析器  ,其实如果按照linux中的管道符来理解也是可以的

res = chain.invoke({'language':'英文','user_text':'春眠不觉晓'})
print(res)
'''
/home/nikofox/.local/bin/uv run /home/nikofox/LLMlearn/.venv/bin/python /home/nikofox/LLMlearn/v2langchain/code/demo0.py 
Spring sleep knows no dawn.
'''