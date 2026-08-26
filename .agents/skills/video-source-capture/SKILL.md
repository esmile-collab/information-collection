---
name: video-source-capture
description: "采集 B 站与 YouTube 的公开视频、元数据、字幕和音视频，并在可信字幕缺失时运行 ASR（自动语音识别）。用户给出视频链接、需要逐字稿、要下载公开视频或分析视听内容时使用。普通网页和 X、小红书帖子不使用。"
---

# 视频源采集

## 目标

用最少下载量获得能支持当前判断的本地证据，同时保留来源、字幕或逐字稿和必要的原始媒体。

## 输入边界

开始前确认已有上下文中是否包含：视频链接、信息用途、需要的交付物、输出目录。缺失项不会改变路线时直接采用最小方案；默认输出到工作区 `artifacts/YYYY-MM-DD/<source-id>/`。

仅处理公开内容或用户有权访问的内容。登录、验证码、地区或权限限制需要用户在浏览器中完成授权后再继续。

## 执行流程

1. 运行工作区 `scripts/check-source-tools.sh video`。工具缺失时运行 `scripts/bootstrap-source-tools.sh`。
2. 先采集元数据：

   ```bash
   .agents/skills/video-source-capture/scripts/fetch_media.py URL --mode metadata --output OUTPUT_DIR
   ```

3. 需要理解口播时，优先请求站内字幕：

   ```bash
   .agents/skills/video-source-capture/scripts/fetch_media.py URL --mode captions --output OUTPUT_DIR
   ```

4. 字幕缺失、错误明显或画外音会改变结论时，下载音频并运行 ASR（自动语音识别）：

   ```bash
   .agents/skills/video-source-capture/scripts/fetch_media.py URL --mode audio --output OUTPUT_DIR
   .agents/skills/video-source-capture/scripts/aliyun_asr_chunks.py AUDIO_FILE --output OUTPUT_DIR/transcript
   ```

5. 只有画面本身影响判断时才下载视频。提取关键帧后回看原视频时间点，不用 OCR（光学字符识别）或自动描述替代视觉核验。
6. 记录源链接、采集时间、标题、作者、发布日期、工具版本、产物路径和异常。作者口述与独立事实分开标记。

## 验证

- `.info.json` 可解析，源链接、ID、标题和时长合理。
- 下载文件非空；音视频用 `ffprobe` 验证时长和编码。
- 字幕或 ASR（自动语音识别）抽查开头、中段、结尾；专有名词、数字和否定词回听原音。
- SRT（字幕文件）时间码单调递增，TXT（纯文本）和 JSON（结构化数据）与分段数一致。

## 路由与停止条件

- B 站和 YouTube 的站点差异、现有证据与后备路线见 [source-playbook.md](references/source-playbook.md)。
- 页面删除、付费限制、验证码或未授权登录出现时停止自动采集，报告已完成部分和最小用户配合项。
- 能用字幕回答时停止媒体下载；已有证据足以支持决策时停止扩张采集范围。
