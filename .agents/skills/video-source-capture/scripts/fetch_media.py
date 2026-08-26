#!/usr/bin/env python3
"""用工作区 yt-dlp 采集视频元数据、字幕、音频或视频。"""

from __future__ import annotations

import argparse
import shlex
import shutil
import subprocess
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[4]
YTDLP = WORKSPACE / ".tools/source-tools-venv/bin/yt-dlp"


def build_command(args: argparse.Namespace) -> list[str]:
    command = [
        str(YTDLP),
        "--write-info-json",
        "--write-thumbnail",
        "--no-overwrites",
        "--paths",
        str(args.output),
        "-o",
        "%(extractor)s/%(id)s/%(title)s [%(id)s].%(ext)s",
        "--yes-playlist" if args.playlist else "--no-playlist",
    ]

    node = shutil.which("node")
    if node:
        command.extend(["--js-runtimes", f"node:{node}"])

    if args.browser:
        command.extend(["--cookies-from-browser", args.browser])

    if args.mode == "metadata":
        command.append("--skip-download")
    elif args.mode == "captions":
        command.extend(
            [
                "--skip-download",
                "--write-subs",
                "--write-auto-subs",
                "--sub-langs",
                args.subtitle_languages,
                "--sub-format",
                "srt/vtt/best",
            ]
        )
    elif args.mode == "audio":
        command.extend(["-f", "bestaudio/best", "-x", "--audio-format", "m4a"])
    elif args.mode == "video":
        command.extend(["-f", "bv*+ba/b", "--merge-output-format", "mp4"])
    elif args.mode == "all":
        command.extend(
            [
                "-f",
                "bv*+ba/b",
                "--merge-output-format",
                "mp4",
                "--write-subs",
                "--write-auto-subs",
                "--sub-langs",
                args.subtitle_languages,
                "--sub-format",
                "srt/vtt/best",
            ]
        )

    command.append(args.url)
    return command


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="B 站、YouTube 或 yt-dlp 支持的视频 URL")
    parser.add_argument(
        "--mode",
        choices=["metadata", "captions", "audio", "video", "all"],
        default="metadata",
        help="采集模式，默认只取元数据",
    )
    parser.add_argument("--output", type=Path, required=True, help="输出根目录")
    parser.add_argument(
        "--subtitle-languages",
        default="zh.*,en.*",
        help="yt-dlp 字幕语言表达式，默认中文和英文",
    )
    parser.add_argument(
        "--browser",
        choices=["brave", "chrome", "chromium", "edge", "firefox", "safari"],
        help="临时读取用户已授权的浏览器 Cookie，不导出 Cookie 文件",
    )
    parser.add_argument("--playlist", action="store_true", help="允许采集播放列表或合集")
    args = parser.parse_args()

    if not YTDLP.is_file():
        parser.error(f"缺少 {YTDLP}，请先运行 scripts/bootstrap-source-tools.sh")

    args.output.mkdir(parents=True, exist_ok=True)
    command = build_command(args)
    print("运行：", shlex.join(command))
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
