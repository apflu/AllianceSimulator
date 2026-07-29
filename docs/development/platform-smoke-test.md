# Discord 与 Telegram 冒烟测试

## 准备

1. 启动 PostgreSQL，并执行 `uv run alembic upgrade head`。
2. 从 `.env.example` 创建本地 `.env`，填写测试 Bot token。
3. Discord Bot 需要 application command 和向测试用户发送私信的权限；建议配置 `ASIM_DISCORD_GUILD_ID` 加速命令同步。
4. Telegram Bot 应允许与测试账号私聊。
5. 分别启动 `alliancesim-worker`、`alliancesim-discord` 和 `alliancesim-telegram`。

token 只能放在本地环境或密钥系统中，不提交到仓库，也不粘贴到测试报告。

## Discord

- [ ] `/start <联盟名称>` 创建联盟；重复原交互不会生成第二个联盟。
- [ ] `/status` 展示初始成员、Pioneer、空库存和空闲状态。
- [ ] `/mine` 展示完成时间和 100 预计产量。
- [ ] 到期后收到私信通知，`/status` 展示 100 `raw-ore`。
- [ ] `/events` 展示“异常矿石样本”和两个按钮。
- [ ] 点击按钮后得到对应资源；再次点击不会重复发放。
- [ ] `/train` 完成后收到通知，状态显示 `mining-operations: 1`。
- [ ] 下一次 `/mine` 展示 110 预计产量。

## Telegram

- [ ] `/start <联盟名称>`、`/status` 和 `/mine` 产生与 Discord 等价的游戏状态。
- [ ] 到期后收到主动消息。
- [ ] `/events` 返回 inline keyboard，回调可以成功解决事件。
- [ ] 重复回调不会重复发放资源。
- [ ] `/train` 完成后，后续采矿产量提升到 110。

## 记录

完成后在 [MVP 验证报告](../milestones/verification.md) 中填写日期、测试平台和结果，不记录 token、用户 ID、服务器 ID 或聊天 ID。若平台测试失败，应记录可复现的命令、响应类别和日志关联 ID。
