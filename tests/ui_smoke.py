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
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('console',lambda msg:errors.append(msg.text) if msg.type=='error' else None)
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
            assert not errors, errors
            print('PASS: 3 scenario outcomes, history inspection, export, pending edits, reload persistence, escaped borrower, mobile overflow, no console errors')
            browser.close()
    finally:
        server.shutdown();server.server_close();thread.join()
