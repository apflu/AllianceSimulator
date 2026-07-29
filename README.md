# Alliance Simulator

一个受 EVE Online 启发、以 Discord 和 Telegram 为首要交互界面的异步联盟经营游戏。

本仓库是全新实现。旧仓库 `D:\\workspace\\AllianceSimulator` 只作为需求和设计意图的参考，不复制其类结构或运行机制。

## 当前状态

MVP 功能实现与自动化验证已经完成，等待真实 Discord 和 Telegram 测试 Bot 的最终冒烟验收。已经确定：

- 权威后端使用 Python；
- PostgreSQL 是游戏状态的唯一事实来源；
- Discord、Telegram 和未来 Web 都是可替换的入口适配器；
- 采矿、训练等长期行动以数据库中的截止时间表示，不依赖常驻 `sleep()`；
- 先交付一条可玩的采矿纵向切片，再扩展完整内容。

## 文档入口

- [文档索引](docs/README.md)
- [产品愿景](docs/product/vision.md)
- [MVP 范围](docs/product/mvp-scope.md)
- [总体架构](docs/architecture/overview.md)
- [领域模型](docs/architecture/domain-model.md)
- [里程碑路线图](docs/milestones/README.md)

下一项工作是按[平台冒烟测试](docs/development/platform-smoke-test.md)在真实 Discord
测试服务器和 Telegram 私聊中完成最终验收；自动化范围与现有证据见
[MVP 验证报告](docs/milestones/verification.md)。

## 本地开发

需要 Python 3.13+、uv 和 PostgreSQL。仓库提供的 `compose.yaml` 可用于启动本地数据库：

```powershell
docker compose up -d postgres
Copy-Item .env.example .env
uv sync
uv run alembic upgrade head
```

启动 HTTP 健康检查和 Worker：

```powershell
uv run alliancesim-api
uv run alliancesim-discord
uv run alliancesim-telegram
uv run alliancesim-worker
```

运行全部本地质量检查：

```powershell
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
```

密钥和本地 `.env` 不应提交。数据库连接默认读取 `ASIM_DATABASE_URL`。
Discord Bot 需要 `ASIM_DISCORD_TOKEN`；开发时可以设置 `ASIM_DISCORD_GUILD_ID`，以便命令立即同步到测试服务器。
Telegram Bot 需要 `ASIM_TELEGRAM_TOKEN`。
无法直连 Telegram API 时，可以设置 `ASIM_TELEGRAM_PROXY_URL`；轮询与主动通知会共用该代理。

两个聊天平台提供相同的玩家命令：

- `/start <联盟名称>`：建立联盟；
- `/status`：查看成员、舰船、库存、技能和当前行动；
- `/mine`：开始采矿；
- `/train`：训练采矿技能；
- `/events`：查看并处理联盟事件。
