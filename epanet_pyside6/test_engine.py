"""Test script to verify EPANET engine loading."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.epanet_engine import EPANETEngine

def test_engine():
    """Test EPANET engine initialization."""
    print("Testing EPANET Engine...")
    
    try:
        # Initialize engine
        print("1. Initializing engine...")
        engine = EPANETEngine()
        print("   ✓ Engine initialized successfully")
        
        # Get version
        print("2. Getting EPANET version...")
        version = engine.get_version()
        major = version // 10000
        minor = (version % 10000) // 100
        patch = version % 100
        print(f"   ✓ EPANET version: {major}.{minor}.{patch}")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_engine()
    sys.exit(0 if success else 1)
