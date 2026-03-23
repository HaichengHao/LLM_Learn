# @Time    : 2026/3/21 22:53
# @Author  : hero
# @File    : 02用request去调用.py
#tips:openai的也可以用的
import json
import requests
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("zhipu_key")
url = "https://open.bigmodel.cn/api/paas/v4/async/chat/completions"

payload = json.dumps({
    "model": "glm-4.7",
    "messages": [
        {
            "role": "system",
            "content": "你是一个悬疑小说小说家。"
        },
        {
            "role": "user",
            "content": "写一个500字以内的短篇悬疑小说,不需要有结局"
        }
    ],
    "temperature": 1,
    "stream":False
})
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.post(url, data=payload, headers=headers)

print(response)
print(response.text)