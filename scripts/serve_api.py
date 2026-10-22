from pathlib import Path
import sys
from http.server import ThreadingHTTPServer
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api.estimate import handler
if __name__ == '__main__':
    print('Calculation API: http://127.0.0.1:8000/api/estimate', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8000), handler).serve_forever()
