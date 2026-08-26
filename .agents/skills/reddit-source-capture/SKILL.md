---
name: reddit-source-capture
description: "搜索和读取 Reddit 公开帖子、评论与社区信息，保留可追溯原始数据并提炼用户问题、经验和反对意见。用户需要做市场调研、用户研究、产品口碑或技术问题检索时使用。发帖、评论、投票、私信和持续大规模采集不在此技能的默认范围。"
---

# Reddit 信息采集

## 目标

围绕一个明确的研究问题，采集足以支持判断的 Reddit 公开讨论，保留帖子与评论上下文，并把作者自述、群体信号和分析推断分开。

## 开始前

确认：研究问题、关键词或社区、时间范围、需要帖子还是评论、交付位置。用户未限定样本时，先用少量搜索结果校准关键词和社区，再决定是否扩大。

不要把互动量阈值写成通用质量标准。主题相关性、信息具体程度和反例价值优先，分数与评论数只做辅助排序。

## 工具路由

1. 运行工作区 `scripts/check-source-tools.sh reddit`，再运行 `agent-reach doctor --json`、`opencli doctor` 和 `opencli profile list` 做预检查。Agent Reach 未安装时可跳过它的诊断，OpenCLI 仍是当前读取入口。
2. 结构化搜索、帖子和评论读取优先使用 OpenCLI（浏览器命令行桥）。公开页面在当前环境中无需登录也能读取；个性化内容和受限页面需要用户自己在连接的 Chrome Profile（浏览器配置档案）中登录。
3. 页面结构、图片、动态加载或 OpenCLI 结果需要目视核验时，使用 Kimi WebBridge（Kimi 浏览器桥）。同一任务固定一个 session（会话）和浏览器分组。
4. 持续批量、商业用途或超出普通访问规模的研究，先走 Reddit Data API（数据接口）或研究访问申请。

详细选型、当前验证状态与历史结论见 [tool-selection.md](references/tool-selection.md)。

## 执行

使用脚本减少重复命令：

```bash
.agents/skills/reddit-source-capture/scripts/reddit_collect.py \
  --output artifacts/YYYY-MM-DD/reddit \
  search "QUERY" --subreddit SUBREDDIT --time month --limit 10

.agents/skills/reddit-source-capture/scripts/reddit_collect.py \
  --output artifacts/YYYY-MM-DD/reddit \
  read POST_ID --limit 25 --depth 2
```

流程：

1. 先运行一到三个查询，检查召回主题、社区分布和噪声。
2. 调整关键词、社区与时间范围，保存每次原始 JSON（结构化数据）和 manifest（采集清单）。
3. 明确选择值得深入的帖子，再读取评论；不按搜索结果自动展开全部评论。
4. 记录帖子 URL（统一资源定位符）、采集时间、作者、社区、发帖时间、分数、评论数和原始路径。
5. 分析时单独标记：作者自述、他人回应、版主或机器人内容、独立可核验事实、分析推断。

## 验证与停止条件

- 搜索和详情 JSON 可解析，帖子 ID、URL、社区和时间能回到原页面。
- 帖子和评论分开保存；删除、截断、编辑或评论未展开时明确记录。
- Reddit 分数会变化，评论样本受排序方式影响，不把帖子数直接解释为独立用户数或市场份额。
- 只允许 `search`、`read`、`subreddit`、`subreddit-info` 等读取命令。禁止自动调用 `comment`、`reply`、`save`、`subscribe` 和 `upvote`。
- 遇到 403、429、验证码、登录提示或风险警告时停止重试，报告已完成部分和最小用户动作。
- 证据足以回答当前研究问题时停止扩大样本。
