# M2：Telegram 功能对等

状态：实现与自动验证完成；待真实 Telegram Bot 冒烟

## 玩家结果

Telegram 玩家能够完成与 M1 相同的创建联盟、查看状态和采矿流程，而不复制领域或应用逻辑。

## 交付内容

- Telegram PlatformIdentity 适配器；
- 命令和 inline keyboard 展示；
- Telegram 通知投递器；
- 平台无关展示模型的必要修正；
- Discord/Telegram 共用的入站适配器契约测试；
- Telegram 回调重复投递的幂等测试；
- 平台账号绑定策略的明确文档。

## 验收标准

1. Telegram 可以执行 M1 的全部玩家流程。
2. Discord 既有测试保持通过。
3. 两个平台调用相同应用用例并产生相同领域状态变化。
4. 游戏核心没有导入 aiogram 或 discord.py。
5. 消息格式差异只存在于适配器或渲染层。

## 暂不处理

跨平台自动合并账号。MVP 可通过受控绑定码或明确选择维持独立身份，但必须防止仅凭显示名绑定。
