# @Time    : 2026/4/12 11:53
# @Author  : hero
# @File    : 15节点缓存策略.py

'''
langGraph支持基于节点输入对任务/节点进行缓存，使用缓存的方法如下

编译图(或指定入口点)时指定缓存
为节点指定缓存策略，每个缓存策略支持

.add_node(node,action,cache_policy=CachePolicy(key_func,ttl)))
key_func用于根据节点的输入生成缓存键 (自动生成的)
ttl,即缓存的生存时间(以秒为单位),如果未指定,缓存永不过期


缓存键与命中：
当一个节点开始执行时，系统会使用其配置的 key_func 根据当前节点的输入数据生成一个唯一的键。
LangGraph 会检查缓存中是否存在这个键。

如果存在（缓存命中），则直接返回之前存储的结果，跳过该节点的实际执行。
如果不存在（缓存未命中），则正常执行节点函数，并将结果与缓存键关联后存入缓存。

缓存有效期：
ttl 参数能控制缓存的有效期。

例如，对于依赖实时数据的天气查询节点，可以设置较短的 ttl（如 60 秒）。
而对于处理静态信息或变化不频繁数据的节点，则可以设置较长的 ttl 甚至不设置（None），
让缓存永久有效，直到手动清除。

'''
import time

from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated

#important：下面俩函数用于实现缓存策略
from langgraph.cache.memory import InMemoryCache
from  langgraph.types import CachePolicy

#定义状态类，也就是业务实体
class State(TypedDict):
    x:int
    result:int

#创建图
builder = StateGraph(State)

#定义节点函数 ：模拟耗时计算
def expensive_node(state:State)->dict[str,int]:
    time.sleep(3)
    return {
        'result':state['x']*2
    }


#给图添加节点并绑定，别有心理压力,就是把之前没写的参数写上去了罢了,之前写就是.add('en1',expensive_node),现在是写上参数名并加上了内存缓存规约
builder.add_node(node='en1',
                 action=expensive_node,
                 cache_policy=CachePolicy(ttl=8)#important:不用传key_fn,底层自动用默认逻辑
)


#设置入口和出口，这次不用START和END,换成另一种
builder.set_entry_point("en1")
builder.set_finish_point("en1")


#编译图,指定内存缓存
#因为我们上面添加的节点有缓存了，所以要编译的时候得指定一个地方让它能存进去,所以我们可以指定内存
graph = builder.compile(
    cache=InMemoryCache(),
)

#第一次执行,耗时3秒(无缓存)
print('第一次执行(无缓存,耗时3s):')
res1 = graph.invoke(
    {
        'x':2,
        #result不传入的话按照schema的类型就是int,初始值就是0,因为并未将其设为必须传入
    }
)
print(res1)

#tips:第二次执行,瞬间返回(因为利用了缓存)
res2 = graph.invoke(
    {
        'x':5
    }
)
print('第二次运行利用缓存并快速返回:')
print(res2)


print('等待8s后缓存过期,这时候调用就又会很慢了')
time.sleep(8)
print('第三次执行,由于缓存过期,就又得等了')
res3 = graph.invoke(
    {
        'x':5
    }
)
print(res3)