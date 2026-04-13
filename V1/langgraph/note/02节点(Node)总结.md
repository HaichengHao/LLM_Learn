# 节点

## 定义一个节点
```text
节点是langGraph中的一个 基本处理单元，代表工作流中的一个操作步骤,
可以是一个Agent、调用大模型、工具或一个函数(说白了就是绑定一个python函数,
具体逻辑可以干任何事情)

最佳实践:
单一职责(Single Responsibility)
纯函数优先(Prefer Pure Functions)

常见模式(Common Patterns)
LLM调用,工具调用

设计模式:
单一职责:每个节点应该只负责一项职责，避免功能过于复杂
无状态设计:节点本身不应该保存状态，所有数据都通过输入状态传递
幂等性：相同的输入应该产生相同的输出，确保可重试性
可测试性:节点逻辑应该易于单元测试


内置的__START__和__END__节点是非常实用的
之后会学到graph.set_entry_point('node_name')函数设置起始节点,等价于graph.add_edges(START,'node_name')
之后会学到graph.set_finish_point('node_name')函数设置终止点,等价于graph.add_edges('node_name',END)


```
**节点的添加就是.add_node(node_name="自定义的名称",action=构造的节点函数)**
```python
from functools import partial

from langgraph.graph import StateGraph,START,END
from typing   import TypedDict,Annotated

from langgraph.types import RetryPolicy
from requests import RequestException


#定义状态图 state_schema
class GraphState(TypedDict):
    process_data:dict


#定义节点函数,入参为state

def input_node(state:GraphState) -> GraphState:
    print(f'input_node收到的初始值为:{state}')
    return {
        'process_data':{
            'input':'input_value'
        }
    }


#定义带参数的节点
def process_node(state:dict,param1:int,param2:str) -> dict:
    print(state,param1,param2)
    return {
        'process_data':{
            "process":"process_value"
        }
    }

#重试策略,add_node方法时可选
retry_policy=RetryPolicy(
    max_attempts=3,
    initial_interval=1,#初始间隔
    jitter=True, #添加随机性避免重试风暴
    backoff_factor=2,#避免乘数(每次重试间隔时间的增长倍数)
    retry_on=[
        RequestException,
        TimeoutError,
    ] #只重试这些异常
)


#创建图
builder=StateGraph(GraphState)
#添加节点
builder.add_node('input',input_node)

#tips:给process_node节点绑定参数
process_with_params=partial(process_node,param1=100,param2='test')

#important:添加带参数的node节点
# 之前写的都省略了,譬如.add_node('nodename','node_function'),其实等价于.add_node(node='nodename',action='node_function')
builder.add_node(node='process',action=process_with_params,retry_policy=retry_policy)


#定义节点之间的执行顺序edges
#设置节点间的依赖关系,形成执行流程图
builder.add_edge(START,'input')
builder.add_edge('input','process')
builder.add_edge('process',END)

#编译图
graph=builder.compile()


#打印图的边和节点信息
print(builder.edges)
'''
{('input', 'process'), ('process', '__end__'), ('__start__', 'input')}  注意,要倒过来看,从最后一个元组往前推
'''
print(builder.nodes)
'''
'''
#打印图的可视化显示
print(graph.get_graph().print_ascii())


#定义一个初始化状态字典,包含在键值对"x":5
initial_state={
    'state':5
}
res=graph.invoke(
    initial_state
)
print(res)
'''
+-----------+  
| __start__ |  
+-----------+  
      *        
      *        
      *        
  +-------+    
  | input |    
  +-------+    
      *        
      *        
      *        
 +---------+   
 | process |   
 +---------+   
      *        
      *        
      *        
 +---------+   
 | __end__ |   
 +---------+   
None
input_node收到的初始值为:{}
{'process_data': {'input': 'input_value'}} 100 test
{'process_data': {'process': 'process_value'}}
'''
```

## 节点的策略
langGraph支持基于节点输入对任务/节点进行缓存，使用缓存的方法如下  

.add_node(node,action,cache_policy=CachePolicy(key_func,ttl)))
key_func用于根据节点的输入生成缓存键 (自动生成的)
ttl,即缓存的生存时间(以秒为单位),如果未指定,缓存永不过期

编译图(或指定入口点)时指定缓存  

为节点指定缓存策略，每个缓存策略支持  

```text
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
```
### 节点缓存策略CachePolicy

在给图添加节点的时候指定缓存策略`CachePolicy()`  
并在编译图的时候指定cache为`InMemoryCache()`  

```python
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
```


### 节点异常重试RetryPolicy

在添加节点的时候传入`RetryPolicy(ax_attempts=最大尝试次数, retry_on=重试触发函数)`

**一些参数**
```python
retry_policy=RetryPolicy(
    max_attempts=3,
    initial_interval=1,#初始间隔
    jitter=True, #添加随机性避免重试风暴
    backoff_factor=2,#避免乘数(每次重试间隔时间的增长倍数)
    retry_on=[
        RequestException,
        TimeoutError,
    ] #只重试这些异常
)
```

```text
langGraph提供了错误处理和重试机制来指定重试次数、重试间隔、重试异常等，用于保证系统的可靠性

为节点添加重试策略,需要在add_node中设置retry_policy参数,retry_policy参数接收一个RetryPolicy命名元组对象
默认情况下,retry_on参数使用default_retry_on函数,该函数会在遇到任何异常时重试

默认重试策略:max_attmpts=5,对Exception重试,对ValueError/TypeError等不重试,异常过滤列表完全相同:
自定义重试策略:max_attmpts=5+custom_retry_on,仅对包含模拟API调用失败的异常重试;
不可重试测试:ValueError直接抛出,无重试,max_attmpts=3
```
 
```python
from typing import Dict, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy


# 定义状态类型
class DemoState(TypedDict):
    result: str

# 全局计数器：记录API尝试次数
attempt_counter = 0


# 工具函数
def build_retry_graph(node_name: str, node_func, retry_policy: RetryPolicy):
    builder = StateGraph(DemoState)
    #为节点添加重试策略，需要在add_node中设置retry_policy参数。
    # retry_policy参数接受一个RetryPolicy命名元组对象。
    # 默认情况下，retry_on参数使用default_retry_on函数，该函数会在遇到任何异常时重试
    builder.add_node(node_name, node_func, retry_policy=retry_policy)
    builder.add_edge(START, node_name)
    builder.add_edge(node_name, END)
    return builder.compile()


# 模拟不稳定的API调用，使用全局变量跟踪尝试次数
def unstable_api_call(state: DemoState) -> Dict[str, Any]:
    """模拟不稳定API：前2次失败，第3次成功（全局计数器记录尝试次数）"""
    global attempt_counter
    attempt_counter += 1
    # 纯文本打印尝试次数
    print(f"尝试调用API，这是第 {attempt_counter} 次尝试")

    # 模拟失败/成功逻辑：前2次抛异常，第3次返回结果
    if attempt_counter < 3:
        raise Exception(f"模拟API调用失败abcd (尝试 {attempt_counter})")
    return {"result": f"API调用成功，经过 {attempt_counter} 次尝试"}

# 自定义重试条件判断函数
def custom_retry_on(exception: Exception) -> bool:
    """自定义重试规则：只对包含「模拟API调用失败」的异常重试"""
    print("########################:  "+str(exception))
    err_msg = str(exception)
    if "模拟API调用失败" in err_msg:
        print(f"捕获到可重试异常: {err_msg}")
        return True
    print(f"捕获到不可重试异常: {err_msg}")
    return False

# 模拟抛出 ValueError 的节点
def value_error_call(state: DemoState) -> Dict[str, Any]:
    """模拟抛出ValueError：默认重试策略对这类异常不重试"""
    print("调用会抛出 ValueError 的节点")
    raise ValueError("模拟 ValueError 异常")


# 测试方法1：默认重试策略
def test_default_retry():
    global attempt_counter
    print("1. 使用默认重试策略:")
    print("   默认策略会对除特定异常外的所有异常进行重试")
    print("   不会重试的异常包括: ValueError, TypeError, ArithmeticError, ImportError,")
    print("                     LookupError, NameError, SyntaxError, RuntimeError,")
    print("                     ReferenceError, StopIteration, StopAsyncIteration, OSError\n")

    print("测试默认重试策略:")
    attempt_counter = 0  # 重置计数器
    default_graph = build_retry_graph(
        node_name="unstable_api",
        node_func=unstable_api_call,
        retry_policy=RetryPolicy(max_attempts=5)  # 最多5次尝试，足够重试成功
    )
    try:
        result = default_graph.invoke({"result": ""})
        print(f"最终结果: {result}\n")
    except Exception as e:
        print(f"最终失败: {type(e).__name__}: {e}\n")


# 测试方法2：自定义重试策略（输出完全匹配要求）
def test_custom_retry():
    global attempt_counter
    print("2. 使用自定义重试策略:")
    print("   自定义策略只对特定错误进行重试\n")
    print("测试自定义重试策略:")
    attempt_counter = 0  # 重置计数器
    custom_graph = build_retry_graph(
        node_name="custom_retry_api",
        node_func=unstable_api_call,
        retry_policy=RetryPolicy(max_attempts=5, retry_on=custom_retry_on)
    )
    try:
        result = custom_graph.invoke({"result": ""})
        print(f"最终结果: {result}\n")
    except Exception as e:
        print(f"最终失败: {type(e).__name__}: {e}\n")


# 测试方法3：不可重试异常演示,测试 ValueError（默认策略不会重试）
def test_no_retry_exception():
    print("3. 测试不会重试的异常类型:")
    print("测试 ValueError（默认策略不会重试）:")
    no_retry_graph = build_retry_graph(
        node_name="value_error_node",
        node_func=value_error_call,
        retry_policy=RetryPolicy(max_attempts=3)
    )
    try:
        result = no_retry_graph.invoke({"result": ""})
        print(f"最终结果: {result}\n")
    except Exception as e:
        print(f"最终失败: {type(e).__name__}: {e}\n")


# 主演示函数
def run_demo():
    print("=== LangGraph 节点重试策略完整演示===")
    print("-" * 80 + "\n")
    #test_default_retry()
    #test_custom_retry()
    test_no_retry_exception()
    print("-" * 80)
    print("=== 演示结束 ===")


# 程序入口
if __name__ == "__main__":
    run_demo()
```
### 节点等待与超步
大规模并行图计算的模型，执行过程分为3个阶段
1.Plan(规划)，确定本论要执行的节点
2.Executive(执行):并行执行所有选中的节点
3.Update(更新):将节点输出更新到通道(channels)

每个轮次称为一个超步"(super-step)",系统会持续迭代知道没有节点需要执行

当开启defer=True的时候，这个节点会监控前序节点又没有流向它的数据流，如果有则等待所有流向它的数据流结束再进行下一步   

```python
from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated,Any
import operator
import uuid

class MStateGraph(TypedDict):
    aggreate:Annotated[list,operator.add]

def a(state:MStateGraph):
    """
    启动分支
    :param state: 当前状态
    :return: 包含新结果的状态更新
    """
    print(f'Addding "A" to  {state["aggreate"]}')
    return {
        'aggreate':['A']
    }

def b(state:MStateGraph):
    print(f'Addding "B" to  {state["aggreate"]}')
    return {
        'aggreate': ['B']
    }

def b2(state:MStateGraph):
    print(f'Addding "B2" to  {state["aggreate"]}')
    return {
        'aggreate': ['B2']
    }

def c(state:MStateGraph):
    print(f'Addding "C" to  {state["aggreate"]}')
    return {
        'aggreate': ['C']
    }

def d(state:MStateGraph):
    print(f'Addding "D" to  {state["aggreate"]}')
    return {
        'aggreate': ['D']
    }

builder  = StateGraph(MStateGraph)


builder.add_node('a',a)
builder.add_node('b',b)
builder.add_node('b2',b2)
builder.add_node('c',c)
# builder.add_node('d',d,defer=True) #important:设置defer=True延迟执行
builder.add_node('d',d) #tips:尝试关掉等待会怎样


builder.add_edge(START,'a')
builder.add_edge('a','b')
builder.add_edge('a','c')
builder.add_edge('b','b2')
builder.add_edge('b2','d')
builder.add_edge('c','d')
builder.add_edge('d',END)

app = builder.compile()

res = app.invoke(
    {}
)
print(f'执行结果{res}')

print(app.get_graph().print_ascii())
output_path = '../demoimgs/'+str(uuid.uuid4())[:8]+'.png'
with open(output_path,'wb') as f:
    f.write(app.get_graph().draw_mermaid_png())
```
启用等待的结果
```text
Addding "A" to  []
Addding "B" to  ['A']
Addding "C" to  ['A']
Addding "B2" to  ['A', 'B', 'C']
Addding "D" to  ['A', 'B', 'C', 'B2']
执行结果{'aggreate': ['A', 'B', 'C', 'B2', 'D']}
```

不启用等待结果  
```text
Addding "A" to  []
Addding "B" to  ['A']
Addding "C" to  ['A']
Addding "B2" to  ['A', 'B', 'C']
Addding "D" to  ['A', 'B', 'C']
Addding "D" to  ['A', 'B', 'C', 'B2', 'D']
执行结果{'aggreate': ['A', 'B', 'C', 'B2', 'D', 'D']}
```

## 延迟节点执行
在需要延迟执行的节点上指明`defer=True` 
即.add_node(node_name,action,defer=True)
```python

from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated,Any
import operator
import uuid

class MStateGraph(TypedDict):
    aggreate:Annotated[list,operator.add]

def a(state:MStateGraph):
    """
    启动分支
    :param state: 当前状态
    :return: 包含新结果的状态更新
    """
    print(f'Addding "A" to  {state["aggreate"]}')
    return {
        'aggreate':['A']
    }

def b(state:MStateGraph):
    print(f'Addding "B" to  {state["aggreate"]}')
    return {
        'aggreate': ['B']
    }

def b2(state:MStateGraph):
    print(f'Addding "B2" to  {state["aggreate"]}')
    return {
        'aggreate': ['B2']
    }

def c(state:MStateGraph):
    print(f'Addding "C" to  {state["aggreate"]}')
    return {
        'aggreate': ['C']
    }

def d(state:MStateGraph):
    print(f'Addding "D" to  {state["aggreate"]}')
    return {
        'aggreate': ['D']
    }

builder  = StateGraph(MStateGraph)


builder.add_node('a',a)
builder.add_node('b',b)
builder.add_node('b2',b2)
builder.add_node('c',c)
# builder.add_node('d',d,defer=True) #important:设置defer=True延迟执行
builder.add_node('d',d) #tips:尝试关掉等待会怎样


builder.add_edge(START,'a')
builder.add_edge('a','b')
builder.add_edge('a','c')
builder.add_edge('b','b2')
builder.add_edge('b2','d')
builder.add_edge('c','d')
builder.add_edge('d',END)

app = builder.compile()

res = app.invoke(
    {}
)
print(f'执行结果{res}')

print(app.get_graph().print_ascii())
# output_path = '../demoimgs/'+str(uuid.uuid4())[:8]+'.png'
# with open(output_path,'wb') as f:
#     f.write(app.get_graph().draw_mermaid_png())
```