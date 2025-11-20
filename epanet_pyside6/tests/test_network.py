"""Unit tests for Network class."""

import unittest
from core.network import Network
from models.node import Junction, Reservoir
from models.link import Pipe

class TestNetwork(unittest.TestCase):
    """Test Network management."""
    
    def setUp(self):
        self.net = Network()
        
    def test_add_node(self):
        """Test adding nodes."""
        j1 = Junction("J1", 0, 0)
        self.net.add_node(j1)
        self.assertIn("J1", self.net.nodes)
        self.assertEqual(self.net.get_node("J1"), j1)
        
        # Duplicate ID check
        with self.assertRaises(ValueError):
            self.net.add_node(Junction("J1", 10, 10))
            
    def test_add_link(self):
        """Test adding links."""
        j1 = Junction("J1", 0, 0)
        j2 = Junction("J2", 10, 0)
        self.net.add_node(j1)
        self.net.add_node(j2)
        
        p1 = Pipe("P1", "J1", "J2")
        self.net.add_link(p1)
        self.assertIn("P1", self.net.links)
        self.assertEqual(self.net.get_link("P1"), p1)
        
        # Missing node check
        p2 = Pipe("P2", "J1", "MISSING")
        with self.assertRaises(ValueError):
            self.net.add_link(p2)
            
    def test_remove_node(self):
        """Test removing nodes."""
        j1 = Junction("J1", 0, 0)
        self.net.add_node(j1)
        self.net.remove_node("J1")
        self.assertNotIn("J1", self.net.nodes)
        
        # Remove non-existent
        with self.assertRaises(ValueError):
            self.net.remove_node("MISSING")
            
    def test_get_by_type(self):
        """Test retrieving objects by type."""
        self.net.add_node(Junction("J1", 0, 0))
        self.net.add_node(Reservoir("R1", 0, 0))
        
        junctions = self.net.get_junctions()
        self.assertEqual(len(junctions), 1)
        self.assertEqual(junctions[0].id, "J1")
        
        reservoirs = self.net.get_reservoirs()
        self.assertEqual(len(reservoirs), 1)
        self.assertEqual(reservoirs[0].id, "R1")

if __name__ == '__main__':
    unittest.main()
