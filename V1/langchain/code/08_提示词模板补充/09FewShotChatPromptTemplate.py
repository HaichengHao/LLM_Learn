# @Time    : 2026/3/25 14:21
# @Author  : hero
# @File    : 09FewShotChatPromptTemplate.py

#important:
# FewShotPromptTemplate结合PromptTemplate使用
# FewShotChatPromptTemplate结合ChatPromptTemplate使用
from langchain_core.prompts import FewShotChatMessagePromptTemplate,ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

zai_key = os.getenv('zhipu_key')
zai_url = os.getenv('zhipu_base_url')


model = ChatOpenAI(
    api_key=zai_key,
    base_url=zai_url,
    model='glm-4'
)


parser=StrOutputParser()


examples = [
            {"input": "2+2", "output": "4"},
            {"input": "2+3", "output": "5"},
        ]

example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "What is {input}?"),
        ("ai", "{output}"),
    ]
)

few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    # This is a prompt template used to format each individual example.
    example_prompt=example_prompt,
)

final_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful AI Assistant"),
        few_shot_prompt,
        ("human", "{input}"),
    ]
)
final_prompt.format(input="What is 4+4?")

chain=final_prompt|model|parser


resp=chain.invoke({'input':'核聚变'})
print(resp)

