#!/usr/bin/env python3
"""将任意音视频规范化为 55 秒 WAV 切片，并调用阿里云 NLS 转写。"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlencode


WORKSPACE = Path(__file__).resolve().parents[4]
SOURCE_VENV = WORKSPACE / ".tools/source-tools-venv"
SOURCE_PYTHON = SOURCE_VENV / "bin/python"
if Path(sys.prefix) != SOURCE_VENV and SOURCE_PYTHON.is_file():
    os.execv(str(SOURCE_PYTHON), [str(SOURCE_PYTHON), __file__, *sys.argv[1:]])

import requests
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


ENV_NAMES = ("ALIYUN_AK_ID", "ALIYUN_AK_SECRET", "ALIYUN_NLS_APPKEY")


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"缺少环境变量：{name}")
    return value


def create_token() -> str:
    client = AcsClient(require_env("ALIYUN_AK_ID"), require_env("ALIYUN_AK_SECRET"), "cn-shanghai")
    request = CommonRequest()
    request.set_method("POST")
    request.set_domain("nls-meta.cn-shanghai.aliyuncs.com")
    request.set_version("2019-02-28")
    request.set_action_name("CreateToken")
    response = client.do_action_with_exception(request)
    return json.loads(response)["Token"]["Id"]


def duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return float(result.stdout.strip())


def split_audio(source: Path, work_dir: Path, chunk_seconds: int) -> list[Path]:
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)
    pattern = work_dir / "chunk_%04d.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            "-f",
            "segment",
            "-segment_time",
            str(chunk_seconds),
            "-reset_timestamps",
            "1",
            str(pattern),
        ],
        check=True,
    )
    return sorted(work_dir.glob("chunk_*.wav"))


def recognize(path: Path, token: str, appkey: str) -> tuple[str, dict]:
    query = urlencode(
        {
            "appkey": appkey,
            "format": "wav",
            "sample_rate": "16000",
            "enable_punctuation_prediction": "true",
            "enable_inverse_text_normalization": "true",
            "enable_voice_detection": "true",
        }
    )
    url = f"https://nls-gateway-cn-shanghai.aliyuncs.com/stream/v1/asr?{query}"
    with path.open("rb") as audio:
        response = requests.post(
            url,
            headers={"X-NLS-Token": token, "Content-Type": "application/octet-stream"},
            data=audio,
            timeout=120,
        )
    response.raise_for_status()
    data = response.json()
    if data.get("status") != 20000000:
        raise RuntimeError(f"{path.name} 转写失败：{data.get('status')} {data.get('message', '')}")
    return data.get("result", "").strip(), data


def srt_time(seconds: float) -> str:
    millis = round(seconds * 1000)
    hours, remainder = divmod(millis, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path, help="输入音频或视频")
    parser.add_argument("--output", type=Path, required=True, help="输出目录")
    parser.add_argument("--name", help="输出文件名，不含扩展名")
    parser.add_argument("--chunk-seconds", type=int, default=55, choices=range(10, 60))
    parser.add_argument("--keep-work", action="store_true", help="保留规范化后的 WAV 切片")
    args = parser.parse_args()

    if not args.media.is_file():
        parser.error(f"文件不存在：{args.media}")
    for name in ENV_NAMES:
        require_env(name)

    args.output.mkdir(parents=True, exist_ok=True)
    base_name = args.name or args.media.stem
    work_dir = args.output / f".{base_name}.asr-work"
    total_duration = duration(args.media)
    chunks = split_audio(args.media, work_dir, args.chunk_seconds)
    if not chunks:
        raise SystemExit("未生成音频切片")

    token = create_token()
    appkey = require_env("ALIYUN_NLS_APPKEY")
    records: list[dict] = []
    for index, chunk in enumerate(chunks, start=1):
        start = (index - 1) * args.chunk_seconds
        end = min(index * args.chunk_seconds, total_duration)
        print(f"[{index}/{len(chunks)}] {srt_time(start)} -> {srt_time(end)}", flush=True)
        text, raw = recognize(chunk, token, appkey)
        records.append({"index": index, "start": start, "end": end, "text": text, "raw": raw})
        time.sleep(0.2)

    prefix = args.output / f"{base_name}.aliyun"
    txt_path = Path(f"{prefix}.txt")
    json_path = Path(f"{prefix}.json")
    srt_path = Path(f"{prefix}.srt")
    txt_path.write_text(
        "\n".join(item["text"] for item in records if item["text"]) + "\n", encoding="utf-8"
    )
    json_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    srt_lines: list[str] = []
    for item in records:
        if item["text"]:
            srt_lines.extend(
                [
                    str(item["index"]),
                    f"{srt_time(item['start'])} --> {srt_time(item['end'])}",
                    item["text"],
                    "",
                ]
            )
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")

    if not args.keep_work:
        shutil.rmtree(work_dir)
    print(txt_path)
    print(srt_path)
    print(json_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
