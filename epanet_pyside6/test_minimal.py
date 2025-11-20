"""Minimal test to isolate crash."""

import sys
print("Step 1: Imports starting")

from core.project import EPANETProject
from models import Junction, Reservoir, Pipe

print("Step 2: Imports complete")

project = EPANETProject()
print("Step 3: Project created")

r1 = Reservoir("R1", 0, 0)
r1.total_head = 100.0
print(f"Step 4: Reservoir created: {r1}")

project.network.add_node(r1)
print("Step 5: Reservoir added to network")

j1 = Junction("J1", 100, 0)
j1.elevation = 50.0
j1.base_demand = 10.0
print(f"Step 6: Junction created: {j1}")

project.network.add_node(j1)
print("Step 7: Junction added to network")

p1 = Pipe("P1", "R1", "J1")
p1.length = 1000.0
p1.diameter = 12.0
p1.roughness = 100.0
print(f"Step 8: Pipe created: {p1}")

project.network.add_link(p1)
print("Step 9: Pipe added to network")

print("Step 10: Calling _sync_network_to_wntr")
project._sync_network_to_wntr()
print("Step 11: _sync_network_to_wntr complete")

print("Step 12: Calling save_project")
project.save_project("test_minimal.inp")
print("Step 13: save_project complete")

print("SUCCESS: All steps completed")
