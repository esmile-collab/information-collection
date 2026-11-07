# 信息决策中台：架构图依据与维护

核对日期：2026-11-07。代码 / 文档基线：`0f6d08f942a65e24cd9f3cdaa9c9e0e505b0703d`。

## 图源

`architecture.svg` 是可编辑图源，README 直接展示。图中没有脚本、动画、外部字体或图片依赖。
实线表示已有代码关系或仓库规定的 Skill 流程；虚线表示人工处理、人工维护或下一次发起。蓝色突出评测问题和反馈回路。

## 模块与证据

| 图中关系 | 对应文件 | 已核对的范围 |
| --- | --- | --- |
| 决策与路由、核验、停止条件 | [.agents/skills/research-decision-router/SKILL.md](../.agents/skills/research-decision-router/SKILL.md) | 现有 Skill 流程；由宿主 Agent 执行，包含人工复核。 |
| 三类采集能力 | [.agents/skills/video-source-capture/SKILL.md](../.agents/skills/video-source-capture/SKILL.md) | 与 social-source-capture、reddit-source-capture 并列；按来源选用。 |
| 问题和能力边界 | [docs/verification.md](../docs/verification.md) | 历史验证与已知限制；不能视为本次重新实测。 |
| 稳定方法沉淀 | [AGENTS.md](../AGENTS.md) | 真实任务完成后维护已有 Skill，验证后更新路由；需要 Agent / 人工操作。 |

## 当前边界

- 宿主 Agent 按 Skill 执行；核验与方法沉淀包含人工参与。
- 访问受阻时保留缺口并停止；后续只补充会改变决策的证据。
- 路由与质量核验由宿主 Agent 依照 Skill 完成，没有独立的常驻编排服务或自动评测服务器。
- docs/verification.md 保留历史运行证据；本次架构图核对没有重新访问平台或调用收费 ASR。

## 随代码维护

输入输出、模块调用、评测门槛、记录位置或反馈路径变化时，在同一提交内更新 SVG、对应 README 与本文件。人工环节保留虚线；只有代码已经实现自动执行后才改为实线。
直接编辑 SVG 中的文字、节点与路径，保持全部信息默认可见。英文图存在时同步更新。提交前检查 XML 能解析、文字与箭头不重叠、README 图片路径有效，且图中每条回流都有代码或现有流程依据。
