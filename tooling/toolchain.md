# 采集工具链

更新时间：2026-08-26。

## 能力与依赖

| 能力 | 必需或主要依赖 | 可选后备 |
| --- | --- | --- |
| B 站、YouTube 视频 | `yt-dlp`、`ffmpeg`、`ffprobe` | Node.js、`youtube-transcript-api`、阿里云 NLS |
| X 图片与媒体 | `gallery-dl` | 已授权浏览器、`yt-dlp` |
| 小红书图文 | 已授权浏览器 | XHS-Downloader、macOS Vision OCR |
| Reddit 公开研究 | OpenCLI 与 Browser Bridge | Agent Reach、Kimi WebBridge、正式 Data API |

Python 依赖固定在 [requirements-source-tools.txt](../requirements-source-tools.txt)，安装到仓库的 `.tools/source-tools-venv/`。XHS-Downloader 使用独立环境 `.tools/vendor/XHS-Downloader/.venv/`。

## 安装

基础 Python 工具：

```bash
./scripts/bootstrap-source-tools.sh
```

同时安装 XHS-Downloader：

```bash
./scripts/bootstrap-source-tools.sh --with-xhs
```

脚本不会自动安装系统级 `ffmpeg`、Node.js、OpenCLI、Agent Reach 和浏览器扩展。对应官方入口见 [参考与致谢](../docs/references.md)。

## 自检

```bash
./scripts/check-source-tools.sh video
./scripts/check-source-tools.sh social
./scripts/check-source-tools.sh reddit
./scripts/check-source-tools.sh all
```

`MISS` 表示当前路线的必要工具缺失，`WARN` 表示可选后备工具缺失。

## 阿里云 ASR

使用 `aliyun_asr_chunks.py` 前，只在当前终端提供以下环境变量：

```bash
export ALIYUN_AK_ID="..."
export ALIYUN_AK_SECRET="..."
export ALIYUN_NLS_APPKEY="..."
```

不要把真实值写入仓库、`.env`、命令历史或交付物。

## 文件边界

`.tools/`、`artifacts/`、Cookie 和环境变量文件均被 Git 忽略。公开仓库只保留 Skill、脚本、依赖清单、公开来源和验证口径。

## 更新原则

1. 升级工具前后各运行一次真实公开链接的最小测试。
2. 更新固定版本后同步修改依赖清单和验证记录。
3. 上游站点变化只记录为当前限制，不写成永久通用规则。
4. Cookie、AccessKey 和 token 不进入脚本、配置、日志和提交。
