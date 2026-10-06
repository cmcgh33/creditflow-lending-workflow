import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from creditflow.engine import evaluate, ValidationError
from creditflow.storage import Store
from creditflow.server import make_server

BASE = dict(borrower="Fictional Holdings", property_type="Industrial", loan_amount="1000000", property_value="2000000", noi="150000", annual_debt_service="100000")

def app(**changes):
    return {**BASE, **changes}

class EngineTests(unittest.TestCase):
    def test_all_pass(self):
        r = evaluate(BASE)
        self.assertEqual(r['outcome'], 'eligible')
        self.assertEqual(r['metrics'], {'dscr': 1.5, 'ltv': 50.0, 'debt_yield': 15.0})
    def test_thresholds(self):
        cases = [
            ('dscr', dict(noi='125000'), 'pass'), ('dscr', dict(noi='124999.99'), 'review'),
            ('dscr', dict(noi='100000'), 'review'), ('dscr', dict(noi='99999.99'), 'decline'),
            ('ltv', dict(loan_amount='1500000'), 'pass'), ('ltv', dict(loan_amount='1500000.01'), 'review'),
            ('ltv', dict(loan_amount='1700000'), 'review'), ('ltv', dict(loan_amount='1700000.01'), 'decline'),
            ('debt_yield', dict(noi='80000'), 'pass'), ('debt_yield', dict(noi='79999.99'), 'review'),
            ('debt_yield', dict(noi='60000'), 'review'), ('debt_yield', dict(noi='59999.99'), 'decline')]
        for metric, changes, expected in cases:
            with self.subTest(metric=metric, changes=changes):
                r = evaluate(app(**changes))
                self.assertEqual(next(rule['status'] for rule in r['rules'] if rule['metric'] == metric), expected)
    def test_precedence(self):
        self.assertEqual(evaluate(app(noi='120000', loan_amount='1800000'))['outcome'], 'decline')
        self.assertEqual(evaluate(app(noi='120000'))['outcome'], 'review')
    def test_zero_noi_is_valid_decline(self):
        self.assertEqual(evaluate(app(noi='0'))['outcome'], 'decline')
    def test_invalid_numeric_inputs(self):
        for value in ['NaN', 'Infinity', '-1', '0', '1.001', '1000000001', True, [], {}, None, '1e999999']:
            with self.subTest(value=value):
                with self.assertRaises(ValidationError): evaluate(app(loan_amount=value))
    def test_invalid_application(self):
        for payload in [None, [], {}, app(borrower=' '), app(borrower='x'*81), app(property_type=[]), app(extra=1)]:
            with self.subTest(payload=payload):
                with self.assertRaises(ValidationError): evaluate(payload)
    def test_property_type_does_not_change_outcome(self):
        for kind in ['Office', 'Retail', 'Multifamily']:
            self.assertEqual(evaluate(app(property_type=kind))['outcome'], 'eligible')
    def test_snapshot_and_normalized_input(self):
        r = evaluate(app(borrower=' Fictional Holdings ', loan_amount='1e6'))
        self.assertEqual(r['application']['loan_amount'], '1000000')
        self.assertEqual(r['application']['borrower'], 'Fictional Holdings')
        self.assertEqual(r['policy_snapshot']['version'], r['policy_version'])

class StoreTests(unittest.TestCase):
    def test_persistence_and_independent_evaluations(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'demo.db'; store = Store(path)
            a = store.save(evaluate(BASE)); b = store.save(evaluate(BASE))
            self.assertNotEqual(a['id'], b['id'])
            self.assertEqual(Store(path).get(a['id']), a)
            self.assertEqual(len(store.list()), 2)
            self.assertIsNone(store.get("' OR 1=1 --"))

class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.server = make_server(0, Path(cls.temp.name)/'api.db')
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True); cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join();cls.temp.cleanup()
    def request(self, path, body=None, headers=None):
        req = Request(self.url+path, data=None if body is None else body.encode(), headers=headers or {'Content-Type':'application/json'})
        try: response = urlopen(req)
        except HTTPError as exc: response = exc
        with response:
            raw = response.read()
            return response.status, json.loads(raw) if 'application/json' in response.headers.get('Content-Type','') else raw
    def test_round_trip(self):
        code,r = self.request('/api/evaluations', json.dumps(BASE));self.assertEqual(code,201)
        self.assertEqual(self.request('/api/evaluations/'+r['id']), (200,r))
        self.assertIn(r, self.request('/api/evaluations')[1]['items'])
    def test_invalid_not_saved(self):
        before = len(self.request('/api/evaluations')[1]['items'])
        self.assertEqual(self.request('/api/evaluations',json.dumps(app(annual_debt_service=0)))[0],422)
        self.assertEqual(len(self.request('/api/evaluations')[1]['items']),before)
    def test_malformed_json(self):
        for value in ['{', 'NaN']:
            self.assertEqual(self.request('/api/evaluations',value)[0],400)
    def test_size_and_content_type(self):
        self.assertEqual(self.request('/api/evaluations',' '*8193)[0],413)
        self.assertEqual(self.request('/api/evaluations','{}',{'Content-Type':'text/plain'})[0],415)
    def test_cross_origin(self):
        self.assertEqual(self.request('/api/evaluations',json.dumps(BASE),{'Content-Type':'application/json','Origin':'https://example.com'})[0],403)
    def test_routes(self):
        self.assertEqual(self.request('/api/policy')[1]['version'],'demo-cre-1.0')
        for path in ['/missing','/api/evaluations/missing','/../creditflow/engine.py']:
            self.assertEqual(self.request(path)[0],404)
        for path in ['/','/app.js','/style.css']:
            self.assertEqual(self.request(path)[0],200)

if __name__ == '__main__': unittest.main()
