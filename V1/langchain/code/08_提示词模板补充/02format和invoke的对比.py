# @Time    : 2026/3/24 23:36
# @Author  : hero
# @File    : 02format和invoke的对比.py
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


uformat=template.format(hobby='打篮球')

print(uformat)
# 你叫小言,你喜欢打篮球


# tips:除此之外我们还可以按照属性赋值法赋值
template1 = PromptTemplate.from_template(
    template='你叫{name},你喜欢{hobby}',
)
#important:注意,需要用新的变量名来接收
template1new= template.partial(name='小言')
uformat1 = template1new.format(hobby='烫头')
print(uformat1)

# 你叫小言,你喜欢烫头

#theway invoke,形参是字典，返回值是PromptValue

template2 = PromptTemplate.from_template(
    template='你叫{name},你喜欢{hobby}',
)

prompt1 = template2.invoke({'name':'张三','hobby':'跑步'})
print(type(prompt1))
print(prompt1)
print(prompt1.text)
print(type(prompt1.text))
# <class 'langchain_core.prompt_values.StringPromptValue'>
# text='你叫张三,你喜欢跑步'
# 你叫张三,你喜欢跑步
# <class 'str'>

#important:总结,其实本质上都是实现了template.format(**{prompt}),本质是对于python解包赋值对封装
