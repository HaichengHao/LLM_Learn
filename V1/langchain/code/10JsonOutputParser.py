# @Time    : 2026/3/23 22:51
# @Author  : hero
# @File    : 10JsonOutputParser.py

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser  # important:引入输出解析器中的Json输出解析器
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
from typing import Annotated
import asyncio

# tips:JsonOutputParser使用pydantic定义的数据结构,来定义json当中key有哪些,分别的结构是什么
load_dotenv()
api_key = os.getenv('api_key')
base_url = os.getenv('base_url')

model = ChatOpenAI(
    model='gpt-4o-mini',
    api_key=api_key,
    base_url=base_url,
    temperature=1.0
)


# tips:定义模型类
class FilmItem(BaseModel):
    film_name: Annotated[str, Field(description='电影名')]
    out_date: Annotated[str, Field(description='上映日期')]
    film_introduce: Annotated[str, Field(description='电影介绍')]


# tips:由于这次的任务是返回三部推荐的电影所以是JSON嵌套形式
class FilmSuggestion(BaseModel):
    films: Annotated[list[FilmItem], Field(description='推荐的电影列表')]


# important:构造输出解析器，指定模型类(FilmSuggestion)作为验证
# JsonOutputParser:Parse the output of an LLM call to a JSON object. 把大模型的输出解析为JSON格式
jsonparser = JsonOutputParser(pydantic_object=FilmSuggestion)  # tips:指定我们自定义的格式
# tips:构造输出格式
output_format = jsonparser.get_format_instructions()  # 返回格式化的命令(prompt中给llm的命令)
# print(output_format)

"""
看一眼源码,发现返回的是按照我们指定的JSON output格式的提示词模板
def get_format_instructions(self) -> str:
Return the format instructions for the JSON output.

        Returns:
            The format instructions for the JSON output.
        """
prompt = ChatPromptTemplate(
    [
        ('system', '你现在是一个影评专家,回答用户问题,并按照以下形式输出:{output_format}'),
        ('user', '{user_instruction}')
    ]
)

chain = prompt | model | jsonparser

# tips:调用时指定输出格式
# resp = chain.invoke(
#     {'output_format': output_format, 'user_instruction': '请给我推荐三部经典高分电影'}
# )
#
# print(type(resp))
# print(resp)

'''
<class 'dict'>
{'films': [{'film_name': '肖申克的救赎', 'out_date': '1994-09-22', 'film_introduce': '讲述了一个关于希望和友谊的故事，安迪·杜佛兰因被错判入狱，经过多年努力，最终实现逃离和公平的正义。'}, 
{'film_name': '霸王别姬', 'out_date': '1993-01-01', 'film_introduce': '描绘了京剧演员程蝶衣和他的搭档段小楼之间错综复杂的感情，在历史变革中与命运抗争的传奇故事。'}, 
{'film_name': '公民凯恩', 'out_date': '1941-05-01', 'film_introduce': '讲述了媒体巨头查尔斯·福斯特·凯恩的一生，探讨权力、财富与孤独之间的关系。'}
]}
'''


# tips:异步改造
async def main():
    resp = await chain.ainvoke(
        {'output_format': output_format, 'user_instruction': '请给我推荐三部经典高分电影'}

    )
    print(resp)


if __name__ == '__main__':
    asyncio.run(main())

'''
/home/nikofox/.local/bin/uv run /home/nikofox/LLMlearn/.venv/bin/python /home/nikofox/LLMlearn/V1/langchain/code/10JsonOutputParser.py 
{'films': [{'film_name': '肖申克的救赎', 'out_date': '1994-09-23', 'film_introduce': '讲述了银行家安迪因冤屈被关入肖申克监狱，在监狱中努力寻求自由与希望的故事。'}, {'film_name': '教父', 'out_date': '1972-03-24', 'film_introduce': '以科里昂家族的故事为背景，展现了美国黑手党家族的权力斗争与亲情关系。'}, {'film_name': '黑暗骑士', 'out_date': '2008-07-18', 'film_introduce': '蝙蝠侠与小丑之间的斗争，探讨了正义与混乱的主题，引发了观众对道德的深思。'}]}

Process finished with exit code 0
'''