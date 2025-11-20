"""Unit tests for data models."""

import unittest
from models.node import Junction, Reservoir, Tank
from models.link import Pipe, Pump, Valve
from core.constants import NodeType, LinkType, LinkStatus

class TestNodeModels(unittest.TestCase):
    """Test node model classes."""
    
    def test_junction_defaults(self):
        """Test Junction default values."""
        j = Junction("J1", 10.0, 20.0)
        self.assertEqual(j.id, "J1")
        self.assertEqual(j.x, 10.0)
        self.assertEqual(j.y, 20.0)
        self.assertEqual(j.node_type, NodeType.JUNCTION)
        self.assertEqual(j.elevation, 0.0)
        self.assertEqual(j.base_demand, 0.0)
        
    def test_reservoir_defaults(self):
        """Test Reservoir default values."""
        r = Reservoir("R1", 0.0, 0.0)
        self.assertEqual(r.node_type, NodeType.RESERVOIR)
        self.assertEqual(r.total_head, 0.0)
        
    def test_tank_defaults(self):
        """Test Tank default values."""
        t = Tank("T1", 0.0, 0.0)
        self.assertEqual(t.node_type, NodeType.TANK)
        self.assertEqual(t.init_level, 0.0)
        self.assertEqual(t.min_level, 0.0)
        self.assertEqual(t.max_level, 0.0)
        self.assertEqual(t.diameter, 0.0)
        
    def test_validation(self):
        """Test validation logic."""
        with self.assertRaises(ValueError):
            Junction("", 0, 0) # Empty ID

class TestLinkModels(unittest.TestCase):
    """Test link model classes."""
    
    def test_pipe_defaults(self):
        """Test Pipe default values."""
        p = Pipe("P1", "J1", "J2")
        self.assertEqual(p.id, "P1")
        self.assertEqual(p.from_node, "J1")
        self.assertEqual(p.to_node, "J2")
        self.assertEqual(p.link_type, LinkType.PIPE)
        self.assertEqual(p.length, 0.0)
        self.assertEqual(p.diameter, 0.0)
        self.assertEqual(p.roughness, 100.0)
        self.assertEqual(p.status, LinkStatus.OPEN)
        
    def test_pump_defaults(self):
        """Test Pump default values."""
        p = Pump("PMP1", "J1", "R1")
        self.assertEqual(p.link_type, LinkType.PUMP)
        self.assertEqual(p.speed, 1.0)
        
    def test_valve_defaults(self):
        """Test Valve default values."""
        v = Valve("V1", "J1", "J2")
        self.assertEqual(v.link_type, LinkType.PRV) # Default type
        self.assertEqual(v.diameter, 0.0)
        
    def test_validation(self):
        """Test validation logic."""
        with self.assertRaises(ValueError):
            Pipe("", "J1", "J2") # Empty ID
        with self.assertRaises(ValueError):
            Pipe("P1", "", "J2") # Empty from_node

if __name__ == '__main__':
    unittest.main()
