import sys
import os
import unittest

# Add parent directory to path to import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.project import EPANETProject as Project
from core.constants import FlowUnits, LinkType, NodeType

class TestUnitHandling(unittest.TestCase):
    def setUp(self):
        self.project = Project()
        self.test_dir = os.path.dirname(__file__)
        self.gpm_file = os.path.join(self.test_dir, 'test_units_gpm.inp')
        self.lps_file = os.path.join(self.test_dir, 'test_units_lps.inp')

    def test_gpm_units(self):
        print("\nTesting GPM (US) Units...")
        self.project.open_project(self.gpm_file)
        
        # Check Flow Units
        self.assertEqual(self.project.network.options.flow_units, FlowUnits.GPM)
        print("Flow Units: GPM - OK")
        
        # Check Node Elevation (should be 100 ft)
        node2 = self.project.network.nodes['2']
        self.assertAlmostEqual(node2.elevation, 100.0, places=4)
        print(f"Node Elevation: {node2.elevation} ft - OK")
        
        # Check Pipe Diameter (should be 12 inches)
        pipe1 = self.project.network.links['1']
        self.assertAlmostEqual(pipe1.diameter, 12.0, places=4)
        print(f"Pipe Diameter: {pipe1.diameter} in - OK")
        
        # Check Pipe Length (should be 1000 ft)
        self.assertAlmostEqual(pipe1.length, 1000.0, places=4)
        print(f"Pipe Length: {pipe1.length} ft - OK")
        
        # Run Simulation
        print("Running Simulation...")
        self.project.run_simulation()
        
        # Check Results
        # Node 2 Pressure
        # Reservoir Head = 200 ft
        # Node 2 Elev = 100 ft
        # Static Head = 100 ft
        # Pressure = 100 ft * 0.433 psi/ft = 43.3 psi
        # With flow, there will be headloss.
        # Demand = 100 GPM.
        # Pipe 12 inch, 1000 ft.
        # Headloss will be small.
        print(f"Node 2 Pressure: {node2.pressure} psi")
        self.assertTrue(40.0 < node2.pressure < 45.0)
        print("Pressure Result - OK")
        
        # Check Link Flow (should be 100 GPM)
        print(f"Link 1 Flow: {pipe1.flow} GPM")
        self.assertAlmostEqual(pipe1.flow, 100.0, delta=0.1)
        print("Flow Result - OK")

    def test_lps_units(self):
        print("\nTesting LPS (SI) Units...")
        self.project.open_project(self.lps_file)
        
        # Check Flow Units
        self.assertEqual(self.project.network.options.flow_units, FlowUnits.LPS)
        print("Flow Units: LPS - OK")
        
        # Check Node Elevation (should be 30.48 m)
        node2 = self.project.network.nodes['2']
        self.assertAlmostEqual(node2.elevation, 30.48, places=4)
        print(f"Node Elevation: {node2.elevation} m - OK")
        
        # Check Pipe Diameter (should be 304.8 mm)
        pipe1 = self.project.network.links['1']
        self.assertAlmostEqual(pipe1.diameter, 304.8, places=4)
        print(f"Pipe Diameter: {pipe1.diameter} mm - OK")
        
        # Check Pipe Length (should be 304.8 m)
        self.assertAlmostEqual(pipe1.length, 304.8, places=4)
        print(f"Pipe Length: {pipe1.length} m - OK")
        
        # Run Simulation
        print("Running Simulation...")
        self.project.run_simulation()
        
        # Check Results
        # Node 2 Pressure
        # Reservoir Head = 60.96 m
        # Node 2 Elev = 30.48 m
        # Static Head = 30.48 m
        # Pressure = 30.48 m (since specific gravity is 1.0)
        print(f"Node 2 Pressure: {node2.pressure} m")
        self.assertTrue(28.0 < node2.pressure < 32.0)
        print("Pressure Result - OK")

if __name__ == '__main__':
    unittest.main()
