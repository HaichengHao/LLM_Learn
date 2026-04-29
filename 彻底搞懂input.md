你这个疑惑非常正常，因为 LangChain / LangGraph 里确实有好几种“看起来都像输入”的格式。

一句话先定调：

**不同写法不是互相矛盾，而是喂给了不同层。**

可以按这 4 层理解：

```text
ChatModel 层       直接喂消息
PromptTemplate 层  喂变量，让模板生成消息
Chain/Runnable 层  喂字典，给链上的每一步用
LangGraph/Agent 层 喂状态 State，比如 {"messages": [...]}
```

---

## 1. 最底层：ChatModel 直接吃 messages

比如你直接调用模型：

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="glm-4", api_key=zai_key, base_url=zai_url)

res = llm.invoke([
    ("human", "你好")
])

print(res.content)
```

这里的：

```python
[
    ("human", "你好")
]
```

本质是 **消息列表**。

LangChain 允许消息用多种等价写法表示。官方文档里也说明，Message 是 LangChain 中表示对话上下文的基本单位；`ChatPromptTemplate.from_messages` 也支持 `(message type, template)` 这种二元组格式。([LangChain 文档][1])

下面这些写法本质接近：

```python
from langchain_core.messages import HumanMessage

llm.invoke([
    HumanMessage(content="你好")
])
```

等价于：

```python
llm.invoke([
    ("human", "你好")
])
```

也接近于：

```python
llm.invoke([
    {"role": "user", "content": "你好"}
])
```

只是不同地方对格式支持程度略有差异。

推荐你记住：

```python
[("human", "xxx")]
```

常见于 **直接调用 ChatModel** 或 **构造 PromptTemplate**。

---

## 2. PromptTemplate 层：`from_messages` 里的 tuple 不是最终输入，而是模板

比如：

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}"),
    ("human", "请解释：{question}")
])

messages = prompt.invoke({
    "role": "AI老师",
    "question": "LangChain是什么？"
})
```

这里的：

```python
[
    ("system", "你是一个{role}"),
    ("human", "请解释：{question}")
]
```

不是用户输入，而是 **提示词模板结构**。

真正的输入是：

```python
{
    "role": "AI老师",
    "question": "LangChain是什么？"
}
```

所以这一层经常长这样：

```python
chain = prompt | llm

res = chain.invoke({
    "role": "AI老师",
    "question": "LangChain是什么？"
})
```

这里为什么必须传字典？

因为模板里有变量：

```python
{role}
{question}
```

LangChain 要用这个字典去填坑。

---

## 3. `MessagesPlaceholder`：把历史消息插进模板

如果你要带历史记录，常见写法是：

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有帮助的助手"),
    MessagesPlaceholder("history"),
    ("human", "{input}")
])
```

调用时：

```python
res = prompt.invoke({
    "history": [
        ("human", "我叫hero"),
        ("ai", "你好hero")
    ],
    "input": "我叫什么？"
})
```

这里注意：

```python
"history": [
    ("human", "我叫hero"),
    ("ai", "你好hero")
]
```

是消息列表。

而外面整体：

```python
{
    "history": [...],
    "input": "我叫什么？"
}
```

是模板变量字典。

`MessagesPlaceholder` 的作用就是：某个变量本身已经是一组 messages，把它原样插进 Prompt 里。官方参考文档也说明，`MessagesPlaceholder` 假设变量本身已经是 messages 列表。([LangChain 参考文档][2])

---

## 4. Chain / Runnable 层：通常吃字典

LangChain 里很多东西都实现了 Runnable，比如：

```python
prompt | llm | parser
```

这就是一个 Runnable chain。

如果链条里有变量，通常这样输入：

```python
chain.invoke({
    "input": "你好",
    "language": "中文"
})
```

举个完整例子：

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个翻译助手，请翻译成{language}"),
    ("human", "{text}")
])

chain = prompt | llm | StrOutputParser()

res = chain.invoke({
    "language": "英文",
    "text": "牡丹花"
})
```

这里不能写成：

```python
chain.invoke([("human", "牡丹花")])
```

因为这个链的入口是 prompt，prompt 需要：

```python
language
text
```

也就是说：

```text
直接 llm.invoke(...)       可以喂 messages
prompt.invoke(...)         要喂模板变量
(prompt | llm).invoke(...) 也要喂模板变量
```

---

## 5. LangGraph / Agent 层：通常吃 State

到了 LangGraph 以后，输入就不再只是“给模型的一句话”了。

LangGraph 是状态图，它关心的是整个工作流的状态。官方介绍中也把 LangGraph 定位为用于构建、管理、部署长期运行、有状态 agent 的底层编排框架。([GitHub][3])

所以它常见输入是：

```python
{
    "messages": [
        {"role": "user", "content": "你好"}
    ]
}
```

或者：

```python
{
    "messages": [
        ("human", "你好")
    ]
}
```

比如你的 DeepAgent：

```python
agent.invoke({
    "messages": [
        {"role": "user", "content": "牡丹花用英文怎么说"}
    ]
})
```

这里的：

```python
{
    "messages": [...]
}
```

不是普通 prompt 变量，而是 **图的状态 State**。

可以理解为 LangGraph 的状态长这样：

```python
{
    "messages": 对话历史,
    "todos": 任务列表,
    "files": 文件,
    ...
}
```

DeepAgent 内部需要的不只是一句话，它要维护消息、工具调用、中间步骤、todo 等状态，所以外面要包一层：

```python
{"messages": [...]}
```

---

## 6. 那 `role: human` 和 `role: user` 到底有什么区别？

这俩你可以先这样记：

```text
LangChain 内部习惯：human / ai / system
OpenAI API 习惯：user / assistant / system
```

对应关系：

| LangChain | OpenAI 风格   | 含义    |
| --------- | ----------- | ----- |
| `human`   | `user`      | 用户消息  |
| `ai`      | `assistant` | 模型回复  |
| `system`  | `system`    | 系统提示词 |
| `tool`    | `tool`      | 工具结果  |

所以这些通常都能被 LangChain 转换：

```python
("human", "你好")
```

```python
{"role": "user", "content": "你好"}
```

```python
HumanMessage(content="你好")
```

但是我建议你在自己的项目里统一风格。

对你现在的 DeepAgent / LangGraph 项目，建议统一用：

```python
{"role": "user", "content": message}
{"role": "assistant", "content": reply}
```

因为这和 Gradio 的 `type="messages"` 更容易对接。

---

## 7. 你现在最容易混的两种写法

### 写法 A：直接问模型

```python
llm.invoke([
    ("human", "牡丹花用英文怎么说")
])
```

这是：

```text
ChatModel 输入
```

模型直接吃消息。

---

### 写法 B：问 Agent / Graph

```python
agent.invoke({
    "messages": [
        {"role": "user", "content": "牡丹花用英文怎么说"}
    ]
})
```

这是：

```text
LangGraph State 输入
```

Agent 不是直接模型，它是一张图，所以要传状态。

---

## 8. 为什么你的 DeepAgent 不能写成这样？

你原来 Gradio 里写过：

```python
agent.astream({
    "message": message
})
```

这个不对。

因为 DeepAgent 期待的是：

```python
{
    "messages": [...]
}
```

不是：

```python
{
    "message": "..."
}
```

`message` 是你自己随便起的字段名，但 DeepAgent 图里没有这个状态字段，所以它不知道该怎么用。

正确是：

```python
agent.astream({
    "messages": [
        {"role": "user", "content": message}
    ]
})
```

---

## 9. 最推荐你记这张表

| 场景                       | 输入格式                    | 示例                                                         |
| ------------------------ | ----------------------- | ---------------------------------------------------------- |
| 直接调用 ChatModel           | `list[messages]`        | `llm.invoke([("human", "你好")])`                            |
| 构造 ChatPromptTemplate    | `list[tuple]` 模板        | `ChatPromptTemplate.from_messages([("human", "{input}")])` |
| 调用 Prompt / Chain        | `dict` 变量               | `chain.invoke({"input": "你好"})`                            |
| 带历史的 Prompt              | `dict`，其中某个字段是 messages | `{"history": [...], "input": "你好"}`                        |
| 调用 LangGraph / Agent     | `dict` 状态               | `agent.invoke({"messages": [...]})`                        |
| Gradio `type="messages"` | `list[dict]` 历史         | `[{"role": "user", "content": "..."}]`                     |

---

## 10. 给你一个统一写法建议

你以后可以按这个原则写：

### 普通模型调用

```python
llm.invoke([
    {"role": "user", "content": "你好"}
])
```

### Prompt Chain

```python
chain.invoke({
    "input": "你好"
})
```

### Agent / LangGraph

```python
agent.invoke({
    "messages": [
        {"role": "user", "content": "你好"}
    ]
})
```

### Gradio 转 Agent

```python
def build_messages(message, history):
    messages = []

    for item in history:
        messages.append({
            "role": item["role"],
            "content": item["content"]
        })

    messages.append({
        "role": "user",
        "content": message
    })

    return messages
```

然后：

```python
inputs = {
    "messages": build_messages(message, history)
}
```

---

## 11. 你可以这样理解整个调用链

你的 Gradio + DeepAgent 实际流程是：

```text
Gradio 用户输入
    ↓
message = "牡丹花用英文怎么说"

转成 LangGraph State
    ↓
{
  "messages": [
    {"role": "user", "content": "牡丹花用英文怎么说"}
  ]
}

DeepAgent / LangGraph 运行
    ↓
内部调用 ChatModel
    ↓
ChatModel 看到 messages
    ↓
返回 AIMessage
    ↓
LangGraph 把 AIMessage 追加回 state["messages"]
```

所以：

```python
{"messages": [...]}
```

是给 **Agent/Graph** 的。

```python
[("human", "...")]
```

是给 **ChatModel 或 PromptTemplate** 的。

这就是核心区别。

[1]: https://docs.langchain.com/oss/python/langchain/messages?utm_source=chatgpt.com "Messages - Docs by LangChain"
[2]: https://reference.langchain.com/python/langchain-core/prompts/chat/MessagesPlaceholder?utm_source=chatgpt.com "MessagesPlaceholder | langchain_core"
[3]: https://github.com/langchain-ai/langgraph?utm_source=chatgpt.com "langchain-ai/langgraph: Build resilient language agents as ..."
