# MVP 验证报告

- 验证日期：2026-07-30
- 分支：`python-rewrite`
- 状态：MVP 全部验收完成；自动化与真实 Discord/Telegram 冒烟均通过

## 已取得的证据

### Docker 全量质量门槛

- `ruff format --check`：通过；
- `ruff check`：通过；
- `pyright` 严格模式：0 错误、0 警告；
- 独立临时 PostgreSQL 中：55 项测试全部通过，包含 3 项 PostgreSQL 专属测试；
- 无 PostgreSQL 时仍可运行核心套件：52 项通过，3 项数据库专属测试按条件跳过；
- 质量数据库使用临时文件系统，不连接或修改玩家存档；
- CI 除上述门槛外还校验 Compose 配置并构建运行镜像。

### 完整 Docker 运行栈

- 固定摘要的 Python 3.13/uv 基础镜像按 `uv.lock` 构建成功，运行镜像不包含开发依赖；
- Compose 等待 PostgreSQL 健康后执行 Alembic，迁移容器以退出码 0 结束；
- API 和 Worker 容器以非 root 用户运行，API `/health/ready` 返回 HTTP 200；
- Telegram 容器使用 `host.docker.internal` 访问 Windows 本地代理，真实 Bot 完成身份校验并进入轮询；
- 应用、Worker 和平台入口共用同一镜像，Discord/Telegram 通过 profile 按需启动；
- PostgreSQL `postgres-data` volume 在重建应用容器后保持，验收存档未被删除。

### 真实 PostgreSQL 17.9

使用仅监听 `127.0.0.1` 的便携 PostgreSQL 执行并通过：

1. 从空数据库升级到 Alembic head；
2. 降级到 base 后再次完整升级；
3. 含采矿、训练和通知历史的数据安全降级到不支持训练的旧结构，再升级到 head；
4. 两个独立 Worker 同时认领同一到期采矿行动；
5. 最终只有一个 Worker 完成结算，联盟库存只增加一次 100 `raw-ore`。

便携数据库已在验证后停止并清理。当前 Docker 质量 profile 使用独立 PostgreSQL 17 临时文件系统
重复执行相同门槛。

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

### 真实 Telegram Bot（2026-07-30）

使用 Docker PostgreSQL 17、真实 Telegram Bot 私聊和本地 HTTP 代理完成完整流程：

1. `/start` 创建联盟，`/status` 展示 New Capsuleer、Pioneer、空库存和空闲状态；
2. `/mine` 展示 100 预计产量，到期后主动通知首次投递成功；
3. `/events` 返回两个 inline keyboard 选项，选择 `analyze` 后获得 1 `research-data`；
4. 再次点击同一旧按钮未重复发放资源；
5. `/train` 完成后收到主动通知，状态显示 `mining-operations: 1`；
6. 后续 `/mine` 展示并结算 110 产量，最终库存为 210 `raw-ore` 和 1 `research-data`。

数据库终态确认三项行动均为 `completed`、没有活动行动，三条 outbox 通知均在首次尝试后为
`sent`。测试未记录 token、Telegram 用户 ID 或聊天 ID。

### 真实 Discord Bot 完整旅程（2026-07-30）

使用 Docker PostgreSQL 17、真实 Discord Bot、测试服务器和共享 HTTP 代理完成完整流程：

1. Discord REST 身份认证成功；
2. 5 条 MVP application command 以 guild scope 同步，Gateway 进入 ready；切换 scope 时会清理
   同一应用遗留的 global command，避免重复命令；
3. `/start`、`/status` 和 `/mine` 完成基础流程，基础采矿预计并结算 100；
4. Bot 以 `bot` scope 加入测试服务器后，采矿和训练完成私信均成功送达；Bot Permissions 保持为 0；
5. `/events` 展示事件按钮，重启 Bot 后点击重启前生成的旧按钮仍可获得 1 `research-data`；
6. 再次点击同一按钮返回已处理结果，数据库仍只有一个事件实例和 1 `research-data`；
7. `/train` 完成后状态显示 `mining-operations: 1`，后续 `/mine` 预计并结算 110。

首次 Guild Install 只包含 application command，Bot 未成为服务器成员，Discord 因没有共同服务器而
以 `50278` 拒绝私信。补充 `bot` scope 后，玩家手工开始了一次新的基础采矿来重试旅程，因此测试
存档包含两次独立的 100 采矿和一次训练后的 110 采矿，最终为 310 `raw-ore` 和 1
`research-data`。四项行动均为 `completed`，没有活动行动；修正安装后的两条采矿通知和一条训练
通知均为 `sent`，首次失败记录保留为可审计的 `failed` 终态。测试未记录 token、Bot ID、服务器
ID、用户 ID 或 Gateway session ID。

### 关键不变量

- 重复创建联盟和重复开始行动不会创建第二份状态；
- 服务重启后采矿和训练仍可结算；
- 行动只结算一次；
- 通知失败后按退避策略重试；
- 事件选项重复点击不会重复发放资源；
- 事件超时只应用一次默认结果；
- Discord 与 Telegram 调用同一应用用例并产生等价领域状态；
- `domain` 不导入 FastAPI、SQLAlchemy、discord.py 或 aiogram。

### 可靠性与平台边界

- Discord slash command 在访问数据库前确认 interaction，避免超过平台响应时限；
- Discord 在命令同步和 Gateway ready 后分别写入可机器检索的结构化启动事件；
- Discord 事件按钮使用动态持久化组件，Bot 重启后仍可根据稳定 `custom_id` 重建路由；
- Telegram callback 在处理领域命令前先向平台确认；
- Discord 与 Telegram 命令均绑定结构化 `request_id`、平台和命令结果；
- 平台 API 错误在持久化前脱敏，Telegram URL 中的 token 不会进入错误字段或日志；
- 通知采用指数退避，连续 10 次失败后进入可审计的 `failed` 终态；
- Worker 单次轮询失败后继续运行，并记录行动完成、通知成功、重试与最终失败。

## MVP 范围逐项审计

| 文档要求 | 权威证据 | 结论 |
|---|---|---|
| 平台身份映射到内部玩家 | `20260730_0001_identity.py` 的唯一身份约束；`test_full_mining_lifecycle_is_idempotent_and_persistent` | 通过 |
| 幂等创建联盟 | 同一平台身份重复创建返回既有联盟；集成测试覆盖 | 通过 |
| 初始角色、舰船和采矿模块 | `create_alliance` 同事务创建成员与 Pioneer；完整旅程验证可直接采矿 | 通过 |
| 状态与库存查询 | `get_status` 与 `/status` 展示模型；完整旅程验证空库存和结算后库存 | 通过 |
| 固定地点和材料 | 稳定内容 ID `calm-asteroid-belt`、`raw-ore`；行动冻结地点、材料和规则版本 | 通过 |
| 采矿开始、到期结算和查询 | 领域规划、持久化行动、Worker 结算及端到端旅程 | 通过 |
| 重启后结算逾期行动 | 关闭并重建数据库适配器后的结算与状态测试 | 通过 |
| 事务性通知发件箱和安全重试 | 行动与 outbox 同事务；租约认领、退避、终止状态及发送器测试 | 通过 |
| Discord 入口 | 五个 slash command、component、handler、渲染契约测试及真实完整旅程 | 通过 |
| Telegram 对等入口 | 五个 command、inline keyboard、callback、通知、对等状态测试及真实 Bot 完整旅程 | 通过 |
| 联盟事件及明确结果 | 唯一触发、内容快照、幂等选项、24 小时默认结果测试 | 通过 |
| 单元、集成和适配器契约测试 | Docker 中 55 项测试全部通过，包含 3 项 PostgreSQL 专属测试 | 通过 |

### MVP 指标审计

| 指标 | 证据 | 结论 |
|---|---|---|
| 重复平台交互不重复发放资源 | 行动唯一幂等键、事件解析幂等测试 | 通过 |
| 停服重启后最终且仅结算一次 | 重启集成测试与真实 PostgreSQL 双 Worker 测试 | 通过 |
| 两个平台产生等价领域结果 | 平台对等集成测试、共用 `GameService`/`ChatCommandAdapter` 与双平台真实旅程 | 通过 |
| 核心测试无需平台 API | 全量本地测试使用 fake/mock sender 和平台对象 | 通过 |
| 首次采矿无需修改数据库 | `test_player_completes_mvp_journey_without_database_edits` | 通过 |

## 外部验证结论

Telegram 的真实 token、代理、轮询、私聊、inline keyboard 和主动通知，以及 Discord 的真实 token、
代理、guild command、Gateway、私信和重启后动态按钮均已验证。MVP 没有剩余的外部验收项；下一阶段
可以进入 M4 的范围细化，不需要继续扩展当前冒烟存档。
