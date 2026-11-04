#!/usr/bin/env python3
"""Capture the exact requests Pi would send, using a local stub provider.

Session logs do not store the system prompt or tool definitions. This runs Pi
against a stub on 127.0.0.1 that records each request and answers 400, so no
provider is contacted and nothing is spent. Installed extensions do still load.

Usage: pi_capture_prompt.py OUT_DIR [pi options...]
Requests are saved as OUT_DIR/request.N.json, in order. It prints a size
breakdown of every request that carries more than a couple of tools.
"""

import http.server
import json
import pathlib
import re
import subprocess
import sys
import threading

CHARS_PER_TOKEN = 4
PI_TIMEOUT_SECONDS = 90
SIDE_CALL_MAX_TOOLS = 2
EXTENSION = """export default function (pi: any) {
  pi.registerProvider("capture", {
    name: "Capture",
    baseUrl: "http://127.0.0.1:PORT/v1",
    apiKey: "stub",
    api: "openai-responses",
    models: [{
      id: "stub",
      name: "Stub",
      reasoning: true,
      input: ["text"],
      cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
      contextWindow: 272000,
      maxTokens: 8192,
    }],
  });
}
"""


def tokens(value):
    text = value if isinstance(value, str) else json.dumps(value)
    return len(text) // CHARS_PER_TOKEN


def message_text(item):
    content = item.get("content")
    if isinstance(content, str):
        return content
    return "".join(block.get("text", "") for block in content)


def report(path):
    request = json.loads(path.read_text())
    tools = request.get("tools", [])
    print(f"{path.name}: ~{tokens(request):,} tok, {len(tools)} tools")
    if len(tools) <= SIDE_CALL_MAX_TOOLS:
        return
    print(f"  tool definitions ~{tokens(tools):,} tok")
    for size, name in sorted(((tokens(tool), tool.get("name")) for tool in tools), reverse=True):
        print(f"    {size:6,}  {name}")
    for item in request.get("input", []):
        if item.get("role") not in ("system", "developer"):
            continue
        text = message_text(item)
        print(f"  instructions ~{tokens(text):,} tok")
        for section in re.split(r"(?m)^(?=#{1,2} |<[a-z_-]+>)", text):
            if len(section) > 200:
                print(f"    {tokens(section):6,}  {section.splitlines()[0][:70]}")


def main():
    out_dir = pathlib.Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers["Content-Length"]))
            path = out_dir / f"request.{len(saved) + 1}.json"
            path.write_bytes(body)
            saved.append(path)
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error":{"message":"stub: captured"}}')

        def log_message(self, format, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    extension = out_dir / "capture_extension.ts"
    extension.write_text(EXTENSION.replace("PORT", str(server.server_port)))
    command = ["pi", "-p", "--no-session", "--offline", "-e", str(extension)]
    command += ["--model", "capture/stub", *sys.argv[2:], "hi"]
    # Pi exits non-zero by design here: the stub rejects every request.
    subprocess.run(
        command,
        capture_output=True,
        stdin=subprocess.DEVNULL,
        timeout=PI_TIMEOUT_SECONDS,
        check=False,
    )
    if not saved:
        raise SystemExit("Pi sent no requests to the stub")
    for path in saved:
        report(path)


main()
