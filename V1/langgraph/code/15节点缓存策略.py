# @Time    : 2026/4/12 11:53
# @Author  : hero
# @File    : 15节点缓存策略.py

'''
langGraph支持基于节点输入对任务/节点进行缓存，使用缓存的方法如下

编译图(或指定入口点)时指定缓存
为节点指定缓存策略，每个缓存策略支持

key_func用于根据节点的输入生成缓存键 (自动生成的)
ttl,即缓存的生存时间(以秒为单位),如果未指定,缓存永不过期

以下是从图片中提取的文字内容（已修正 OCR 识别错误，如 “Key_func” 应为 key_func，并规范格式）：

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


#给图添加节点并绑定
builder.add_node(node='en1',action=expensive_node)

