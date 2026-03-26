# @Time    : 2026/3/25 13:37
# @Author  : hero
# @File    : 08FewShotPromptTemplate.py
from langchain_classic.chains.constitutional_ai.prompts import examples
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
#tips:少量示例的提示词模板
# 它要解决的问题是
#  在构建prompt时,可以通过一个少量示例列表去进一步格式化prompt,这是一种简单但强大的指导生成的方式,在某些情况下可以显著提升模型性能
#  每个示例都是一个字典,其中键是输入变量，值是输入变量的值
#  基于LLM模型与聊天模型,可分别使用FewShotTemplate或FewShotChatMessagePromptTemplate,两者使用基本一致
#  少量示例提示模板可以由一组示例或一个负责从定义的集合中选择一部分示例的示例选择器构建
#important:
# FewShotPromptTemplate结合PromptTemplate使用
# FewShotChatPromptTemplate结合ChatPromptTemplate使用
from langchain_core.prompts import FewShotPromptTemplate,FewShotChatMessagePromptTemplate,PromptTemplate,ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()
zai_key = os.getenv('zhipu_key')
zai_url = os.getenv('zhipu_base_url')

model = ChatOpenAI(
    base_url=zai_url,
    api_key=zai_key,
    model='glm-4'

)

parser=StrOutputParser()
prompt_template=FewShotPromptTemplate(
    example_prompt=PromptTemplate.from_template(
        template='你是{uname},你喜欢{uhobby}',
    ),#tips:示例输入,要求传入的是PromptTemplate类型
    examples=[
        {'uname':'小明','uhobby':'种花'},
        {'uname':'鲲鲲','uhobby':'打篮球'},
        {'uname':'礼堂王','uhobby':'锐克5代'}
    ], #tips:提供示例构造的列表
    suffix="我的问题是:{name},喜欢{hobby}么?", #tips:当前少量提示词模板的提示词模板
    input_variables=['name','hobby']

)
str1 = prompt_template.invoke({'name':'小明','hobby':'种花'})
print(str1)
# text='你是小明,你喜欢种花\n\n你是鲲鲲,你喜欢打篮球\n\n你是礼堂王,你喜欢锐克5代\n\n我的问题是:小明,喜欢种花么?'

chain = prompt_template|model|parser

resp = chain.invoke({'name':'小明','hobby':'种花'})
print(resp)

# 是的，我喜欢种花。