# Alliance Simulator

一个受 EVE Online 启发、以 Discord 和 Telegram 为首要交互界面的异步联盟经营游戏。

本仓库是全新实现。旧仓库 `D:\\workspace\\AllianceSimulator` 只作为需求和设计意图的参考，不复制其类结构或运行机制。

## 当前状态

MVP 功能实现与自动化验证已经完成，真实 Telegram Bot 冒烟已通过；当前等待 Discord
测试服务器的最终冒烟验收。已经确定：

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
测试服务器完成剩余验收；自动化与 Telegram 实测证据见
[MVP 验证报告](docs/milestones/verification.md)。

## Docker 启动

需要 Docker Desktop。复制本地配置后，可用 Compose 启动 PostgreSQL、数据库迁移、API 和 Worker；
主机不需要安装 Python 或 uv：

```powershell
Copy-Item .env.example .env
docker compose up -d --build --wait
```

按需启用聊天平台入口：

```powershell
docker compose --profile telegram up -d --build --wait
docker compose --profile discord up -d --build --wait
```

完整说明见 [Docker 运行方式](docs/development/docker.md)。密钥和本地 `.env` 不应提交；
容器内数据库地址由 Compose 设置。

## Docker 质量检查

质量镜像包含锁定的开发依赖和测试，不要求主机安装 Python：

```powershell
docker compose --profile quality build quality
docker compose --profile quality run --rm quality uv run --no-sync ruff format --check .
docker compose --profile quality run --rm quality uv run --no-sync ruff check .
docker compose --profile quality run --rm quality uv run --no-sync pyright
docker compose --profile quality run --rm quality
```

Discord Bot 需要 `ASIM_DISCORD_TOKEN`；开发时可以设置 `ASIM_DISCORD_GUILD_ID`，以便命令立即同步到测试服务器。
Telegram Bot 需要 `ASIM_TELEGRAM_TOKEN`。
无法直连 Telegram API 时，可以设置 `ASIM_TELEGRAM_PROXY_URL`；容器中的轮询与主动通知会共用该代理。

两个聊天平台提供相同的玩家命令：

- `/start <联盟名称>`：建立联盟；
- `/status`：查看成员、舰船、库存、技能和当前行动；
- `/mine`：开始采矿；
- `/train`：训练采矿技能；
- `/events`：查看并处理联盟事件。
