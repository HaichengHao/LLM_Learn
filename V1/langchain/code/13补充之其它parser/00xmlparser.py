# @Time    : 2026/3/25 14:48
# @Author  : hero
# @File    : 00xmlparser.py
from statistics import mode

from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import XMLOutputParser
from dotenv import load_dotenv
import os
import re


load_dotenv()

zai_key = os.getenv('zhipu_key')
zai_url = os.getenv('zhipu_base_url')
api_key = os.getenv('api_key')
base_url=os.getenv('base_url')

# model = ChatOpenAI(
#     api_key=zai_key,
#     base_url=zai_url,
#     model='glm-4'
# )
#

model=ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model='gpt-4o-mini'
)

def clean_xml(text: str) -> str:
    # 去掉 markdown 代码块
    text = re.sub(r"```xml\s*", "", text)
    text = re.sub(r"```", "", text)
    # 确保有根标签（XMLOutputParser 要求有单一根）
    if not text.strip().startswith("<"):
        # 如果模型胡说八道，强行包装
        text = f"<response>{text}</response>"
    return text

parser=XMLOutputParser(

)

output_format = parser.get_format_instructions()


prompt= ChatPromptTemplate(
    messages=[
        ('system',f'你现在是一名影评专家,回答用户问题并按照如下格式输出:{output_format}'),
        ('human','{human_instruction}')

    ]
)

chain = prompt|model|parser


resp =chain.invoke(
    {
        # 'output_format': output_format,
        'human_instruction':'科幻小说的整体最简要素是什么'
    }
)

print(resp)

# /home/nikofox/.local/bin/uv run /home/nikofox/LLMlearn/.venv/bin/python /home/nikofox/LLMlearn/V1/langchain/code/13补充之其它parser/00xmlparser.py
# {'scifi': [{'element': [{'description': '科幻小说的整体最简要素是设定在未来、其他星球或平行宇宙中的情节，通常涉及科学技术的进步和其对人类社会的影响。'}]}]}
#
# Process finished with exit code 0

#tips:不得不提的一点是,即使用了xmlparser,返回的依然是json,因为json在当下绝对是最好的数据格式