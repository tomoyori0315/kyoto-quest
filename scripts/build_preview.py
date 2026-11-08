#!/usr/bin/env python3
"""Export a committed game snapshot into a new, empty hosting directory."""

import argparse
import hashlib
from html import escape
import json
from pathlib import Path, PurePosixPath
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="HEAD", help="Committed revision to export")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    revision = git("rev-parse", "--verify", "--end-of-options", args.ref + "^{commit}").decode().strip()
    entries = []
    for record in git("ls-tree", "-rz", revision, "--", "index.html", "kyoto-quest.html", "assets").split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, kind, blob = metadata.decode().split()
        path = raw_path.decode("utf-8")
        if path not in ("index.html", "kyoto-quest.html") and not path.endswith(".png"):
            continue
        relative = PurePosixPath(path)
        if mode not in ("100644", "100755") or kind != "blob" or relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Unsupported game file: " + path)
        entries.append((path, blob))
    files = {path: git("cat-file", "blob", blob) for path, blob in entries}
    if "index.html" not in files or "kyoto-quest.html" not in files:
        raise ValueError("Both game HTML files must exist in the selected commit")
    if files["index.html"] != files["kyoto-quest.html"]:
        raise ValueError("Game HTML files must match")

    output = args.output.absolute()
    if output.is_symlink() or (output.exists() and any(output.iterdir())):
        raise ValueError("Output must be a new or empty directory; existing files are never overwritten")
    output.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for path, content in files.items():
        destination = output / "game" / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        hashes[path] = hashlib.sha256(content).hexdigest()
    manifest = {"source_commit": revision, "files_sha256": hashes}
    (output / "snapshot.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    page = '''<!doctype html>
<html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>京都クエスト｜試遊版</title>
<style>body{margin:0;background:#152722;color:#f5f0dc;font:17px/1.8 system-ui,sans-serif}main{max-width:620px;margin:auto;padding:40px 24px}h1{font-size:30px;line-height:1.4}a{color:#b8dfcf}a.play{display:block;background:#efd696;color:#182a23;text-align:center;padding:16px;border-radius:12px;text-decoration:none;font-weight:700;margin:28px 0}code{overflow-wrap:anywhere;font-size:13px}li{margin:12px 0}small{color:#c4cabe}</style>
<main><small>京都クエスト / レビュー用</small><h1>京都を歩いて、<br>遊び心地を確かめる。</h1>
<p>本編への反映前に操作感を確認するための試遊版です。</p>
<a class="play" href="game/index.html">試遊をはじめる →</a>
<p>iPhoneは縦画面で操作してください。</p><ul>
<li>移動スティックで歩けるか</li><li>NPCとの会話と猫帳を開閉できるか</li><li>ステージを行き来できるか</li></ul>
<p><a href="game/index.html?dpad=1">D-padで試す</a> · <a href="game/index.html?debug=1">DBGモード</a></p>
<p><small>対象コミット<br><code>REVISION</code><br>気になる点は、この版の番号と操作手順を相棒に伝えてください。</small></p>
</main></html>
'''
    (output / "index.html").write_text(page.replace("REVISION", escape(revision)), encoding="utf-8")
    print(json.dumps({"source_commit": revision, "game_files": len(files), "output": str(output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
