# 参考与致谢

更新时间：2026-08-26。

本页说明这套 Skills 实际参考或调用过哪些公开项目和文档，以及它们影响了哪一部分设计。链接已在发布前重新核验。

## GitHub 项目

| 项目 | 本仓库中的用途 | 链接 |
| --- | --- | --- |
| OpenAI Skills（历史参考） | Skill 目录结构、`SKILL.md`、`agents/openai.yaml` 和安装方式参考；该仓库目前已标记为 deprecated | [仓库](https://github.com/openai/skills) · [Skill Creator](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md) |
| OpenAI Plugins（当前入口） | 当前 Codex Skill 和 Plugin 示例 | [仓库](https://github.com/openai/plugins) |
| yt-dlp | B 站、YouTube 和 X 视频的元数据、字幕、音频与视频采集 | [仓库](https://github.com/yt-dlp/yt-dlp) · [支持站点](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) · [Cookie FAQ](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp) · [EJS](https://github.com/yt-dlp/yt-dlp/wiki/EJS) |
| gallery-dl | X 图片、媒体和元数据采集 | [仓库](https://github.com/mikf/gallery-dl) · [Twitter/X 路线](https://github.com/mikf/gallery-dl/wiki/Twitter) · [认证说明](https://github.com/mikf/gallery-dl/wiki/Authentication) |
| youtube-transcript-api | YouTube 已有字幕的补充读取路线 | [仓库](https://github.com/jdepoix/youtube-transcript-api) · [IP 限制说明](https://github.com/jdepoix/youtube-transcript-api?tab=readme-ov-file#working-around-ip-bans-requestblocked-or-ipblocked-exception) |
| XHS-Downloader | 小红书作品信息和批量媒体下载的可选路线 | [仓库](https://github.com/JoeanAmier/XHS-Downloader) · [README](https://github.com/JoeanAmier/XHS-Downloader/blob/master/README.md) |
| Agent Reach | 多平台能力安装、诊断和后端路由参考 | [仓库](https://github.com/Panniantong/Agent-Reach) · [安装文档](https://github.com/Panniantong/Agent-Reach/blob/main/docs/install.md) |
| OpenCLI | 使用已连接浏览器执行 Reddit 结构化搜索、帖子和评论读取 | [仓库](https://github.com/jackwener/opencli) · [Reddit Adapter](https://github.com/jackwener/opencli/blob/main/docs/adapters/browser/reddit.md) |

## 官方产品与接口文档

| 来源 | 本仓库中的用途 | 链接 |
| --- | --- | --- |
| Kimi WebBridge | 动态网页、授权登录态、页面快照和视觉核验的浏览器路线 | [产品页](https://www.kimi.ai/products/kimi-webbridge) |
| FFmpeg | 音视频转换、音频切片、时长和编码验证 | [官方文档](https://ffmpeg.org/documentation.html) |
| Apple Vision | macOS 本地中英文图片 OCR | [Recognizing Text in Images](https://developer.apple.com/documentation/vision/recognizing-text-in-images) |
| 阿里云智能语音交互 | NLS Token 与短音频 RESTful ASR | [RESTful API](https://help.aliyun.com/zh/isi/developer-reference/restful-api-2) |
| Reddit | 公开研究、正式 Data API 和授权边界 | [Data API Terms](https://redditinc.com/policies/data-api-terms) · [User Agreement](https://redditinc.com/policies/user-agreement) |

## 参考关系说明

- 上述工具负责获取或转换信息；本仓库负责决策路由、停止条件、证据结构和验证流程。
- `video-source-capture` 的通用入口以 yt-dlp 为主，YouTube 字幕 API 和 ASR 为后备。
- `social-source-capture` 组合浏览器、gallery-dl、XHS-Downloader 和 Apple Vision OCR。
- `reddit-source-capture` 组合 Agent Reach 的诊断思路、OpenCLI 的结构化读取和浏览器视觉核验。
- 早期验证还参考过用户本机已有的 B 站下载与阿里云 ASR 脚本。那些本地项目和原始案例没有公开 URL，也不包含在本仓库中；当前仓库只保留独立整理后的可复用实现。

## 许可证与归属

本仓库没有复制上述项目的完整源码。通过安装脚本取得的第三方依赖继续受各自许可证约束。项目名称和商标归各自所有者，本仓库与相关平台没有隶属或背书关系。
