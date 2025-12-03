
import os
import sys
from core.project import EPANETProject
from models.control import SimpleControl, Rule

def test_export_controls():
    print("Testing export_network with controls...")
    
    # 1. Create Project
    project = EPANETProject()
    project.new_project()
    
    # 2. Add some dummy data
    project.add_node('Junction', 0, 0) # J1
    project.add_node('Junction', 100, 0) # J2
    project.add_link('Pipe', 'J1', 'J2') # P1
    
    # 3. Add Controls
    c1 = SimpleControl(link_id='P1', status='CLOSED', control_type='AT_TIME', time='12:00')
    project.network.controls.append(c1)
    
    # 4. Add Rules
    r1 = Rule(rule_id='1', conditions=['IF SYSTEM CLOCKTIME >= 12:00'], then_actions=['LINK P1 STATUS IS OPEN'], else_actions=[])
    project.network.rules.append(r1)
    
    # 5. Export
    outfile = "test_export.inp"
    try:
        project.save_project(outfile)
        
        # 6. Verify Content
        with open(outfile, 'r') as f:
            content = f.read()
            
        print("\n--- INP Content Snippet ---")
        if "[CONTROLS]" in content:
            print("[CONTROLS] section found.")
            start = content.find("[CONTROLS]")
            end = content.find("\n\n", start)
            print(content[start:end+20])
        else:
            print("FAIL: [CONTROLS] section NOT found.")
            
        if "[RULES]" in content:
            print("[RULES] section found.")
            start = content.find("[RULES]")
            end = content.find("\n\n", start)
            print(content[start:end+20])
        else:
            print("FAIL: [RULES] section NOT found.")
            
        # Check specific strings
        if "LINK P1 CLOSED AT TIME 12:00" in content:
            print("PASS: Control string found.")
        else:
            print("FAIL: Control string missing.")
            
        if "RULE 1" in content:
            print("PASS: Rule string found.")
        else:
            print("FAIL: Rule string missing.")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if os.path.exists(outfile):
            os.remove(outfile)

if __name__ == "__main__":
    test_export_controls()
