"""Public demo adapter. Same engine, browser-session history; no shared borrower store."""
import json
from datetime import datetime, timezone
from html import escape
from uuid import uuid4
from pathlib import Path
import streamlit as st
from creditflow.engine import evaluate, ValidationError

st.set_page_config(page_title="CreditFlow | Lending workspace", page_icon="↗", layout="wide")
st.html('''<style>
.stApp {background:radial-gradient(ellipse at 85% 0%,#302348 0,transparent 48%),radial-gradient(ellipse at 0% 80%,#103438 0,transparent 48%),#080d1b;color:#eef2ff}
.block-container{max-width:1450px;padding-top:2rem;padding-bottom:2rem}
h1,h2,h3 {letter-spacing:-.7px} [data-testid="stMetric"] {background:linear-gradient(135deg,#1b2438,#121b2b);border:1px solid #3a4361;border-radius:15px;padding:20px}
[data-testid="stMetricLabel"]{color:#bdcae5} [data-testid="stMetricValue"]{color:#8ce9df}
[data-testid="stForm"]{background:#111a2be8;border-color:#35425c;border-radius:17px;padding:24px}
.hero{padding:28px 0 30px;border-bottom:1px solid #3b3a58;margin-bottom:28px}
.hero h1{font-size:48px;font-weight:650;line-height:1.12;margin:12px 0 18px;letter-spacing:-2px}
.hero h1 span{background:linear-gradient(100deg,#69e9dc,#b4a1ff 80%,#f3aed8);background-clip:text;color:transparent}
.hero p{color:#bbc8e0;max-width:750px}.eyebrow{font-size:11px;color:#b6b4d7;letter-spacing:2px}.brand{display:flex;justify-content:space-between;align-items:center;padding:0 0 20px;border-bottom:1px solid #3b3a58;font-size:21px;font-weight:650}.brand span{font-size:11px;color:#b3eadf;border:1px solid #42817b;padding:6px 12px;border-radius:24px}
.result{padding:24px;border:1px solid #54516e;background:linear-gradient(120deg,#19253b,#342548);border-radius:17px;margin:12px 0 24px}.result h2{font-size:29px;margin:10px 0}.result p{color:#c5d1e7}.pill{display:inline-block;padding:5px 12px;border-radius:24px;font-size:12px;font-weight:650}.eligible{background:#194d42;color:#a4f6df}.review{background:#614a22;color:#ffe0a5}.decline{background:#652e47;color:#ffc2dc}.empty{border:1px solid #3e4762;padding:35px;border-radius:17px;color:#c3cbe3;background:#161c31;margin:12px 0 24px}
[data-testid="stBaseButton-primary"]{background:linear-gradient(100deg,#6be5d5,#b5a1ff);color:#102132;border:0;font-weight:700}
@media(max-width:650px){.hero h1{font-size:36px}.brand{font-size:18px}.brand span{font-size:9px}}
</style>''')
st.html('<div class="brand">CreditFlow ↗ <span>Fictional portfolio demo</span></div><section class="hero"><div class="eyebrow">FROM APPLICATION TO EXPLANATION</div><h1>Clarity at every<br><span>credit decision.</span></h1><p>Explore a commercial lending scenario, understand every screening rule, and export the evidence behind its next step.</p></section>')

PRESETS = {
    "Harbor Point · eligible": dict(borrower="Harbor Point Holdings", property_type="Industrial", loan_amount=4500000.0, property_value=6500000.0, noi=520000.0, annual_debt_service=380000.0),
    "Juniper Square · review": dict(borrower="Juniper Square Partners", property_type="Office", loan_amount=4500000.0, property_value=5800000.0, noi=350000.0, annual_debt_service=300000.0),
    "Cedar Commons · decline": dict(borrower="Cedar Commons Group", property_type="Retail", loan_amount=4500000.0, property_value=5000000.0, noi=250000.0, annual_debt_service=300000.0),
}
if "records" not in st.session_state:
    st.session_state.records = []
    st.session_state.current = None
    st.session_state.update(PRESETS["Harbor Point · eligible"])

def load_preset():
    if st.session_state.preset in PRESETS:
        st.session_state.update(PRESETS[st.session_state.preset])

def inspect_record():
    selected = next(r for r in st.session_state.records if r["id"] == st.session_state.history_id)
    st.session_state.current = selected
    st.session_state.preset = "Saved / edited scenario"
    for key, value in selected["application"].items():
        st.session_state[key] = float(value) if key in {"loan_amount", "property_value", "noi", "annual_debt_service"} else value

left, right = st.columns([1, 2], gap="large")
with left:
    st.caption("01 / APPLICATION")
    st.subheader("Build your scenario")
    st.selectbox("Start with a fictional example", [*PRESETS, "Saved / edited scenario"], key="preset", on_change=load_preset)
    with st.form("intake"):
        st.text_input("Fictional borrower name", key="borrower", max_chars=80)
        st.selectbox("Property type", ["Industrial", "Office", "Retail", "Multifamily"], key="property_type")
        for key, label in [("loan_amount", "Loan amount ($)"), ("property_value", "Property value ($)"), ("noi", "Annual NOI ($)"), ("annual_debt_service", "Annual debt service ($)")]:
            st.number_input(label, min_value=0.0, max_value=1000000000.0, step=1000.0, format="%.2f", key=key)
        st.caption("NOI = net operating income. Use fictional information only.")
        submitted = st.form_submit_button("Evaluate application →", type="primary", width="stretch")
    if submitted:
        payload = {key: st.session_state[key] for key in PRESETS["Harbor Point · eligible"]}
        try:
            record = {**evaluate(payload), "id": str(uuid4()), "created_at": datetime.now(timezone.utc).isoformat()}
            st.session_state.records = [record, *st.session_state.records][:100]
            st.session_state.current = record
        except ValidationError as exc:
            for field, message in exc.errors.items():
                st.error(f"{field.replace('_', ' ').title()}: {message}")

with right:
    st.caption("02 / SCREENING RESULT")
    current = st.session_state.current
    if current:
        outcome = current["outcome"]
        title = {"eligible": "Ready for the next step.", "review": "A closer look is needed.", "decline": "Outside the screening limits."}[outcome]
        label = {"eligible": "Eligible for underwriting", "review": "Analyst review", "decline": "Screening decline"}[outcome]
        st.html(f'<div class="result"><span class="pill {outcome}">{label}</span><h2>{title}</h2><p>{escape(current["summary"])}</p></div>')
        st.caption(f'Saved evaluation: {current["application"]["borrower"]} · {current["policy_version"]} · {current["created_at"][:19]} UTC')
        st.caption("Results describe this saved evaluation. Form changes take effect when you click Evaluate.")
        cols = st.columns(3)
        for col, (key, label, unit) in zip(cols, [("dscr", "DSCR", "×"), ("ltv", "Loan to value", "%"), ("debt_yield", "Debt yield", "%")]):
            col.metric(label, f'{current["metrics"][key]:.2f}{unit}')
        st.subheader("Every rule. Every reason.")
        for rule in current["rules"]:
            with st.container(border=True):
                st.markdown(f'**{rule["label"]} · {rule["status"].upper()}**')
                st.write(rule["explanation"])
        st.download_button("Export evaluation JSON ↗", json.dumps(current, indent=2), file_name=f'creditflow-{current["id"]}.json', mime="application/json")
    else:
        st.html('<div class="empty"><h2>A clear next step.</h2><p>Evaluate a scenario to see its screening outcome, calculated ratios, and rule explanations.</p></div>')

st.divider()
st.caption("03 / DECISION HISTORY")
st.subheader("A record you can revisit.")
st.caption("History belongs to this browser session only. Up to 100 evaluations are retained; download JSON to keep evidence. Reloading or ending the session can clear it.")
if st.session_state.records:
    records = st.session_state.records
    st.dataframe([{"Borrower": r["application"]["borrower"], "Loan ($)": float(r["application"]["loan_amount"]), "Property": r["application"]["property_type"], "Outcome": r["outcome"].title(), "Evaluated (UTC)": r["created_at"][:19]} for r in records], hide_index=True, width="stretch")
    def record_label(record_id):
        r = next(r for r in records if r["id"] == record_id)
        return f'{r["application"]["borrower"]} · {r["outcome"]} · {r["id"][:8]}'
    st.selectbox("Choose an evaluation to inspect", [r["id"] for r in records], format_func=record_label, key="history_id")
    st.button("Inspect saved evaluation →", on_click=inspect_record)
else:
    st.info("No evaluations yet. Start with a fictional scenario above.")

with st.expander("Policy reference · demo-cre-1.0"):
    st.table([
        {"Rule": "DSCR", "Eligible": "≥ 1.25×", "Review": "≥ 1.00× and < 1.25×", "Decline": "< 1.00×"},
        {"Rule": "LTV", "Eligible": "≤ 75%", "Review": "> 75% and ≤ 85%", "Decline": "> 85%"},
        {"Rule": "Debt yield", "Eligible": "≥ 8%", "Review": "≥ 6% and < 8%", "Decline": "< 6%"},
    ])
    st.write("Decline takes precedence over review. Rules compare unrounded ratios; displayed metrics round to two decimals. Property type is contextual and does not affect screening.")

st.caption("CreditFlow · Fictional rules and data. Educational screening only; no lending approval.")
st.link_button("Explore the source and BA case study", "https://github.com/cmcgh33/creditflow-lending-workflow")
