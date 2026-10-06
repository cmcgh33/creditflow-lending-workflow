import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from creditflow.storage import Store
from creditflow.engine import evaluate
from creditflow.governance import ReviewError
import test_creditflow as support
BASE = support.BASE

class ReviewTests(unittest.TestCase):
    def test_history_preserves_original_policy_and_separates_review(self):
        with tempfile.TemporaryDirectory() as folder:
            store=Store(Path(folder)/'review.db'); original=store.save(evaluate(BASE))
            proposal=store.propose_review(original['id'],dict(proposer='Analyst A',rationale='Fictional missing lease detail',proposed_outcome='review'))
            with self.assertRaises(ReviewError):store.resolve_review(proposal['id'],dict(reviewer='analyst a',decision='accepted',rationale='Self review'))
            result=store.resolve_review(proposal['id'],dict(reviewer='Reviewer B',decision='accepted',rationale='Require lease review'))
            self.assertEqual(result['status'],'accepted');self.assertEqual(store.get(original['id']),original)
            self.assertEqual([e['status'] for e in store.review_history(original['id'])],['pending','accepted'])
            with self.assertRaises(ReviewError):store.resolve_review(proposal['id'],dict(reviewer='Reviewer C',decision='rejected',rationale='Second review'))
    def test_concurrent_resolution_has_one_winner(self):
        with tempfile.TemporaryDirectory() as folder:
            store=Store(Path(folder)/'review.db');record=store.save(evaluate(BASE))
            p=store.propose_review(record['id'],dict(proposer='A',rationale='Review',proposed_outcome='review'))
            def attempt(who):
                try:store.resolve_review(p['id'],dict(reviewer=who,decision='rejected',rationale='Keep screening'));return True
                except ReviewError:return False
            with ThreadPoolExecutor(max_workers=2) as pool:self.assertEqual(sum(pool.map(attempt,['B','C'])),1)
            self.assertEqual(len(store.review_history(record['id'])),2)
    def test_invalid_and_missing_proposals(self):
        with tempfile.TemporaryDirectory() as folder:
            store=Store(Path(folder)/'review.db');r=store.save(evaluate(BASE))
            for data in [None,{},dict(proposer='A',rationale='',proposed_outcome='review'),dict(proposer='A',rationale='x',proposed_outcome='eligible')]:
                with self.assertRaises(ReviewError):store.propose_review(r['id'],data)
            with self.assertRaises(KeyError):store.propose_review('missing',{})

class ReviewApiTests(support.ApiTests):
    def test_review_round_trip(self):
        import json
        _,r=self.request('/api/evaluations',json.dumps(BASE))
        code,p=self.request('/api/evaluations/'+r['id']+'/reviews',json.dumps(dict(proposer='A',rationale='Missing fictional lease',proposed_outcome='review')))
        self.assertEqual(code,201)
        code,result=self.request('/api/reviews/'+p['id']+'/resolve',json.dumps(dict(reviewer='B',decision='accepted',rationale='Agreed')))
        self.assertEqual(code,201);self.assertEqual(result['authority'],'fictional screening review; no loan approval')
        self.assertEqual(len(self.request('/api/evaluations/'+r['id']+'/reviews')[1]['items']),2)
        self.assertEqual(self.request('/api/evaluations/'+r['id'])[1],r)
