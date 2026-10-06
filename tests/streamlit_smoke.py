"""Optional hosted-adapter tests. Install requirements.txt first."""
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
APP = str(Path(__file__).resolve().parents[1] / 'streamlit_app.py')

class HostedDemoTests(unittest.TestCase):
    def start(self):
        at = AppTest.from_file(APP, default_timeout=15).run()
        self.assertEqual(len(at.exception),0)
        return at
    def test_scenarios_and_history_inspection(self):
        at=self.start()
        for scenario, expected in [('Harbor Point · eligible','eligible'),('Juniper Square · review','review'),('Cedar Commons · decline','decline')]:
            at.selectbox(key='preset').set_value(scenario).run()
            at.button[0].click().run()
            self.assertEqual(len(at.exception),0)
            self.assertEqual(at.session_state.current['outcome'],expected)
        self.assertEqual(len(at.session_state.records),3)
        record_id=at.session_state.records[-1]['id']
        at.selectbox(key='history_id').set_value(record_id).run()
        at.button[1].click().run()
        self.assertEqual(len(at.exception),0)
        self.assertEqual(at.session_state.current['outcome'],'eligible')
        self.assertEqual(at.text_input(key='borrower').value,'Harbor Point Holdings')
        self.assertEqual(at.selectbox(key='preset').value,'Saved / edited scenario')
    def test_invalid_application_not_recorded(self):
        at=self.start()
        at.number_input(key='annual_debt_service').set_value(0.0)
        at.button[0].click().run()
        self.assertEqual(len(at.exception),0)
        self.assertEqual(len(at.session_state.records),0)
        self.assertGreater(len(at.error),0)
    def test_sessions_are_isolated(self):
        first=self.start();first.button[0].click().run()
        second=self.start()
        self.assertEqual(len(first.session_state.records),1)
        self.assertEqual(len(second.session_state.records),0)

if __name__=='__main__': unittest.main()
