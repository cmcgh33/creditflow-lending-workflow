"""Fictional maker/checker review; supplied identities are demo labels, not authentication."""
from datetime import datetime, timezone
from uuid import uuid4

class ReviewError(ValueError):
    pass

def text(value, label):
    if not isinstance(value, str) or not 1 <= len(value.strip()) <= 500 or any(ord(c) < 32 for c in value):
        raise ReviewError(f"Provide {label} (1–500 characters).")
    return value.strip()

def propose(evaluation, payload):
    if not isinstance(payload, dict) or set(payload) != {'proposer', 'rationale', 'proposed_outcome'}:
        raise ReviewError('Provide proposer, rationale and proposed_outcome only.')
    outcome = payload['proposed_outcome']
    if outcome not in ('eligible', 'review', 'decline') or outcome == evaluation['outcome']:
        raise ReviewError('Choose a different fictional screening disposition.')
    return {'id': str(uuid4()), 'evaluation_id': evaluation['id'], 'policy_version': evaluation['policy_version'],
            'original_outcome': evaluation['outcome'], 'proposed_outcome': outcome,
            'proposer': text(payload['proposer'], 'proposer'), 'rationale': text(payload['rationale'], 'rationale'),
            'status': 'pending', 'created_at': datetime.now(timezone.utc).isoformat()}

def resolve(proposal, payload):
    if proposal['status'] != 'pending':
        raise ReviewError('Proposal already resolved.')
    if not isinstance(payload, dict) or set(payload) != {'reviewer', 'decision', 'rationale'}:
        raise ReviewError('Provide reviewer, decision and rationale only.')
    reviewer = text(payload['reviewer'], 'reviewer')
    if reviewer.casefold() == proposal['proposer'].casefold():
        raise ReviewError('A different demo reviewer must resolve this proposal.')
    if payload['decision'] not in ('accepted', 'rejected'):
        raise ReviewError('Choose accepted or rejected.')
    return {**proposal, 'status': payload['decision'], 'reviewer': reviewer,
            'review_rationale': text(payload['rationale'], 'review rationale'),
            'resolved_at': datetime.now(timezone.utc).isoformat(), 'authority': 'fictional screening review; no loan approval'}
