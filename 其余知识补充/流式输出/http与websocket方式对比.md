在 Python 的 FastAPI 框架中，**WebSocket 接口**和**常规 HTTP 接口（RESTful API）** 有本质区别，主要体现在通信模式、连接方式和适用场景上。以下是详细对比：

---

### 🔁 一、核心区别

| 维度 | 常规 HTTP 接口 | WebSocket 接口 |
|------|------------------|----------------|
| **通信模式** | 请求-响应（单向）：客户端发请求 → 服务端返回响应 → 连接关闭 | 全双工双向通信：连接建立后，双方可随时主动发送消息 |
| **连接生命周期** | 短连接（每次请求新建连接，响应后断开）（HTTP/1.1 可复用连接但仍是“伪长连”） | 长连接：一次握手后保持连接，直到主动关闭 |
| **协议基础** | 基于 HTTP/HTTPS | 基于 WebSocket 协议（通过 HTTP 升级请求建立） |
| **实时性** | 无实时能力，需轮询或长轮询模拟 | 原生支持实时双向通信 |
| **头部开销** | 每次请求带完整 HTTP 头（较大） | 连接建立后数据帧头很小（高效） |

---

### 🛠️ 二、FastAPI 中的代码示例对比

#### 1. 常规 HTTP 接口（REST）
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```
- 客户端调用一次，服务端返回一次，结束。

#### 2. WebSocket 接口
```python
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")
```
- 连接建立后，可无限次收发消息，直到 `disconnect()`。

---

### 🌐 三、为什么要有这两种？——使用场景差异

#### ✅ HTTP 接口适合：
- 获取静态资源（网页、图片、JSON 数据）
- 提交表单、上传文件
- 一次性操作（如登录、查询订单）
- 无状态、低频交互场景

#### ✅ WebSocket 适合：
- **实时聊天应用**（如微信网页版）
- **在线协作工具**（如 Google Docs 实时编辑）
- **金融行情推送**（股票价格实时更新）
- **多人在线游戏**（玩家位置同步）
- **IoT 设备监控**（传感器数据持续上报）
- **通知系统**（服务端主动推送消息）

> 💡 关键点：**当需要服务端主动“推”数据给客户端，或要求毫秒级响应时，WebSocket 是更优解。**

---

### ⚠️ 四、注意事项
- WebSocket 虽好，但会占用更多服务器内存（每个连接需维持状态）
- 不适合高并发但低活跃度的场景（可用 Server-Sent Events 替代）
- 需处理连接异常、心跳保活、认证等问题

---

### 总结
> **HTTP 是“打电话问事”，WebSocket 是“开着对讲机聊天”**。  
> FastAPI 同时支持两者，开发者应根据业务是否需要**实时双向通信**来选择合适的技术方案。