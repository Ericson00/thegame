from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

class AppHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/', '/1', '/2'):
            self.path = '/muenztracker.html'
        return super().do_GET()

if __name__ == '__main__':
    port = 8000
    print(f'Starte auf http://0.0.0.0:{port} mit /1 und /2')
    ThreadingHTTPServer(('0.0.0.0', port), AppHandler).serve_forever()
