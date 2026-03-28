# @Time    : 2026/3/26 18:25
# @Author  : hero
# @File    : 00LangServer.py

'''
想要使用langserve需要安装 "langserve[all]",注意引号也是需要的!!!!
它是基于websockit和fastapi实现的
'''

#tips:本次目标,将其部署成服务

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from fastapi import FastAPI
import os
import uvicorn
from langserve import add_routes

load_dotenv()
zai_key = os.getenv('zhipu_key')
zai_url = os.getenv('zhipu_base_url')

app = FastAPI(title='翻译小帮手接口',description='测试用的',version='0.0.1')




model = ChatOpenAI(
    api_key=zai_key,
    base_url=zai_url,
    model='glm-5'
)

prompt_template = ChatPromptTemplate(
    messages=[
        ('system','你现在是一名翻译家,你会将下面的语句翻译成指定的语言'),
        ('human','{origin_language}用{trans_language}怎么说?')
    ]
)

parser = StrOutputParser()

chain=prompt_template|model|parser

# resp = chain.invoke(
#     {'origin_language':'有志者事竞成','trans_language':'英语'}
# )
#
# print(resp)

#important:最关键的就是这一步，但是其实实际生产过程中LangServer并不常用,而是由我们自己来定制路由
add_routes(
    app=app,
    runnable=chain,
    path='/u_little_transagent',

)


if __name__ == '__main__':
    uvicorn.run(app,host='localhost',port=8000,log_level='info')

