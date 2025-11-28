import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.control import SimpleControl, Rule
from core.network import Network

class TestControls(unittest.TestCase):
    def test_simple_control_parsing(self):
        text = "LINK P1 OPEN IF NODE N1 ABOVE 100"
        control = SimpleControl.from_string(text)
        self.assertIsNotNone(control)
        self.assertEqual(control.link_id, "P1")
        self.assertEqual(control.status, "OPEN")
        self.assertEqual(control.control_type, "IF_NODE")
        self.assertEqual(control.node_id, "N1")
        self.assertEqual(control.operator, "ABOVE")
        self.assertEqual(control.value, 100.0)
        self.assertEqual(control.to_string(), text)
        
    def test_rule_parsing(self):
        text = """RULE 1
IF NODE N1 PRESSURE BELOW 20
THEN PUMP P1 STATUS IS OPEN
ELSE PUMP P1 STATUS IS CLOSED
PRIORITY 1"""
        rule = Rule.from_string(text)
        self.assertIsNotNone(rule)
        self.assertEqual(rule.rule_id, "1")
        self.assertEqual(len(rule.conditions), 1)
        self.assertEqual(len(rule.then_actions), 1)
        self.assertEqual(len(rule.else_actions), 1)
        self.assertEqual(rule.priority, 1.0)
        
    def test_network_storage(self):
        network = Network()
        control = SimpleControl(link_id="P1", status="OPEN", control_type="AT_TIME", time="10:00")
        network.controls.append(control)
        
        self.assertEqual(len(network.controls), 1)
        self.assertEqual(network.controls[0].link_id, "P1")
        
        network.clear()
        self.assertEqual(len(network.controls), 0)

if __name__ == '__main__':
    unittest.main()
