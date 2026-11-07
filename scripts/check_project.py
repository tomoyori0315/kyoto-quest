#!/usr/bin/env python3
"""Check the static game without installing Python or npm packages."""

from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
import shutil
import subprocess
import sys
from threading import Thread
from urllib.request import urlopen


class InlineScripts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.scripts = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag == "script" and "src" not in dict(attrs):
            self.current = []

    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.current is not None:
            self.scripts.append("".join(self.current))
            self.current = None


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    root = Path(__file__).resolve().parents[1]
    errors = []

    def report(ok, message):
        print(f"{'PASS' if ok else 'FAIL'}: {message}")
        if not ok:
            errors.append(message)

    sources = {}
    for name in ("kyoto-quest.html", "index.html"):
        try:
            sources[name] = (root / name).read_bytes()
        except OSError as exc:
            report(False, f"{name}を読み取れません: {exc}")
    if len(sources) != 2:
        return 1

    report(sources["kyoto-quest.html"] == sources["index.html"], "HTML2本の内容一致")
    html = sources["kyoto-quest.html"].decode("utf-8")
    images = sorted(set(re.findall(r'''["'](assets/[^"']+\.png)["']''', html)))
    missing = [path for path in images if not (root / path).is_file()]
    report(not missing, f"静的なPNG参照 {len(images)}件の存在確認")
    for path in missing:
        print(f"  欠落: {path}")

    parser = InlineScripts()
    parser.feed(html)
    report(bool(parser.scripts), "インラインJavaScriptの検出")
    node = shutil.which("node")
    report(node is not None, "構文チェック用Node.jsの利用可否")
    if node:
        for number, script in enumerate(parser.scripts, 1):
            result = subprocess.run(
                [node, "--check"], input=script, text=True, capture_output=True
            )
            report(result.returncode == 0, f"JavaScript構文（ブロック{number}）")
            if result.returncode:
                print(result.stderr.strip())

    # Loopback only; use a free port and release it before returning.
    try:
        server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(QuietHandler, directory=str(root))
        )
    except OSError as exc:
        report(False, f"HTTP検証用サーバーを起動できません: {exc}")
    else:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        paths = [
            "index.html", "kyoto-quest.html", "index.html?debug=1", "index.html?dpad=1"
        ] + images
        failures = []
        try:
            for path in paths:
                try:
                    with urlopen(
                        f"http://127.0.0.1:{server.server_port}/{path}", timeout=10
                    ) as response:
                        if response.status != 200:
                            failures.append(f"{path}: HTTP {response.status}")
                        elif response.read() != (root / path.split("?", 1)[0]).read_bytes():
                            failures.append(f"{path}: 配信内容がファイルと不一致")
                except (OSError, ValueError) as exc:
                    failures.append(f"{path}: {exc}")
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
        report(not failures, f"HTTP配信 {len(paths)}件（200応答・内容一致）")
        for failure in failures:
            print(f"  {failure}")

    print(f"\n結果: {'NG' if errors else 'OK'}（失敗 {len(errors)}項目）")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
