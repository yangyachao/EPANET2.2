"""Integration tests for EPANET PySide6."""

import unittest
import os
import shutil
from core.project import EPANETProject
from models import Junction, Reservoir, Pipe
from core.constants import NodeParam, LinkParam

class TestIntegration(unittest.TestCase):
    """Integration tests for the full workflow."""
    
    def setUp(self):
        """Set up test environment."""
        self.project = EPANETProject()
        self.test_file = "test_integration.inp"
        
    def tearDown(self):
        """Clean up."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        # Clean up any generated report files
        if os.path.exists(self.test_file.replace(".inp", ".rpt")):
            os.remove(self.test_file.replace(".inp", ".rpt"))
        if os.path.exists(self.test_file.replace(".inp", ".bin")):
            os.remove(self.test_file.replace(".inp", ".bin"))
            
    def test_simulation_workflow(self):
        """Test complete simulation workflow."""
        # 1. Build a simple network
        # Reservoir -> Pipe -> Junction
        
        r1 = Reservoir("R1", 0, 0)
        r1.total_head = 100.0
        self.project.network.add_node(r1)
        
        j1 = Junction("J1", 100, 0)
        j1.elevation = 50.0
        j1.base_demand = 10.0
        self.project.network.add_node(j1)
        
        p1 = Pipe("P1", "R1", "J1")
        p1.length = 1000.0
        p1.diameter = 12.0
        p1.roughness = 100.0
        self.project.network.add_link(p1)
        
        # 2. Save project (required for WNTR simulation in our current implementation)
        self.project.save_project(self.test_file)
        
        # 3. Run simulation
        try:
            self.project.run_simulation()
        except Exception as e:
            self.fail(f"Simulation failed: {e}")
            
        # 4. Verify results
        self.assertTrue(self.project.has_results())
        
        head_j1 = self.project.engine.get_node_result("J1", NodeParam.HEAD)
        pressure_j1 = self.project.engine.get_node_result("J1", NodeParam.PRESSURE)
        flow_p1 = self.project.engine.get_link_result("P1", LinkParam.FLOW)
        
        # Basic hydraulic checks
        self.assertGreater(head_j1, 50.0) # Head should be > elevation
        self.assertLess(head_j1, 100.0)   # Head should be < source head (due to friction)
        self.assertGreater(pressure_j1, 0.0)
        self.assertGreater(flow_p1, 0.0)
        
        # 5. Modify property and re-run
        # Increase pipe roughness (make it smoother -> less headloss -> higher pressure)
        # Wait, C-factor: higher is smoother. 
        # Let's change diameter instead, easier to predict.
        # Increase diameter -> less headloss -> higher pressure at J1
        
        old_pressure = pressure_j1
        
        # Update model
        p1_obj = self.project.network.get_link("P1")
        p1_obj.diameter = 24.0 # Double the diameter
        
        # Sync and Save
        self.project.save_project(self.test_file)
        
        # Run again
        self.project.run_simulation()
        
        new_pressure = self.project.engine.get_node_result("J1", NodeParam.PRESSURE)
        
        print(f"Old Pressure: {old_pressure}, New Pressure: {new_pressure}")
        self.assertGreater(new_pressure, old_pressure)

if __name__ == '__main__':
    unittest.main()
