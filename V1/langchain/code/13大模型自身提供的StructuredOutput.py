# @Time    : 2026/3/24 14:08
# @Author  : hero
# @File    : 12大模型自身提供的StructuredOutput.py
import os

from langchain_core.output_parsers import JsonOutputParser
#tips:除了langchain中的解析器外,部分大模型自带有结构化输出⚠️注意,并非全部大模型都有这种能力

from pydantic import BaseModel,Field
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Annotated
load_dotenv()
api_key=os.getenv('api_key')
base_url=os.getenv('base_url')

model = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model='gpt-4o-mini',
    temperature=0.7
)


# theway 1 pydantic方式
class FilmItem(BaseModel):
    film_name:Annotated[str,Field(description='电影名称')]
    film_outdate:Annotated[str,Field(description='电影上映时间')]
    film_introduce:Annotated[str,Field(description='电影介绍')]

class FilmSuggesstion(BaseModel):
    films:list[FilmItem]


# jsonparser=JsonOutputParser(pydantic_object=FilmSuggesstion)
# output_fromat = jsonparser.get_format_instructions()

#tips:之前使用的是jsonoutputparser,这次尝试大模型自带的结构化输出

struct_llm = model.with_structured_output(
    schema=FilmSuggesstion,
)

resp = struct_llm.invoke('帮我推荐三部电影')
print(resp)

"""
films=[FilmItem(film_name='降临', film_outdate='2016-11-11', film_introduce='这是一个关于人类与外星人之间第一次接触的故事，围绕着语言、沟通和理解的主题展开。'), 
FilmItem(film_name='大地惊雷', film_outdate='2018-10-12', film_introduce='讲述了一位年轻女子在二战期间的成长故事，她在战争的阴影下寻找自己的身份和爱情。'),
 FilmItem(film_name='寻梦环游记', film_outdate='2017-11-22', film_introduce='一位老人在即将去世前，带着他的孙子踏上了一场寻找冒险与生活意义的旅程。')]

Process finished with exit code 0"""