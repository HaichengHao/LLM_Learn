# @Time    : 2026/3/23 14:40
# @Author  : hero
# @File    : 00回顾一下协程.py

#tips:
# 协程针对于IO密集型任务适用，CPU密集型不适用
# IO密集型:等待数据传输和写入的任务，比如http请求(比如调用大模型API的时候就是发送一个http请求),接收文件
# CPU密集型：数学计算

import time
import asyncio

async def func1():
    print('func1开始')
    await asyncio.sleep(3)
    print('func1结束')

async def func2():
    print('func2开始')
    await asyncio.sleep(5)
    print('func2结束')

async def func3():
    print('func3开始')
    await asyncio.sleep(10)
    print('func3结束')


async def main():
    await asyncio.gather(func1(), func2(), func3())

start_time = time.time()
asyncio.run(main())
end_time = time.time()
total_time = end_time - start_time
print(total_time)

'''
/home/nikofox/.local/bin/uv run /home/nikofox/LLMlearn/.venv/bin/python /home/nikofox/LLMlearn/V1/langchain/code/00回顾一下协程.py 
func1开始
func2开始
func3开始
func1结束
func2结束
func3结束
10.006443738937378

可见异步的情况下执行三个函数的化只需要约10s(差不多就是最长时间的await),如果是同步的话
那么这个数字在除去其它延时的情况下将会是3+5+10=18s,整整8s
'''