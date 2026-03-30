你提出的问题非常关键，涉及到 Python 装饰器（decorator）的调用方式以及 `@tool` 装饰器在 LangChain / Gradio MCP 中的具体实现机制。

---

### 🔍 问题核心：
> **为什么 `@tool()`（带括号）能正确注册函数名为 `'calc_expo'`，而 `@tool`（不带括号）却显示为 `'decorator'`？**

---

### ✅ 正确写法：`@tool()`
```python
@tool()
def calc_expo(base: int, exponent: int):
    return base ** exponent
```

此时 `calc_expo` 是一个经过 `tool()` 调用后返回的 **可调用对象（通常是 `BaseTool` 的子类实例）**，其内部会保留原始函数的 `__name__`、`__doc__` 等元信息，并显式设置工具名称为 `'calc_expo'`。

---

### ❌ 错误写法：`@tool`
```python
@tool
def calc_expo(base: int, exponent: int):
    return base ** exponent
```

这里 `@tool` 相当于把 `calc_expo` 函数直接传给 `tool` 本身（而不是 `tool()` 的返回值）。如果 `tool` 是一个**工厂函数或类**，那么 `@tool` 会导致：

- `tool(calc_expo)` 被调用；
- 但若 `tool` 的设计是 **必须通过 `tool()` 先配置参数（即使无参）再装饰**，那么直接 `@tool` 就会出错或行为异常。

在你的场景中，`tool` 很可能是一个 **返回装饰器的函数**（即“装饰器工厂”），例如：

```python
def tool(**kwargs):
    def decorator(func):
        # 创建 BaseTool 实例，使用 func.__name__ 作为 name
        return MyTool(name=func.__name__, func=func, ...)
    return decorator
```

所以：
- `@tool()` → 调用 `tool()` 返回 `decorator`，再用它装饰函数 → ✅ 正确获取函数名；
- `@tool` → 把函数传给 `tool` 本身（而非 `decorator`），相当于 `tool(calc_expo)`，而 `tool` 可能没设计成直接接受函数 → ❌ 返回一个无意义的对象，`name` 变成 `'decorator'` 或其他默认值。

---

### 🧪 验证：查看类型
你可以加一行打印：

```python
print(type(calc_expo))
```

- 用 `@tool()`：输出类似 `<class 'langchain_core.tools.tool.Tool'>` 或自定义 Tool 类；
- 用 `@tool`：可能输出 `<function decorator at 0x...>` 或一个未正确初始化的包装器。

---

### 💡 总结

| 写法       | 含义                          | 是否推荐 | 工具名是否正确 |
|------------|-------------------------------|--------|----------------|
| `@tool()`  | 调用 tool 工厂，返回装饰器     | ✅ 是   | ✅ 是 (`calc_expo`) |
| `@tool`    | 把函数传给 tool 本身           | ❌ 否   | ❌ 否 (`decorator`) |

> **因此，必须加 `()`，即使没有参数！**  
> 这是很多基于装饰器的工具库（如 FastAPI、LangChain Tools、Gradio MCP）的通用规范。

---

### 📚 补充：LangChain 官方示例
LangChain 的 `@tool` 装饰器也要求带括号：
```python
from langchain_core.tools import tool

@tool
def search(query: str) -> str:  # ← 注意：LangChain 的 @tool 可以不带括号！
    ...
```

⚠️ 但注意：**Gradio MCP 的 `@tool` 和 LangChain 的 `@tool` 是两个不同的实现！**

你代码中导入的是：
```python
from gradio.mcp import tool
```

而 Gradio MCP 的 `@tool` **必须带括号**，这是它的 API 设计决定的。

---

### ✅ 最佳实践
始终查阅你所用库的文档。对于 **Gradio MCP 的 `tool`**，请坚持使用：
```python
@tool()
def your_function(...):
    ...
```

这样就能确保 `tool_calls[0]['name'] == 'your_function'`。