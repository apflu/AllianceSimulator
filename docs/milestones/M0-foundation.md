# M0：工程基础

状态：完成（2026-07-30）

## 目标

建立一个可安装、可测试、可迁移数据库并能启动应用与 Worker 的最小 Python 工程，为 M1 提供稳定地基。本里程碑不实现完整游戏玩法。

## 交付内容

- 使用 `src` 布局创建 `alliancesim` 包；
- 使用 uv 创建 `pyproject.toml` 和锁文件，固定 Python 与依赖版本；
- 配置 Ruff、Pyright 和 pytest；
- 建立 `domain`、`application`、`adapters`、`bootstrap` 模块边界；
- 定义类型化配置并从环境变量读取；
- 提供 FastAPI 存活与就绪检查；
- 建立 SQLAlchemy 会话、Alembic 和初始迁移；
- 建立 Player、PlatformIdentity、Alliance 的最小持久化模型；
- 提供应用进程和 Worker 进程的启动命令；
- 建立结构化日志和关联 ID；
- 提供本地 PostgreSQL 启动说明；
- CI 或等价本地检查一次运行格式、静态检查和测试。

## 验收标准

1. 新环境依据 README 可以安装依赖并执行所有检查。
2. 空 PostgreSQL 可以升级到最新迁移，也能降级并重新升级。
3. 应用健康检查区分“进程存活”和“数据库就绪”。
4. Worker 在没有任务时可以安全运行和停止。
5. 单元测试不需要网络或真实平台 token。
6. `domain` 不依赖 SQLAlchemy、FastAPI、discord.py 或 aiogram。
7. 仓库没有提交密钥、本地数据库和生成缓存。

## 明确不做

- Discord 或 Telegram 的真实命令；
- 采矿结算；
- 通用依赖注入框架；
- Redis、Celery、Kubernetes 或微服务。

## 完成后下一步

直接进入 M1，以 Discord 交付第一条端到端玩法；不要先建设通用事件引擎或完整舰船模型。
