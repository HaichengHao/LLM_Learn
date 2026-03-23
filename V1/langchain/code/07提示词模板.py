# @Time    : 2026/3/23 15:25
# @Author  : hero
# @File    : 07提示词模板.py



import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

'''
1.了解什么是提示词模板:模块+变量值=完整的提示词
2.什么是(Langchain当中的)PromptTemplate
3.什么是ChatPromptTemplate
4.怎么去调用template


适用场景:
'''

load_dotenv()
api_key = os.getenv('api_key')
base_url = os.getenv('base_url')


model=ChatOpenAI(
    model='gpt-4o-mini',
    api_key=api_key,
    base_url=base_url,
    temperature=1.0
)
template=PromptTemplate(
    template='你是一个同声传译,帮助用户将{content}翻译成语言:{lang}',
    input_variables=['content','lang'],
)

parser=StrOutputParser()

chain = template|model|parser

res = chain.invoke(
    {'content':'春雨惊春青谷天','lang':'英语'}
)
print(res)
'''
/home/nikofox/.local/bin/uv run /home/nikofox/LLMlearn/.venv/bin/python /home/nikofox/LLMlearn/V1/langchain/code/07提示词模板.py 
“春雨惊春青谷天”可以翻译为 “Spring rain surprises the green valleys in spring.”
'''

#tips:不习惯的💐话用之前的也可以
# prompt =ChatPromptTemplate.from_messages([
#     ('system','你是一个小学生,只会10以内加减法,问你超过10以内的加减法你就说"对不起我还没学到诶"'),
#     ('user','{user_input}')]
# )

# parser = StrOutputParser()
#
# chain = prompt|model|parser
#
# user_input = input('来考考我吧!!')
# res = chain.invoke({'user_input':user_input})
# print(res)