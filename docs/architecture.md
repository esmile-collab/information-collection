# 模块协作架构：依据与维护

核对日期：2026-11-07。代码 / 文档基线：`7fb85a50335fa0d1a716a8a3a248cf3defe44ea2`。

## 图源与读法

`architecture.svg` 是可编辑图源，README 直接展示；英文版本存在时同步维护。图片无动画、脚本、外部字体或图片依赖。
图中只保留模块名与连线。实线表示模块协作，包含调用、读写与评测依赖；双向箭头包含结果返回。虚线表示人工迭代。模块职责、接口数据与实现边界见下表。
图按当前职责分组，保留实际依赖与直接访问路径。

## 模块与协作依据

| 模块 | 对应文件 | 接口与边界 |
| --- | --- | --- |
| 宿主 Agent 与路由 Skill | [.agents/skills/research-decision-router/SKILL.md](../.agents/skills/research-decision-router/SKILL.md) | 宿主理解任务、读取路由与核验规则，调用采集 Skill，并依据返回证据形成结论。路由是规则文档，不是独立常驻服务。 |
| 三个采集 Skill | [README.md](../README.md) | video-source-capture、social-source-capture、reddit-source-capture 按来源分别执行，不互相调用；返回正文、媒体与来源记录。 |
| 任务资料与方法记录 | [AGENTS.md](../AGENTS.md) | 证据按任务保存，供回看与补采；稳定方法经复核后更新现有 Skill / references。方法更新包含人工操作。 |
| 已知限制 | [docs/verification.md](../docs/verification.md) | 保留历史验证和访问限制，不代表本次重跑平台采集。 |

## 随代码维护

模块职责、调用方、输入输出、共享校验、持久化或回流方式变化时，在同一提交中更新 SVG、README 和本文。不要将人工操作写成自动模块，也不要删除仍然存在的耦合关系。
图片仅显示简短模块名。使用细框线和充分间距，保持简洁图例；具体职责、接口、路径与限制维护在本文。
提交前检查 XML 解析、文字边界、连线与节点、README 引用以及静态资源大小。代码行为没有变化时无需为图增加运行依赖。
