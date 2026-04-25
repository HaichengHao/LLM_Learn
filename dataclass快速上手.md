在 Python 中，`@dataclass` 是一个非常实用的装饰器（自 3.7 起内置），用于简化以**存储数据为主**的类的定义。它能自动生成 `__init__`、`__repr__`、`__eq__` 等方法。

你老师说“实际生产开发中用得最多的是 `@dataclass`”，这确实很常见——尤其是在处理配置、模型、DTO（数据传输对象）等场景时。

下面我来系统地教你 **如何在 `@dataclass` 中使用继承、类属性、实例属性等操作**。

---

## ✅ 一、基础：`@dataclass` 定义类

```python
from dataclasses import dataclass

@dataclass
class Person:
    name: str      # 实例属性（字段）
    age: int = 0   # 带默认值的实例属性
```

等价于手动写：

```python
class Person:
    def __init__(self, name: str, age: int = 0):
        self.name = name
        self.age = age

    def __repr__(self):
        return f"Person(name={self.name!r}, age={self.age})"

    def __eq__(self, other):
        return isinstance(other, Person) and (self.name, self.age) == (other.name, other.age)
```

---

## ✅ 二、继承（Inheritance）

### ✔ 规则：
- **父类和子类都必须用 `@dataclass` 装饰**
- **子类字段不能出现在父类字段之前**（否则会报错）
- 子类自动继承父类的所有字段，并按顺序排列

### 🌰 示例：

```python
from dataclasses import dataclass

@dataclass
class Animal:
    species: str
    legs: int = 4

@dataclass
class Dog(Animal):  # 继承 Animal
    breed: str       # 新增字段（必须放在父类字段之后！）
    name: str = "Unnamed"
```

✅ 合法用法：

```python
d = Dog(species="Canis lupus", breed="Golden Retriever", name="Buddy")
print(d)
# 输出: Dog(species='Canis lupus', legs=4, breed='Golden Retriever', name='Buddy')
```

### ❌ 错误示例（字段顺序错误）：

```python
@dataclass
class BadDog(Animal):
    name: str = "Unnamed"  # ❌ 错！name 在 breed 之前，但 breed 是父类字段？
    breed: str             # 这会导致 TypeError: non-default argument follows default argument
```

> 💡 **原因**：`dataclass` 会把所有字段合并后生成 `__init__`，而 Python 要求**带默认值的参数必须在无默认值参数之后**。由于父类字段可能有默认值，子类新增的无默认值字段如果放在前面，就会违反这个规则。

---

## ✅ 三、类属性（Class Attributes）

`@dataclass` **只处理实例属性（字段）**，不会把类属性当作字段处理。

### 🌰 正确写法：

```python
@dataclass
class Config:
    host: str
    port: int

    # 类属性（不会被 dataclass 当作字段）
    VERSION = "1.0"
    DEFAULT_TIMEOUT = 30
```

使用：

```python
c = Config("localhost", 8080)
print(c.VERSION)           # ✅ 可以访问
print(Config.VERSION)      # ✅ 也可以通过类访问
```

> ⚠️ 注意：不要把类属性写成带类型注解但无默认值的形式（如 `version: str`），否则 `dataclass` 会把它当作**实例字段**！

---

## ✅ 四、重写方法（如 `__post_init__`）

如果你需要在初始化后做额外处理，可以用 `__post_init__`：

```python
@dataclass
class Circle:
    radius: float

    def __post_init__(self):
        if self.radius < 0:
            raise ValueError("Radius cannot be negative")
```

---

## ✅ 五、抽象基类 + dataclass（高级用法）

虽然不常用，但你可以结合 `ABC` 和 `@dataclass`：

```python
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Shape(ABC):
    color: str

    @abstractmethod
    def area(self) -> float:
        pass

@dataclass
class Rectangle(Shape):
    width: float
    height: float

    def area(self) -> float:
        return self.width * self.height
```

> ✅ 注意：父类 `Shape` 也用了 `@dataclass`，所以子类能正确继承 `color` 字段。

---

## 🔚 总结

| 功能 | 写法 |
|------|------|
| 实例属性 | 直接写 `name: str` |
| 默认值 | `age: int = 0` |
| 继承 | 父类和子类都加 `@dataclass`，子类字段放后面 |
| 类属性 | 写在字段之外，**不要加类型注解**（或用 `ClassVar`） |
| 初始化后处理 | 用 `__post_init__` |
| 抽象类 | 可与 `ABC` 结合，但父类也要 `@dataclass` |

> 💡 补充：如果想明确表示某个带注解的变量是**类属性**而非字段，可用 `typing.ClassVar`：

```python
from typing import ClassVar

@dataclass
class Example:
    instance_field: str
    class_attr: ClassVar[str] = "I'm a class attribute"
```

这样 `dataclass` 就不会把它当作实例字段了。

---

如有具体场景（比如多层继承、混合普通类和 dataclass 等），欢迎继续提问！