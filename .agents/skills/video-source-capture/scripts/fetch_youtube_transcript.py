#!/usr/bin/env python3
"""优先获取 YouTube 已有字幕并输出 TXT、SRT 和 JSON。"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse


WORKSPACE = Path(__file__).resolve().parents[4]
SOURCE_VENV = WORKSPACE / ".tools/source-tools-venv"
SOURCE_PYTHON = SOURCE_VENV / "bin/python"
if Path(sys.prefix) != SOURCE_VENV and SOURCE_PYTHON.is_file():
    os.execv(str(SOURCE_PYTHON), [str(SOURCE_PYTHON), __file__, *sys.argv[1:]])

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import CouldNotRetrieveTranscript


def video_id(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
        return value
    parsed = urlparse(value)
    if parsed.hostname in {"youtu.be", "www.youtu.be"}:
        return parsed.path.strip("/").split("/")[0]
    if parsed.hostname and parsed.hostname.endswith("youtube.com"):
        if parsed.path == "/watch":
            result = parse_qs(parsed.query).get("v", [""])[0]
            if result:
                return result
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) >= 2 and parts[0] in {"shorts", "embed", "live"}:
            return parts[1]
    raise ValueError(f"无法识别 YouTube 视频 ID：{value}")


def srt_time(seconds: float) -> str:
    millis = round(seconds * 1000)
    hours, remainder = divmod(millis, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", help="YouTube URL 或 11 位视频 ID")
    parser.add_argument("--output", type=Path, required=True, help="输出目录")
    parser.add_argument(
        "--languages",
        nargs="+",
        default=["zh-Hans", "zh-Hant", "zh", "en"],
        help="按优先级排列的字幕语言",
    )
    args = parser.parse_args()

    identifier = video_id(args.video)
    try:
        transcript = YouTubeTranscriptApi().fetch(identifier, languages=args.languages)
    except CouldNotRetrieveTranscript as error:
        raise SystemExit(f"YouTube 字幕获取失败：{error}") from None
    records = transcript.to_raw_data()
    args.output.mkdir(parents=True, exist_ok=True)
    stem = args.output / identifier

    (stem.with_suffix(".json")).write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (stem.with_suffix(".txt")).write_text(
        "\n".join(item["text"] for item in records) + "\n", encoding="utf-8"
    )

    lines: list[str] = []
    for index, item in enumerate(records, start=1):
        start = float(item["start"])
        end = start + float(item["duration"])
        lines.extend(
            [str(index), f"{srt_time(start)} --> {srt_time(end)}", item["text"], ""]
        )
    (stem.with_suffix(".srt")).write_text("\n".join(lines), encoding="utf-8")
    print(stem.with_suffix(".txt"))
    print(stem.with_suffix(".srt"))
    print(stem.with_suffix(".json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
