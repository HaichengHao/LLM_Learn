## Runnable

先来看看源码定义
**runnables/base.py**

Runnable定义了一个方法,所有继承它的类.都在重写invoke方法
```text
"""A unit of work that can be invoked, batched, streamed, transformed and composed.

    Key Methods
    ===========

    - `invoke`/`ainvoke`: Transforms a single input into an output.
    - `batch`/`abatch`: Efficiently transforms multiple inputs into outputs.
    - `stream`/`astream`: Streams output from a single input as it's produced.
    - `astream_log`: Streams output and selected intermediate results from an
        input.

    Built-in optimizations:

    - **Batch**: By default, batch runs invoke() in parallel using a thread pool
        executor. Override to optimize batching.

    - **Async**: Methods with `'a'` prefix are asynchronous. By default, they execute
        the sync counterpart using asyncio's thread pool.
        Override for native async.

    All methods accept an optional config argument, which can be used to configure
    execution, add tags and metadata for tracing and debugging etc.

    Runnables expose schematic information about their input, output and config via
    the `input_schema` property, the `output_schema` property and `config_schema`
    method.

    Composition
    ===========

    Runnable objects can be composed together to create chains in a declarative way.

    Any chain constructed this way will automatically have sync, async, batch, and
    streaming support.

    The main composition primitives are `RunnableSequence` and `RunnableParallel`.

    **`RunnableSequence`** invokes a series of runnables sequentially, with
    one Runnable's output serving as the next's input. Construct using
    the `|` operator or by passing a list of runnables to `RunnableSequence`.

    **`RunnableParallel`** invokes runnables concurrently, providing the same input
    to each. Construct it using a dict literal within a sequence or by passing a
    dict to `RunnableParallel`.


    For example,

    ```python
    from langchain_core.runnables import RunnableLambda

    # A RunnableSequence constructed using the `|` operator
    sequence = RunnableLambda(lambda x: x + 1) | RunnableLambda(lambda x: x * 2)
    sequence.invoke(1)  # 4
    sequence.batch([1, 2, 3])  # [4, 6, 8]


    # A sequence that contains a RunnableParallel constructed using a dict literal
    sequence = RunnableLambda(lambda x: x + 1) | {
        "mul_2": RunnableLambda(lambda x: x * 2),
        "mul_5": RunnableLambda(lambda x: x * 5),
    }
    sequence.invoke(1)  # {'mul_2': 4, 'mul_5': 10}
    ```

    Standard Methods
    ================

    All `Runnable`s expose additional methods that can be used to modify their
    behavior (e.g., add a retry policy, add lifecycle listeners, make them
    configurable, etc.).

    These methods will work on any `Runnable`, including `Runnable` chains
    constructed by composing other `Runnable`s.
    See the individual methods for details.

    For example,

    ```python
    from langchain_core.runnables import RunnableLambda

    import random

    def add_one(x: int) -> int:
        return x + 1


    def buggy_double(y: int) -> int:
        \"\"\"Buggy code that will fail 70% of the time\"\"\"
        if random.random() > 0.3:
            print('This code failed, and will probably be retried!')  # noqa: T201
            raise ValueError('Triggered buggy code')
        return y * 2

    sequence = (
        RunnableLambda(add_one) |
        RunnableLambda(buggy_double).with_retry( # Retry on failure
            stop_after_attempt=10,
            wait_exponential_jitter=False
        )
    )

    print(sequence.input_schema.model_json_schema()) # Show inferred input schema
    print(sequence.output_schema.model_json_schema()) # Show inferred output schema
    print(sequence.invoke(2)) # invoke the sequence (note the retry above!!)
    ```

    Debugging and tracing
    =====================

    As the chains get longer, it can be useful to be able to see intermediate results
    to debug and trace the chain.

    You can set the global debug flag to True to enable debug output for all chains:

    ```python
    from langchain_core.globals import set_debug

    set_debug(True)
    ```

    Alternatively, you can pass existing or custom callbacks to any given chain:

    ```python
    from langchain_core.tracers import ConsoleCallbackHandler

    chain.invoke(..., config={"callbacks": [ConsoleCallbackHandler()]})
    ```

    For a UI (and much more) checkout [LangSmith](https://docs.langchain.com/langsmith/home).

    """
```

## 为什么需要统一调用方式

假设没有统一调用方式,每个组件调用方式不同,组合时都需要手动适配
- 提示词渲染用`.format()`
- 模型调用用`.generate()`
- 解析器解析用`.parse()`
- 工具调用`.run()`

极其繁琐且会让代码可读性变得相当差🧋  
所以统一了调用方式后只需要我们`.invoke()`,非常快速且简洁    

Runnable使得langchain中的每个组件拥有统一的调用方式  


----  

## LCEL(langChainExpressionLanguage)  
它是一种从现有的Runnable构建新的Runnable的声明式方法,用于声明，组合和执行各种组件(模型、提示、工具、函数等)    
我们称使用LCEL创建的Runnable为“链”，“链”本身就是Runnable
LCEL的两个主要的组合原语是RunnableSequence和RunnableParallel。许多其他组合原语被认为是这两个原语的变体  

**之前在v0就有写了**
它可以做类似于linux中管道符那样的操作

## RunnableSequence可运行序列

RunnableSequence按顺序“链接”多个可运行对象,其中一个对象的输出作为下一个对象的输入(这里就可以感觉出和管道符理念一致)  
LCEL重载了`|`运算符,以便从两个Runnable创建RunnableSequence.  


作用:  
构造一个串行的执行链,通过runnable_sequence的实例调用invoke方法,就相当于链中每一个组件去调用invoke

实例
```python
# @Time    : 2026/3/24 14:52
# @Author  : hero
# @File    : 14RunnableSequence.py

from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
load_dotenv()

api_key=os.getenv('api_key')
base_url=os.getenv('base_url')

model = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model='gpt-4o-mini',
    temperature=0.8
)

prompt=ChatPromptTemplate(
    [
        ('system','你现在是一个会说话的猫'),
        ('user','{user_instruction}')
    ]
)
parser=StrOutputParser()

#tips:通常写法

chain = prompt|model|parser

#Runnable实例化写法
runnable_sequence=RunnableSequence(
    *[
        prompt,model,parser
    ]
)

resp = runnable_sequence.invoke({'user_instruction':'你会喵喵叫么?'})
print(resp)
'''
当然会喵喵叫！喵~ 你有什么想和我聊的吗？
'''
```

## RunnableParallel的使用   

先来看一个简单例子   
RunnableParallel接收一个字典,字典的键可以自定义,传入的是可执行函数  
构造好之后可以调用invoke,会返回传入的两个函数的返回值,返回的是字典格式
```python
#tips:Runnable是一个可以并行执行chain的一个类

from langchain_core.runnables import RunnableParallel

def fun1(a1):
    return a1+'__func1_output'
def fun2(a2):
    return a2+'__func2_output'

runnable_paralell=RunnableParallel({'key1':fun1,'key2':fun2})

res = runnable_paralell.invoke('你好')
#tips:调用后会把参数同时传递给两个函数fun1,func2,然后运行结束之后会把两个函数运行返回的结果封装为一个字典
print(res)
'''
{'key1': '你好__func1_output', 'key2': '你好__func2_output'}

可以发现其并行执行返回结果
'''
```

实例:调用两个大模型
```python
# @Time    : 2026/3/24 16:10
# @Author  : hero
# @File    : 16Paralell调用不同大模型.py

from langchain_core.runnables import RunnableParallel
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import asyncio
import os


load_dotenv()

api_key = os.getenv('api_key')
base_url=os.getenv('base_url')

zhipu_key =os.getenv('zhipu_key')
zhipu_base_url=os.getenv('zhipu_base_url')


#tips:调用俩模型
model1 = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model='gpt-4o-mini'
)

model2 = ChatOpenAI(
    api_key=zhipu_key,
    base_url=zhipu_base_url,
    model='glm-5'
)

prompt = ChatPromptTemplate(
    messages=[
        ('system','你是一个数学家'),
        ('user','{user_instruction}')
    ]
)
parser=StrOutputParser()
'''
对于用户输入的同一个问题,我们想要调用不同的大模型进行回答,用户可以对比不同大模型回答的效果
'''

chain=prompt|RunnableParallel({'gpt4o-mini':model1,'zpqy':model2})

resp = chain.invoke({'user_instruction':'什么是L2范数?如何计算'})
print(resp)

# async def main():
#     resp = await chain.invoke({'user_instruction':'什么是L2范数?如何计算'})
#     print(resp)
#
# if __name__ == '__main__':
#     asyncio.run(main())
```

---  
## RunnableLambda

看一眼源码介绍  
**将一个可调用的python对象转换为一个Runnable**
```text
class RunnableLambda(Runnable[Input, Output]):
    """`RunnableLambda` converts a python callable into a `Runnable`.

    Wrapping a callable in a `RunnableLambda` makes the callable usable
    within either a sync or async context.

    `RunnableLambda` can be composed as any other `Runnable` and provides
    seamless integration with LangChain tracing.

    `RunnableLambda` is best suited for code that does not need to support
    streaming. If you need to support streaming (i.e., be able to operate
    on chunks of inputs and yield chunks of outputs), use `RunnableGenerator`
    instead.

    Note that if a `RunnableLambda` returns an instance of `Runnable`, that
    instance is invoked (or streamed) during execution.

    Examples:
        ```python
        # This is a RunnableLambda
        from langchain_core.runnables import RunnableLambda


        def add_one(x: int) -> int:
            return x + 1


        runnable = RunnableLambda(add_one)

        runnable.invoke(1)  # returns 2
        runnable.batch([1, 2, 3])  # returns [2, 3, 4]

        # Async is supported by default by delegating to the sync implementation
        await runnable.ainvoke(1)  # returns 2
        await runnable.abatch([1, 2, 3])  # returns [2, 3, 4]


        # Alternatively, can provide both synd and sync implementations
        async def add_one_async(x: int) -> int:
            return x + 1


        runnable = RunnableLambda(add_one, afunc=add_one_async)
        runnable.invoke(1)  # Uses add_one
        await runnable.ainvoke(1)  # Uses add_one_async
        ```
    """
```
简单示例
```python


from langchain_core.runnables import RunnableLambda

runnable_lambda = RunnableLambda(lambda x:x+"__lambdax")
resp = runnable_lambda.invoke(
    'hello'
)
print(resp)
# hello__lambdax 
```

## 利用RunnableLambda改造16Paralell调用不同大模型的代码

```python
# @Time    : 2026/3/24 17:07
# @Author  : hero
# @File    : 17RunnableLambda.py

from langchain_core.runnables import RunnableLambda,RunnableParallel
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('api_key')
base_url=os.getenv('base_url')

zhipu_key =os.getenv('zhipu_key')
zhipu_base_url=os.getenv('zhipu_base_url')

# tips:接下来我们用RunnableLambda来构造后执行函数,优化16Paralell调用不同大模型的输出

model1 = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model='gpt-4o-mini'
)

model2 = ChatOpenAI(
    api_key=zhipu_key,
    base_url=zhipu_base_url,
    model='glm-5'
)

prompt = ChatPromptTemplate(
    messages=[
        ('system','你是一个数学家'),
        ('user','{user_instruction}')
    ]
)

#tips:定义一个函数，从并行输出中提取 content
def extract_contents(results:dict)->dict:
    return {
        key:msg.content for key,msg in results.items()
    }


#tips:构建chain:prompt

chain=prompt|RunnableParallel(
    {'gpt4o-mini':model1,'zpqy':model2}
)|RunnableLambda(extract_contents)

resp = chain.invoke({
    'user_instruction':'什么是L2范数'
})

print(resp)
```