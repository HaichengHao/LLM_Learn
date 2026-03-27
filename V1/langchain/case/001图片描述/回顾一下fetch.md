当然可以！`fetch` 是现代浏览器原生提供的用于发起网络请求的 API，相比 `axios` 更轻量（不需要额外安装），但功能略基础一些。下面是一些常见的 `fetch` 用法示例，帮助你从 `axios` 过渡到 `fetch`。

---

### 1. 基本 GET 请求

**axios 写法：**
```js
axios.get('/api/data')
  .then(res => console.log(res.data))
  .catch(err => console.error(err));
```

**fetch 写法：**
```js
fetch('/api/data')
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json(); // 解析 JSON
  })
  .then(data => console.log(data))
  .catch(err => console.error('Fetch error:', err));
```

> ⚠️ 注意：`fetch` 不会自动 reject HTTP 错误状态（如 404、500），需要手动检查 `response.ok`。

---

### 2. POST 请求（带 JSON 数据）

**axios 写法：**
```js
axios.post('/api/user', { name: 'Alice' })
  .then(res => console.log(res.data));
```

**fetch 写法：**
```js
fetch('/api/user', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ name: 'Alice' })
})
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error(err));
```

---

### 3. 设置请求头（Headers）

```js
fetch('/api/secure', {
  headers: {
    'Authorization': 'Bearer your-token-here',
    'Content-Type': 'application/json'
  }
})
  .then(res => res.json())
  .then(data => console.log(data));
```

---

### 4. 处理错误（更健壮的方式）

```js
async function fetchData() {
  try {
    const response = await fetch('/api/data');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log(data);
  } catch (error) {
    console.error('Error fetching data:', error);
  }
}

fetchData();
```

---

### 5. 与 axios 的主要区别

| 特性 | axios | fetch |
|------|-------|--------|
| 自动转换 JSON | ✅ `res.data` | ❌ 需要 `res.json()` |
| 自动处理 HTTP 错误 | ✅ 会 reject | ❌ 需手动检查 `response.ok` |
| 浏览器兼容性 | 需要 polyfill（旧浏览器）| 现代浏览器支持（IE 不支持）|
| 拦截器（interceptors）| ✅ 支持 | ❌ 原生不支持（需封装）|
| 取消请求 | ✅ 支持（CancelToken / AbortController）| ✅ 通过 `AbortController` |

---

### 小技巧：封装一个简单的 fetch 工具函数

如果你觉得重复写 `.then(res => res.json())` 很麻烦，可以简单封装：

```js
function apiFetch(url, options = {}) {
  return fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  })
    .then(res => {
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      return res.json();
    });
}

// 使用
apiFetch('/api/data')
  .then(data => console.log(data))
  .catch(err => console.error(err));
```

---

如果你有具体的 `axios` 代码想转成 `fetch`，也可以贴出来，我可以帮你改写！