# @Time    : 2026/3/23 17:35
# @Author  : hero
# @File    : 09多模态提示词.py

import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage,SystemMessage


load_dotenv()

api_key=os.getenv("api_key")
base_url=os.getenv("base_url")


model = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model='gpt-4o-mini'
)

prompt = ChatPromptTemplate(
    [
        ('system','用中文简短描述图片内容'),
        ('human',[
            {'type':'text','text':'请描述这张图片:'},
            {'type':'image_url','image_url':'{image_url}'}
        ])
    ]
)

parser = StrOutputParser()

chain = prompt|model|parser

res = chain.invoke(
    {'image_url':'https://c-ssl.dtstatic.com/uploads/blog/202308/12/JOSbDj1qCWj6X66.thumb.400_0.png'}
)


print(res)


'''
/home/nikofox/.local/bin/uv run /home/nikofox/LLMlearn/.venv/bin/python /home/nikofox/LLMlearn/V1/langchain/code/09多模态提示词.py 
这张图片中是一只可爱的猫咪，毛色是淡橙色和白色相间。它正趴在一条皱纹的毛毯上，眼睛大而圆，看起来特别无辜和可爱。背景有一扇窗户，给人温暖舒适的感觉。

Process finished with exit code 0
'''