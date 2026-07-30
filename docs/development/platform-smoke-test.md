# Discord 与 Telegram 冒烟测试

## 准备

1. 从 `.env.example` 创建本地 `.env`，填写测试 Bot token。
2. 使用 Docker Compose 启动数据库、迁移、API、Worker 和待测 Bot：

   ```powershell
   docker compose --profile telegram up -d --build --wait
   docker compose --profile discord up -d --build --wait
   ```

   只执行当前要测试的平台命令；需要同时运行时可同时给出两个 profile。
3. Discord Guild Install 必须包含 `applications.commands` 和 `bot` scope，让 Bot 用户实际加入测试服务器；
   Bot Permissions 可以保持为 `0`。建议配置 `ASIM_DISCORD_GUILD_ID` 加速命令同步。
   当前主动通知只发送私信，不会同时写入执行命令的服务器频道。测试用户必须允许接收来自该服务器
   成员的私信；Discord 错误码 `50278` 表示 Bot 与用户没有共同服务器，`50007` 表示无法向该用户
   发送消息。
4. Telegram Bot 应允许与测试账号私聊。
   无法直连平台 API 时，在 `.env` 设置共享的 HTTP 代理 `ASIM_PROXY_URL`；容器访问 Windows
   主机代理时使用 `host.docker.internal`，不能使用容器自身的 `127.0.0.1`。
5. Discord 玩家测试开始前执行 `docker compose logs discord`，确认日志依次出现
   `discord_commands_synced` 和 `discord_bot_ready`；前者应显示 5 条命令。全局命令同步可能需要
   较长时间，测试服务器优先配置 `ASIM_DISCORD_GUILD_ID` 使用 guild scope。guild scope 启动时会
   同步空的 global command 集合，自动清理由同一应用先前注册的全局命令，避免命令重复。

token 只能放在本地环境或密钥系统中，不提交到仓库，也不粘贴到测试报告。

## Discord

- [ ] `/start <联盟名称>` 创建联盟；重复原交互不会生成第二个联盟。
- [ ] `/status` 展示初始成员、Pioneer、空库存和空闲状态。
- [ ] `/mine` 展示完成时间和 100 预计产量。
- [ ] 到期后收到私信通知，`/status` 展示 100 `raw-ore`。
- [ ] `/events` 展示“异常矿石样本”和两个按钮。
- [ ] 展示事件后重启 Discord Bot，旧按钮或重新执行 `/events` 后的按钮仍可处理该事件。
- [ ] 点击按钮后得到对应资源；再次点击不会重复发放。
- [ ] `/train` 完成后收到通知，状态显示 `mining-operations: 1`。
- [ ] 下一次 `/mine` 展示 110 预计产量。

## Telegram

- [x] `/start <联盟名称>`、`/status` 和 `/mine` 产生与 Discord 等价的游戏状态。
- [x] 到期后收到主动消息。
- [x] `/events` 返回 inline keyboard，回调可以成功解决事件。
- [x] 重复回调不会重复发放资源。
- [x] `/train` 完成后，后续采矿产量提升到 110。

## 记录

完成后在 [MVP 验证报告](../milestones/verification.md) 中填写日期、测试平台和结果，不记录 token、用户 ID、服务器 ID 或聊天 ID。若平台测试失败，应记录可复现的命令、响应类别和日志关联 ID。

- 2026-07-30：Telegram 全流程通过；玩家可见结果与 PostgreSQL 终态一致。
- 2026-07-30：Discord 真实 token 认证、5 条 global command 同步和 Gateway ready 通过；测试服务器
  玩家流程待执行。
