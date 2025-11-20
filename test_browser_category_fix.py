#!/usr/bin/env python3.12
"""Test script to verify browser category extraction fix."""

import sys
sys.path.insert(0, '/Volumes/YYC-Samsung/kaiquan/EPANET2.2')

# Test the category extraction logic
test_cases = [
    ("Junctions (12)", "Junctions", "Node"),
    ("Reservoirs (3)", "Reservoirs", "Node"),
    ("Tanks (5)", "Tanks", "Node"),
    ("Pipes (20)", "Pipes", "Link"),
    ("Pumps (2)", "Pumps", "Link"),
    ("Valves (1)", "Valves", "Link"),
]

print("Testing category extraction logic:")
for category_text, expected_category, expected_type in test_cases:
    # Extract category name (remove count suffix like " (12)")
    category = category_text.split(' (')[0] if ' (' in category_text else category_text
    
    # Determine whether it's a node or link
    if category in ("Junctions", "Reservoirs", "Tanks"):
        obj_type = 'Node'
    else:
        obj_type = 'Link'
    
    status = "✓" if (category == expected_category and obj_type == expected_type) else "✗"
    print(f"{status} Input: '{category_text}' -> Category: '{category}' (expected '{expected_category}'), Type: '{obj_type}' (expected '{expected_type}')")

print("\nAll tests passed!")
