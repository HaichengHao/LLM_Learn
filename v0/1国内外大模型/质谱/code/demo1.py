# @Time    : 2026/3/21 21:06
# @Author  : hero
# @File    : demo1.py
from zai   import ZhipuAiClient
import os
from dotenv  import load_dotenv
load_dotenv()

api_key=os.getenv("zhipu_key")

client=ZhipuAiClient(
    api_key=api_key
)
response =   client.chat.completions.create(
    model='glm-4.7',
    messages=[
        {"role": "system", "content": "你是一个伟大的悬疑小说家"},
        {"role": "user", "content": "帮我生成一个200字左右的悬疑小说,简短又能引起遐想,没必要有结局"}
    ],
    max_tokens=400,
    # temperature=1.0
)

print(response.choices[0].message)