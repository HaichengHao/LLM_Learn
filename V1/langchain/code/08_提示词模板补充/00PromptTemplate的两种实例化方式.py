# @Time    : 2026/3/24 22:41
# @Author  : hero
# @File    : 00两种实例化方式.py
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate
from langchain_openai  import OpenAI,ChatOpenAI
from langchain_core.output_parsers import StrOutputParser,JsonOutputParser
from langchain_core.runnables import RunnableLambda,RunnableParallel
from dotenv import load_dotenv
import os
load_dotenv()

zai_key = os.getenv('zhipu_key')
zai_base_url = os.getenv('zhipu_base_url')

#theway  第一种，构造方法
template1=PromptTemplate(
    template="你是一个小智商超高的小猫咪,名字叫{catname}",
    input_variables=['catname'] #tips:指定模板的变量
)


#tips:调用方式.format
user_format = template1.format(
    catname="小黑"
)

print(user_format)
#你是一个小智商超高的小猫咪,名字叫小黑

#tips:当然,也可以传入多个变量
template2 = PromptTemplate(
    template="你是一个{species},你叫{uname},你喜欢{hobby}",
    input_variables=['species','uname','hobby']
)

user_format2=template2.format(
    species="小兔子",
    uname="小月",
    hobby="吃萝卜"
)
print(user_format2)
# 你是一个小兔子,你叫小月,你喜欢吃萝卜


#theway 第二种,from_template()
# 该方法只需传入template即可,不需要像上面那样还要传入指明变量
template3 = PromptTemplate.from_template(
   template="你是一个{species},你叫{uname},你喜欢{hobby}",
)
user_format3 = template3.format(
    species="小狗",
    uname='布鲁斯',
    hobby='吃骨头'
)
print(user_format3)
