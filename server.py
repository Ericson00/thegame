from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os
import json

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
STATE_FILE = ROOT / "state.json"
DEFAULT_STATE = {
    "1": {"score": 250, "lastAction": "Startwert gesetzt", "updatedAt": "–"},
    "2": {"score": 250, "lastAction": "Startwert gesetzt", "updatedAt": "–"},
}


def load_state():
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            for g in ("1", "2"):
                if g not in data:
                    data[g] = DEFAULT_STATE[g].copy()
                else:
                    data[g].setdefault("score", DEFAULT_STATE[g]["score"])
                    data[g].setdefault("lastAction", DEFAULT_STATE[g]["lastAction"])
                    data[g].setdefault("updatedAt", DEFAULT_STATE[g]["updatedAt"])
            return data
        except Exception:
            pass
    return {k: v.copy() for k, v in DEFAULT_STATE.items()}


def save_state(data):
    STATE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

STATE = load_state()


class AppHandler(SimpleHTTPRequestHandler):
    def _send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/1", "/2"):
            self.path = "/muenztracker.html"
            return super().do_GET()
        if self.path == "/state":
            return self._send_json(STATE)
        return super().do_GET()

    def do_POST(self):
        if self.path != "/state":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            incoming = json.loads(raw)
            for g in ("1", "2"):
                if g in incoming:
                    STATE[g] = {
                        "score": int(incoming[g].get("score", STATE[g]["score"])),
                        "lastAction": str(incoming[g].get("lastAction", STATE[g]["lastAction"])),
                        "updatedAt": str(incoming[g].get("updatedAt", STATE[g]["updatedAt"])),
                    }
            save_state(STATE)
            return self._send_json({"ok": True})
        except Exception as e:
            return self._send_json({"ok": False, "error": str(e)}, code=400)


if __name__ == "__main__":
    port = 8000
    print(f"Server läuft auf http://0.0.0.0:{port}")
    ThreadingHTTPServer(("0.0.0.0", port), AppHandler).serve_forever()
