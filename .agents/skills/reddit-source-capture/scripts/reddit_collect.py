#!/usr/bin/env python3
"""通过 OpenCLI 只读搜索 Reddit，或保存单帖及评论。"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def connected_profile(opencli: str) -> str:
    result = subprocess.run(
        [opencli, "profile", "list"], check=False, text=True, capture_output=True, timeout=30
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or result.stdout.strip())
    profiles = re.findall(r"^\s*([^\s—]+)\s+—\s+connected\b", result.stdout, flags=re.MULTILINE)
    if len(profiles) == 1:
        return profiles[0]
    if not profiles:
        raise SystemExit("没有已连接的 OpenCLI Browser Bridge（浏览器桥）Profile（配置档案）")
    raise SystemExit("检测到多个 OpenCLI Profile，请用 --profile 明确指定")


def parse_json_output(text: str) -> Any:
    decoder = json.JSONDecoder()
    stripped = text.strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        for index, char in enumerate(stripped):
            if char not in "[{":
                continue
            try:
                value, _ = decoder.raw_decode(stripped[index:])
                return value
            except json.JSONDecodeError:
                continue
    raise SystemExit(f"OpenCLI 输出不是有效 JSON：{stripped[:500]}")


def safe_name(value: str, limit: int = 72) -> str:
    name = re.sub(r"[^0-9A-Za-z._-]+", "-", value).strip("-._")
    return (name or "reddit")[:limit]


def run_opencli(opencli: str, profile: str, command: list[str]) -> Any:
    full_command = [
        opencli,
        "--profile",
        profile,
        "reddit",
        *command,
        "--window",
        "background",
        "--site-session",
        "ephemeral",
        "--keep-tab",
        "false",
        "-f",
        "json",
    ]
    result = subprocess.run(
        full_command, check=False, text=True, capture_output=True, timeout=180
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        raise SystemExit(f"OpenCLI 失败：{message}")
    return parse_json_output(result.stdout)


def write_result(output: Path, relative: Path, data: Any, event: dict[str, Any]) -> Path:
    path = output / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = output / "manifest.jsonl"
    record = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        **event,
        "output_path": str(path.resolve()),
        "record_count": len(data) if isinstance(data, list) else 1,
    }
    with manifest.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="输出根目录")
    parser.add_argument("--profile", help="OpenCLI Browser Bridge Profile；只有一个时可省略")
    subparsers = parser.add_subparsers(dest="operation", required=True)

    search = subparsers.add_parser("search", help="搜索公开帖子")
    search.add_argument("query")
    search.add_argument("--subreddit")
    search.add_argument("--sort", choices=["relevance", "hot", "top", "new", "comments"], default="relevance")
    search.add_argument("--time", choices=["hour", "day", "week", "month", "year", "all"], default="all")
    search.add_argument("--limit", type=int, default=15)

    read = subparsers.add_parser("read", help="读取单帖和评论")
    read.add_argument("post_id", help="帖子 ID 或完整 URL")
    read.add_argument("--sort", choices=["best", "top", "new", "controversial", "old", "qa"], default="best")
    read.add_argument("--limit", type=int, default=25, help="顶层评论数")
    read.add_argument("--depth", type=int, default=2)
    read.add_argument("--replies", type=int, default=5)
    read.add_argument("--max-length", type=int, default=2000)
    read.add_argument("--expand-more", action="store_true")

    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit 必须大于 0")
    if args.operation == "read" and (args.depth < 0 or args.replies < 0):
        parser.error("--depth 和 --replies 不能小于 0")
    opencli = shutil.which("opencli")
    if not opencli:
        parser.error("缺少 opencli，请先核对 tooling/toolchain.md")
    profile = args.profile or connected_profile(opencli)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    if args.operation == "search":
        command = ["search", args.query, "--sort", args.sort, "--time", args.time, "--limit", str(args.limit)]
        if args.subreddit:
            command.extend(["--subreddit", args.subreddit])
        data = run_opencli(opencli, profile, command)
        path = write_result(
            args.output,
            Path("raw/search") / f"{stamp}-{safe_name(args.query)}.json",
            data,
            {
                "operation": "search",
                "query": args.query,
                "subreddit": args.subreddit,
                "sort": args.sort,
                "time": args.time,
            },
        )
    else:
        if args.max_length < 100:
            parser.error("--max-length 不能小于 100")
        command = [
            "read",
            args.post_id,
            "--sort",
            args.sort,
            "--limit",
            str(args.limit),
            "--depth",
            str(args.depth),
            "--replies",
            str(args.replies),
            "--max-length",
            str(args.max_length),
            "--expand-more",
            "true" if args.expand_more else "false",
        ]
        data = run_opencli(opencli, profile, command)
        path = write_result(
            args.output,
            Path("raw/posts") / f"{stamp}-{safe_name(args.post_id)}.json",
            data,
            {"operation": "read", "post_id": args.post_id, "sort": args.sort},
        )

    print(path.resolve())
    print((args.output / "manifest.jsonl").resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
