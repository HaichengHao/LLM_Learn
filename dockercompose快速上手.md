Docker Compose 是 Docker 官方提供的一个**用于定义和运行多容器应用的工具**。它通过一个 YAML 文件（通常是 `docker-compose.yml`）来配置你的应用服务，然后用一条命令就可以启动、停止或管理整个应用栈。

既然你已经会用 Docker，那理解 Compose 会非常快！

---

## 🧩 一、为什么需要 Docker Compose？

假设你有一个 Web 应用，包含：
- 一个前端（Nginx）
- 一个后端（Python Flask）
- 一个数据库（PostgreSQL）

不用 Compose 时，你需要：
```bash
docker run -d --name db postgres
docker run -d --name backend --link db my-flask-app
docker run -d --name frontend -p 80:80 --link backend nginx
```
还要手动处理网络、依赖、环境变量等，很麻烦。

**用 Docker Compose 后**，只需写一个 `docker-compose.yml`，然后：
```bash
docker compose up -d
```
全部服务自动启动，网络互通，依赖有序！

---

## 📄 二、基本结构：`docker-compose.yml`

```yaml
version: '3.8'  # 版本号（推荐 3.8 或更高）

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - api

  api:
    build: ./my-flask-app   # 或者用 image: my-flask-app
    environment:
      - DB_HOST=db
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: example
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:  # 声明一个命名卷
```

### 关键概念解释：

| 字段 | 说明 |
|------|------|
| `services` | 每个服务对应一个容器（如 db, api, web） |
| `image` / `build` | 使用现成镜像 or 从 Dockerfile 构建 |
| `ports` | 端口映射（宿主机:容器） |
| `environment` | 设置环境变量 |
| `depends_on` | 启动顺序依赖（注意：**不等待服务就绪**，只是先启动） |
| `volumes` | 挂载卷，持久化数据 |
| `networks` | 默认所有服务在同一个自定义网络中，可直接用服务名通信（如 `db` 就是数据库的 hostname） |

---

## ▶️ 三、常用命令

| 命令 | 作用 |
|------|------|
| `docker compose up` | 启动所有服务（前台运行） |
| `docker compose up -d` | 后台启动（detached） |
| `docker compose down` | 停止并删除容器、网络（**不会删卷！**） |
| `docker compose logs -f` | 查看日志（类似 `docker logs -f`） |
| `docker compose ps` | 查看服务状态 |
| `docker compose build` | 重新构建 `build` 指定的服务 |
| `docker compose restart api` | 重启某个服务 |

> 💡 注意：新版本 Docker（20+）已内置 `docker compose`（无空格），旧版是 `docker-compose`（带横杠）。建议用新命令。

---

## 🛠 四、实战小例子：Redis + Python 脚本

1. 创建目录：
```bash
mkdir myapp && cd myapp
```

2. 创建 `app.py`：
```python
import redis, time
r = redis.Redis(host='redis', port=6379)
while True:
    r.incr('hits')
    print("Hits:", r.get('hits'))
    time.sleep(2)
```

3. 创建 `Dockerfile`：
```dockerfile
FROM python:3.9
RUN pip install redis
COPY app.py .
CMD ["python", "app.py"]
```

4. 创建 `docker-compose.yml`：
```yaml
version: '3.8'
services:
  redis:
    image: redis:alpine
  app:
    build: .
    depends_on:
      - redis
```

5. 运行：
```bash
docker compose up --build
```

你会看到 Python 脚本每 2 秒打印一次计数，且能成功连接 `redis` 服务（因为它们在同一个网络，`host='redis'` 就是 Redis 容器的 hostname）。

---

## ✅ 五、最佳实践建议

1. **不要用 `depends_on` 等待服务就绪**  
   它只控制启动顺序，不保证服务“可用”。如果后端依赖数据库，应在代码中加重试逻辑。

2. **用 `.env` 文件管理敏感配置**  
   ```yaml
   environment:
     - DB_PASSWORD=${DB_PASS}
   ```
   然后创建 `.env` 文件（**不要提交到 Git**）：
   ```
   DB_PASS=secret123
   ```

3. **开发 vs 生产配置分离**  
   可以用多个 compose 文件：
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml up
   ```

4. **清理资源**  
   `docker compose down` 不会删 volume，如需彻底清理：
   ```bash
   docker compose down -v  # -v 删除声明的卷
   ```

---

## 📚 六、学习资源

- 官方文档：https://docs.docker.com/compose/
- 示例库：https://github.com/docker/awesome-compose

---

如果你有具体的项目场景（比如“我想把我的 Flask + MySQL 项目容器化”），我可以帮你写一个完整的 `docker-compose.yml`！