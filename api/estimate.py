"""Vercel function; same handler is served locally by scripts/serve_api.py."""
from http.server import BaseHTTPRequestHandler
from dataclasses import asdict
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from estimator.calculate import calculate
from estimator.schemas import Scenario
from estimator.staffing import staffing
from estimator.loaders import assumptions, rows, ROOT
from estimator.scenarios import reproduce
from estimator.revenue import calculate_revenue, replay_revenue, RevenueScenario


def live_scenario(data):
    if not isinstance(data, dict):
        raise ValueError('Scenario must be an object')
    # Already-open tabs may retain this removed field after a frontend update.
    # Espresso is now standard for both shop types, regardless of its old value.
    current=dict(data)
    current.pop('espresso', None)
    return Scenario(**current)


def execute(payload):
    if not isinstance(payload, dict):
        raise ValueError('Expected a JSON object')
    if payload.get('action') == 'revenue_reproduce':
        return replay_revenue(payload['export'])
    if payload.get('action') == 'revenue':
        inputs=payload.get('cost_inputs')
        cost=calculate(live_scenario(inputs.get('scenario',{})),inputs.get('overrides'),inputs.get('mode','demo')) if inputs else None
        return calculate_revenue(payload.get('revenue',{}),payload.get('channels'),payload.get('baskets'),cost,payload.get('linked_fingerprint'))
    if payload.get('action') == 'reproduce':
        return reproduce(json.dumps(payload['export'], allow_nan=False))
    if not isinstance(payload.get('overrides', {}), dict):
        raise ValueError('Overrides must be an object')
    scenario = payload.get('scenario', {})
    if not isinstance(scenario, dict):
        raise ValueError('Scenario must be an object')
    return calculate(live_scenario(scenario), payload.get('overrides'), payload.get('mode', 'demo'))


class handler(BaseHTTPRequestHandler):
    def reply(self, status, data):
        encoded = json.dumps(data, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        defaults=asdict(Scenario())
        defaults['owner_hours']=staffing(Scenario())['owner_requested']
        self.reply(200, {'scenario': defaults, 'assumptions': assumptions(),
                         'sources': rows(ROOT / 'docs/source_register.csv'),
                         'revenue_defaults': asdict(RevenueScenario()),
                         'revenue_sources': rows(ROOT/'data/processed/revenue/sources.csv'),
                         'menu_prices': rows(ROOT/'data/processed/revenue/menu_prices.csv'),
                         'payment_fees': rows(ROOT/'data/processed/revenue/payment_fees.csv'),
                         'methodology': (ROOT / 'docs/methodology.md').read_text(),
                         'limitations': (ROOT / 'docs/limitations.md').read_text()})

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 512_000:
                self.reply(413, {'error': 'Request must contain 1–512000 bytes'})
                return
            payload = json.loads(self.rfile.read(length), parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite JSON number')))
            self.reply(200, execute(payload))
        except (ValueError, TypeError, KeyError, OverflowError) as error:
            self.reply(400, {'error': str(error)})
        except Exception:
            self.reply(500, {'error': 'Unable to calculate this scenario. Please try again.'})
