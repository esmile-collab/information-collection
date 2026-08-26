# X 与小红书路线

## X

当前成熟度：正文采集有本地案例；2026-08-20 用同一公开帖子实时读取元数据并下载 17 张图片，图片 OCR（光学字符识别）通过。登录态批量采集待真实任务验证。

推荐顺序：

1. 浏览器读取可见正文、线程结构、引用帖子和长文。
2. `gallery-dl -K URL` 先看元数据，不下载。
3. 需要图片时运行 `gallery-dl --cookies-from-browser BROWSER -D OUTPUT URL`。
4. 需要帖子视频时使用 `video-source-capture`（视频源采集）或 `yt-dlp`。
5. 检查 Markdown（标记文本）里是否仍有 `pbs.twimg.com` 等远程媒体链接。

`gallery-dl` 对 X 的用户名密码登录已失效，登录内容依赖浏览器 Cookie（会话凭证）。Cookie 只从用户授权的浏览器会话临时读取，不写入工作区。

公开发布包不附带历史帖子正文和媒体；对应能力状态见仓库验证记录。

## 小红书

当前成熟度：单篇 11 图的原图、OCR（光学字符识别）和人工核验已跑通；XHS-Downloader 已安装，受风控链接待真实任务验证。

单条笔记建议：

1. 在浏览器打开最新分享链接，确认全部轮播图和正文可见。
2. 保存页面正文、当前 URL（统一资源定位符）和原图。
3. 批量媒体需要时运行：

   ```bash
   .tools/vendor/XHS-Downloader/.venv/bin/python \
     .tools/vendor/XHS-Downloader/main.py \
     --url "URL" \
     --work_path "OUTPUT_DIR" \
     --folder_name "media" \
     --record_data yes \
     --note_format md
   ```

4. 对全部图片运行 `ocr_images.swift`，随后逐图核对。

上游已说明：旧分享链接可能受日期和风控影响，自动读取浏览器 Cookie 的功能当前失效，自动滚动可能触发账号风险。优先使用最新分享链接；需要登录态时由用户在浏览器内完成，不把 Cookie 放进命令行或版本库。

公开发布包不附带历史笔记原图和 OCR 结果；对应能力状态见仓库验证记录。

## 来源记录

至少包含：

- 原始链接与最终链接。
- 采集时间和页面显示时间。
- 作者、正文、媒体文件清单和轮播顺序。
- 使用工具、版本、登录态需求和异常。
- OCR（光学字符识别）文本及对应图片。
- 作者自述、独立核验和分析推断的标签。

所用上游项目和官方文档见仓库 [参考与致谢](../../../../docs/references.md)。真实测试状态见 [验证记录](../../../../docs/verification.md)。
