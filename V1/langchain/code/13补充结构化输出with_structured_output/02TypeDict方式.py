# @Time    : 2026/3/27 12:21
# @Author  : hero
# @File    : 02TypeDict方式.py

from typing import Annotated,TypedDict
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

zai_key =  os.getenv('zhipu_key')
zai_base_url = os.getenv('zhipu_base_url')

model  = ChatOpenAI(
    model='glm-4',
    base_url=zai_base_url,
    api_key=zai_key
)

class Animals(TypedDict):
    animal:Annotated[str,'动物']
    emoji:Annotated[str,'表情']


class AnimalList(TypedDict):
    animals:Annotated[list[Animals],'动物与表情列表']

messages=[
    ('human','任意生成三种动物以及它们的emoji表情')
]

llm_with_structured_output=model.with_structured_output(AnimalList)
resp = llm_with_structured_output.invoke(messages)

print(resp)