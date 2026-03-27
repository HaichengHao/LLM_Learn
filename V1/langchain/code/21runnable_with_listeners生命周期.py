# @Time    : 2026/3/26 17:19
# @Author  : hero
# @File    : 21runnable_with_listeners生命周期.py
import time

from langchain_core.runnables import RunnableLambda,RunnableParallel
from langchain_core.tracers import Run


def test(n:int):
    time.sleep(n)
    return n*2
def onstart(run_obj:Run):
    """当r1启动的时候自动调用"""
    print('r1启动时间',run_obj.start_time)
def onend(run_obj:Run):
    print('r1运行结束的时间',run_obj.end_time)


r1 = RunnableLambda(test)

chain = r1.with_listeners(on_start=onstart,on_end=onend)

chain.invoke(2)

# r1启动时间 2026-03-26 09:17:14.331492+00:00
# r1运行结束的时间 2026-03-26 09:17:16.331929+00:00