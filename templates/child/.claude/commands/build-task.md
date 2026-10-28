---
description: 子骨架实现当前垂直切片
argument-hint: <任务编号>
---

以子骨架身份实现一个垂直切片：

1. 仅在 READY 或 BUILD 状态开始；先核对任务版本和 B 区范围。
2. 只修改本切片声明的数据、后端、前端、测试和文档，范围外问题记 INBOX。
3. 每完成一个可运行增量就进行相关集成检查，不等全部模块完成后拼装。
4. 在 C 区记录实际 diff/文件/配置和实现摘要，未执行验证写 NOT_RUN。
5. 开始时在 D 区追加 `子 | status: READY -> BUILD`；实现完成后置为 VERIFY 并追加 `子 | status: BUILD -> VERIFY`。不得以编译或页面可打开代替测试通过，继续使用 verify-task。
