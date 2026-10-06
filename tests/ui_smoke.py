"""Optional browser checks: pip install playwright; playwright install chromium."""
import json
import tempfile
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from creditflow.server import make_server

with tempfile.TemporaryDirectory() as folder:
    server = make_server(0, Path(folder)/'ui.db')
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=['--no-sandbox'])
            page = browser.new_page(viewport={'width':1440,'height':1080}, device_scale_factor=1)
            errors=[]
            expected_rejections=[]
            def check_console(msg):
                if msg.type!='error':return
                if '422 (Unprocessable Entity)' in msg.text and '/api/reviews/' in msg.location.get('url','') and msg.location.get('url','').endswith('/resolve'):
                    expected_rejections.append(msg.text)
                else:errors.append(msg.text)
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('console',check_console)
            page.goto(f'http://127.0.0.1:{server.server_port}')
            for scenario,title in [('eligible','Ready for the next step.'),('review','A closer look is needed.'),('decline','Outside the screening limits.')]:
                page.select_option('#preset',scenario);page.click('#evaluate')
                expect(page.locator('#outcome-title')).to_have_text(title)
                expect(page.locator('#refresh')).to_be_enabled()
            assert page.locator('#history-body tr').count()==3
            page.locator('#history-body tr').last.locator('button').click()
            assert page.locator('#borrower').input_value()=='Harbor Point Holdings'
            assert page.locator('#outcome-title').inner_text()=='Ready for the next step.'
            with page.expect_download() as download:
                page.click('#export')
            evidence=json.loads(Path(download.value.path()).read_text())
            assert evidence['application']['borrower']=='Harbor Point Holdings'
            assert evidence['policy_snapshot']['version']=='demo-cre-1.0'
            assert 'comparison_value' in evidence['rules'][0]
            page.fill('#proposer','Analyst A');page.fill('#review-rationale','Fictional lease review needed')
            page.select_option('#proposed-outcome','review');page.locator('#review-form button').click()
            expect(page.locator('#resolve-form')).to_be_visible()
            page.fill('#reviewer','Analyst A');page.fill('#resolve-rationale','Self review')
            with page.expect_response(lambda response:'/api/reviews/' in response.url and response.url.endswith('/resolve')) as denied:
                page.locator('#resolve-form button').click()
            assert denied.value.status==422
            expect(page.locator('#review-status')).to_contain_text('different demo reviewer')
            page.fill('#reviewer','Reviewer B');page.fill('#resolve-rationale','Independent review accepted')
            page.locator('#resolve-form button').click()
            expect(page.locator('#review-events')).to_contain_text('ACCEPTED')
            expect(page.locator('#result-state')).to_contain_text('Eligible')
            with page.expect_download() as review_download:page.click('#export-reviews')
            review_evidence=json.loads(Path(review_download.value.path()).read_text())
            assert [e['status'] for e in review_evidence['review_events']]==['pending','accepted']
            assert review_evidence['evaluation']['outcome']=='eligible'
            page.screenshot(path='docs/images/governance.png',full_page=True)
            page.fill('#noi','510000')
            assert 'unevaluated changes' in page.locator('#result-meta').inner_text()
            page.locator('#history-body tr').last.locator('button').click()
            assert page.locator('#preset').input_value()=='eligible'
            page.evaluate('() => window.scrollTo(0,0)')
            page.screenshot(path='docs/images/workspace.png',full_page=True)
            page.reload();expect(page.locator('#history-body tr')).to_have_count(3)
            page.locator('#history-body tr').last.locator('button').click()
            page.set_viewport_size({'width':390,'height':844});page.evaluate('() => window.scrollTo(0,0)');page.screenshot(path='docs/images/mobile.png',full_page=True)
            assert page.evaluate('() => document.documentElement.scrollWidth <= window.innerWidth')
            page.fill('#borrower','<img src=x onerror=alert(1)>');page.click('#evaluate')
            expect(page.locator('#history-body tr')).to_have_count(4)
            assert page.locator('#history-body img').count()==0
            assert len(expected_rejections)==1, expected_rejections
            assert not errors, errors
            print('PASS: 3 scenario outcomes, history inspection, export, pending edits, reload persistence, escaped borrower, mobile overflow, no console errors')
            browser.close()
    finally:
        server.shutdown();server.server_close();thread.join()
