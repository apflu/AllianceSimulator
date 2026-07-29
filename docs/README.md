# 文档索引

这里记录项目的产品边界、领域语言、架构决策和交付计划。实现与文档冲突时，应先确认真实意图，再同步修改对应文档；不能让两者长期分叉。

## 产品

- [产品愿景](product/vision.md)：我们在做什么，以及刻意不做什么。
- [MVP 范围](product/mvp-scope.md)：首个可玩版本包含和不包含的内容。
- [平台身份与账号策略](product/account-linking.md)：Discord、Telegram 身份隔离与未来绑定方案。

## 架构

- [总体架构](architecture/overview.md)：系统边界、模块和运行方式。
- [领域模型](architecture/domain-model.md)：核心实体、命令和状态转换。
- [内容定义与存档兼容](architecture/content-versioning.md)：稳定 ID、规则版本与事件快照。
- [ADR-0001：Python 权威后端](architecture/decisions/0001-python-backend.md)
- [ADR-0002：持久化的时间行动](architecture/decisions/0002-persistent-timed-actions.md)
- [ADR-0003：平台适配器](architecture/decisions/0003-platform-adapters.md)

## 交付计划

- [里程碑路线图](milestones/README.md)
- [M0：工程基础](milestones/M0-foundation.md)
- [M1：Discord 采矿纵向切片](milestones/M1-discord-mining-slice.md)
- [M2：Telegram 功能对等](milestones/M2-telegram-parity.md)
- [M3：事件与长期成长](milestones/M3-events-and-progression.md)
- [MVP 验证报告](milestones/verification.md)

## 开发

- [开发与提交工作流](development/workflow.md)：小目标、提交边界、检查和远端操作约定。
- [Docker 运行方式](development/docker.md)：完整服务栈、平台 profile、代理与存档操作。
- [平台冒烟测试](development/platform-smoke-test.md)：Discord 与 Telegram 的最终外部验收步骤。

## 参考

- [旧项目检查结论](reference/legacy-system-findings.md)

## 文档维护规则

- 产品规则变化：更新 `product/` 和受影响的里程碑。
- 架构方向变化：新增 ADR；不要覆写旧决策的历史背景。
- 领域名称变化：更新领域模型、接口和测试用例中的统一语言。
- 里程碑只有在所有验收条件满足后才能标记完成。
- 完成小而完整的分支目标或到达自然检查点时，按开发工作流主动提交。
