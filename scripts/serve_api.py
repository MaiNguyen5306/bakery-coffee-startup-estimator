from pathlib import Path
import sys
from http.server import ThreadingHTTPServer
import argparse
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api.estimate import handler
if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=8000)
    args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),handler)
    print(f'Calculation API: http://127.0.0.1:{args.port}/api/estimate', flush=True)
    server.serve_forever()
