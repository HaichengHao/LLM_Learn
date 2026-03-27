# @Time    : 2026/3/27 12:07
# @Author  : hero
# @File    : 01Pydantic方式.py
from langchain_classic.chains.question_answering.map_reduce_prompt import messages
from pydantic import BaseModel,Field
from typing import Annotated
# from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

zai_key =  os.getenv('zhipu_key')
zai_base_url = os.getenv('zhipu_base_url')


# model  = init_chat_model(
#     model='glm-5',
#     # model_provider='',
#     base_url=zai_base_url,
#     api_key=zai_key
# )

model  = ChatOpenAI(
    model='glm-5',
    # model_provider='',
    base_url=zai_base_url,
    api_key=zai_key
)

class Animals(BaseModel):
    animal:Annotated[str,Field(description='动物')]
    emoji:Annotated[str,Field(description='表情')]


class AnimalList(BaseModel):
    animals:Annotated[list[Animals],Field(description='动物与表情列表')]

messages=[
    ('human','任意生成三种动物以及它们的emoji表情')
]

llm_with_structured_output=model.with_structured_output(AnimalList)
resp = llm_with_structured_output.invoke(messages)

print(resp)