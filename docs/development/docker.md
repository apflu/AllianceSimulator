# Docker 运行方式

Compose 是 MVP 的标准运行方式。PostgreSQL、迁移、HTTP API、Worker 和聊天平台入口均使用容器，
主机无需安装 Python 或 uv。

## 服务

| 服务 | 默认启动 | 用途 |
|---|---:|---|
| `postgres` | 是 | PostgreSQL 17 权威存储 |
| `migrate` | 是 | 等待数据库健康后执行 Alembic 迁移并退出 |
| `api` | 是 | HTTP 健康检查与未来 Web 入口 |
| `worker` | 是 | 结算到期行动并投递通知 |
| `telegram` | 否 | Telegram 长轮询入口，使用 `telegram` profile |
| `discord` | 否 | Discord gateway 入口，使用 `discord` profile |
| `postgres-test` | 否 | 仅供质量 profile 使用的临时 PostgreSQL |
| `quality` | 否 | 格式、静态检查和测试所需的开发镜像 |

`api`、`worker` 和两个 Bot 共用同一个本地应用镜像。应用容器以非 root 用户运行，数据库迁移成功后
才会启动长期进程。API 只发布到主机的 `127.0.0.1:8000`。

## 首次启动

从模板创建本地配置并填写需要的平台 token；不要把 `.env` 提交到仓库：

```powershell
Copy-Item .env.example .env
docker compose up -d --build --wait
```

默认命令会启动数据库、迁移、API 和 Worker。检查 API：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health/ready
```

迁移容器正常退出是预期行为。查看状态和去除敏感信息后的日志：

```powershell
docker compose ps
docker compose logs api worker
```

## 启动聊天入口

Telegram：

```powershell
docker compose --profile telegram up -d --build --wait
```

Discord：

```powershell
docker compose --profile discord up -d --build --wait
```

同时启动两个平台：

```powershell
docker compose --profile telegram --profile discord up -d --build --wait
```

若当前网络需要代理，容器不能用 `127.0.0.1` 访问 Windows 主机上的代理。将共享的
`ASIM_PROXY_URL` 设置为 Docker 容器可访问的 HTTP 地址，例如
`http://host.docker.internal:7897`。Discord Gateway、Telegram 轮询以及两个平台的主动通知都会
使用该地址。省略 `http://` 时配置层会自动补齐；非 HTTP scheme 会在进程启动时被拒绝。

## 停止与存档

```powershell
docker compose --profile telegram --profile discord down
```

上述命令保留 `postgres-data` volume。只有明确决定删除本地存档时才使用 `down --volumes`。

修改 Python 依赖或应用代码后重新运行带 `--build` 的启动命令。`uv.lock` 决定镜像中的依赖版本，
构建会在 lock 文件与项目声明不一致时失败。

## 质量检查

质量检查也在容器中运行，并会使用独立的临时 PostgreSQL 执行数据库专属测试：

```powershell
docker compose --profile quality build quality
docker compose --profile quality run --rm quality uv run --no-sync ruff format --check .
docker compose --profile quality run --rm quality uv run --no-sync ruff check .
docker compose --profile quality run --rm quality uv run --no-sync pyright
docker compose --profile quality run --rm quality
```

最后一个命令使用质量镜像的默认命令运行全部 pytest 测试。质量 profile 不连接玩家存档数据库；
`postgres-test` 使用临时文件系统，容器删除时测试数据一并消失，`postgres-data` volume 不受影响。
