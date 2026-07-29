# MVP 验证报告

- 验证日期：2026-07-30
- 分支：`python-rewrite`
- 状态：实现与自动化验证完成；真实 Discord/Telegram 冒烟待执行

## 已取得的证据

### 本地全量质量门槛

- `ruff format --check`：通过；
- `ruff check`：通过；
- `pyright` 严格模式：0 错误、0 警告；
- 无外部平台和 PostgreSQL 时：37 项测试通过，2 项 PostgreSQL 专属测试按条件跳过；
- API 进程实际启动，`/health/live` 返回 HTTP 200 和 `x-request-id`。

### 真实 PostgreSQL 17.9

使用仅监听 `127.0.0.1` 的便携 PostgreSQL 执行并通过：

1. 从空数据库升级到 Alembic head；
2. 降级到 base 后再次完整升级；
3. 两个独立 Worker 同时认领同一到期采矿行动；
4. 最终只有一个 Worker 完成结算，联盟库存只增加一次 100 `raw-ore`。

便携数据库已在验证后停止并清理。CI 使用 PostgreSQL 17 service 重复执行相同门槛。

### 完整玩家旅程

`tests/e2e/test_mvp_journey.py` 从平台无关聊天命令开始，在不手工修改数据库的情况下验证：

1. 建立联盟并获得初始成员与舰船；
2. 查看空库存；
3. 开始并完成采矿；
4. Worker 结算、写入库存并投递通知；
5. 处理首次采矿触发的联盟事件；
6. 开始并完成技能训练；
7. 后续采矿产量由 100 提升到 110；
8. 最终状态、库存和技能均可查询。

### 关键不变量

- 重复创建联盟和重复开始行动不会创建第二份状态；
- 服务重启后采矿和训练仍可结算；
- 行动只结算一次；
- 通知失败后按退避策略重试；
- 事件选项重复点击不会重复发放资源；
- 事件超时只应用一次默认结果；
- Discord 与 Telegram 调用同一应用用例并产生等价领域状态；
- `domain` 不导入 FastAPI、SQLAlchemy、discord.py 或 aiogram。

## 尚缺的外部验证

自动化测试不能证明真实 Bot token、平台权限、命令同步和私信策略均已正确配置。以下两项仍需在测试环境执行：

- Discord 测试服务器完成 `/start → /status → /mine → /events → /train`；
- Telegram 私聊完成同一流程，并验证 inline keyboard 回调和主动通知。

执行步骤见[平台冒烟测试](../development/platform-smoke-test.md)。完成并记录结果后，才能把 MVP 状态改为“全部验收完成”。
