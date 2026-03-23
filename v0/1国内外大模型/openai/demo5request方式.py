# @Time    : 2026/3/21 23:08
# @Author  : hero
# @File    : demo5request方式.py

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("api_key")
url = "https://xiaoai.plus/v1/chat/completions"
payload = json.dumps({
   "messages": [
      {
         "role": "system",
         "content": "你是一个大语言模型机器人"
      },
      {
         "role": "user",
         "content": "你好"
      }
   ],
   "stream": False,
   "model": "gpt-3.5-middle",
   "temperature": 0.5,
   "presence_penalty": 0,
   "frequency_penalty": 0,
   "top_p": 1
})
headers = {
    "Content-Type": "application/json",
    # sk-xxx替换为自己的key
   'Authorization': f'Bearer {api_key}',
}
response = requests.request("POST", url, headers=headers, data=payload)
print(response.text)