# @Time    : 2026/3/24 23:15
# @Author  : hero
# @File    : 01部分提示词模板和组合提示词的使用.py
from langchain_core.prompts import PromptTemplate
from langchain_openai  import OpenAI,ChatOpenAI
from langchain_core.output_parsers import StrOutputParser,JsonOutputParser
from langchain_core.runnables import RunnableLambda,RunnableParallel
from dotenv import load_dotenv
import os
load_dotenv()

zai_key = os.getenv('zhipu_key')
zai_base_url = os.getenv('zhipu_base_url')


#tips:部分提示词模板

template = PromptTemplate.from_template(
    template='你叫{name},你喜欢{hobby}',
    partial_variables={'name':'小言'} #tips:部分提示词模板提前赋值
)
# tips:除此之外我们还可以按照属性赋值法赋值
template.partial(name='小言')

uformat=template.format(hobby='打篮球')

print(uformat)
# 你叫小言,你喜欢打篮球


# tips:除此之外我们还可以按照属性赋值法赋值
template1 = PromptTemplate.from_template(
    template='你叫{name},你喜欢{hobby}',
)
template1new= template.partial(name='小言')
uformat1 = template1new.format(hobby='烫头')
print(uformat1)

