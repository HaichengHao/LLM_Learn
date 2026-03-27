# @Time    : 2026/3/27 12:24
# @Author  : hero
# @File    : 03JsonSchema方式.py

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

schema = {
  "name": "animal_list",
  "schema": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "animal": {"type": "string", "description": "动物名称"},
        "emoji": {"type": "string", "description": "动物的emoji表情"},
      },
      "required": ["animal", "emoji"],
    },
  },
}
messages=[
    ('human','任意生成三种动物以及它们的emoji表情')
]

llm_with_structured_output=model.with_structured_output(schema,method="json_schema",include_raw=True)
resp = llm_with_structured_output.invoke(messages)

print(resp)
print(resp['raw'])
print(resp['schema'])