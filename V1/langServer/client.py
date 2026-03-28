# @Time    : 2026/3/27 22:58
# @Author  : hero
# @File    : client.py

#important:利用RemoteRunnable可以调用运行中的langserve进行调用
from langserve import RemoteRunnable


if __name__ == '__main__':
    client = RemoteRunnable(url='http://127.0.0.1:8000/u_little_transagent/')
    print(client.invoke({'origin_language':'有志者事竞成','trans_language':'英语'}))

