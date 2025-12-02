"""Test script for Pattern and Curve editors."""

import sys
from PySide6.QtWidgets import QApplication
from models import Pattern, Curve, CurveType
from gui.dialogs import PatternEditor, CurveEditor


def test_pattern_editor():
    """Test Pattern Editor dialog."""
    print("Testing Pattern Editor...")
    
    app = QApplication(sys.argv)
    
    # Create test pattern
    test_multipliers = [1.0, 1.2, 1.5, 1.3, 1.1, 0.9, 0.8, 1.0]
    
    dialog = PatternEditor()
    dialog.load_data("PAT1", test_multipliers, "Test pattern")
    
    def on_updated(pattern_id, multipliers, comment):
        print(f"Pattern updated: ID={pattern_id}, Count={len(multipliers)}, Comment={comment}")
    
    dialog.pattern_updated.connect(on_updated)
    dialog.show()
    
    sys.exit(app.exec())


def test_curve_editor():
    """Test Curve Editor dialog."""
    print("Testing Curve Editor...")
    
    app = QApplication(sys.argv)
    
    # Create test curve (pump curve with 3 points)
    test_points = [(0.0, 100.0), (500.0, 80.0), (1000.0, 0.0)]
    
    dialog = CurveEditor()
    dialog.load_data("CURVE1", "Pump", test_points, "Test pump curve")
    
    def on_updated(curve_id, curve_type, points, comment):
        print(f"Curve updated: ID={curve_id}, Type={curve_type}, Points={len(points)}, Comment={comment}")
    
    dialog.curve_updated.connect(on_updated)
    dialog.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Pattern and Curve editors")
    parser.add_argument("--pattern", action="store_true", help="Test Pattern Editor")
    parser.add_argument("--curve", action="store_true", help="Test Curve Editor")
    
    args = parser.parse_args()
    
    if args.pattern:
        test_pattern_editor()
    elif args.curve:
        test_curve_editor()
    else:
        print("Usage: python test_editors.py [--pattern | --curve]")
        print("  --pattern: Test Pattern Editor")
        print("  --curve: Test Curve Editor")
