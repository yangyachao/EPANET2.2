"""EPANET Input/Output utilities for Scenarios."""

import os
from datetime import datetime
from core.constants import NodeParam, LinkParam

def export_scenario(project, filepath: str):
    """Export scenario data to INP file.
    
    Exports:
    - Demands
    - Initial Quality
    - Status
    - Controls
    - Rules
    - Energy
    - Options
    
    Args:
        project: EPANETProject instance
        filepath: Output file path
    """
    network = project.network
    
    with open(filepath, 'w', encoding='utf-8') as f:
        # Title
        f.write("[TITLE]\n")
        f.write(f"Scenario Export from {network.title or 'EPANET Project'}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Demands
        f.write("[DEMANDS]\n")
        f.write(";Junction        \tDemand      \tPattern         \tCategory\n")
        for node in network.nodes.values():
            if node.node_type.name == 'JUNCTION':
                # Base demand
                if node.base_demand != 0 or node.demand_pattern:
                    f.write(f" {node.id:<16}\t{node.base_demand:<12}\t{node.demand_pattern or '':<16}\n")
                # TODO: Handle multiple demand categories if supported in data model
        f.write("\n")
        
        # Quality (Initial Quality)
        f.write("[QUALITY]\n")
        f.write(";Node            \tInitQual\n")
        for node in network.nodes.values():
            if node.init_quality != 0:
                f.write(f" {node.id:<16}\t{node.init_quality}\n")
        f.write("\n")
        
        # Status (Initial Status/Setting)
        f.write("[STATUS]\n")
        f.write(";ID              \tStatus/Setting\n")
        for link in network.links.values():
            if link.link_type.name in ['PUMP', 'VALVE', 'PIPE']:
                # Check for non-default status/setting
                # This requires knowing the initial status vs current.
                # For now, we export current status/setting as "initial" for the scenario.
                if hasattr(link, 'initial_status') and link.initial_status:
                     f.write(f" {link.id:<16}\t{link.initial_status}\n")
                elif hasattr(link, 'initial_setting') and link.initial_setting is not None:
                     f.write(f" {link.id:<16}\t{link.initial_setting}\n")
        f.write("\n")
        
        # Controls
        f.write("[CONTROLS]\n")
        for control in network.controls:
            f.write(f"{str(control)}\n")
        f.write("\n")
        
        # Rules
        f.write("[RULES]\n")
        for rule in network.rules:
            f.write(f"{str(rule)}\n")
        f.write("\n")
        
        # Energy
        f.write("[ENERGY]\n")
        opts = network.options
        if hasattr(opts, 'global_efficiency'): f.write(f" Global Efficiency  \t{opts.global_efficiency}\n")
        if hasattr(opts, 'global_price'): f.write(f" Global Price       \t{opts.global_price}\n")
        if hasattr(opts, 'demand_charge'): f.write(f" Demand Charge      \t{opts.demand_charge}\n")
        # Pump energy settings
        for link in network.links.values():
            if link.link_type.name == 'PUMP':
                # Check for pump specific energy settings
                pass # TODO: Add pump energy settings if stored in model
        f.write("\n")
        
        # Options
        f.write("[OPTIONS]\n")
        opts = network.options
        f.write(f" Units              \t{opts.flow_units.name}\n")
        
        # Headloss
        hl_map = {0: "H-W", 1: "D-W", 2: "C-M"}
        hl_str = hl_map.get(int(opts.headloss_formula), "H-W")
        f.write(f" Headloss           \t{hl_str}\n")
        
        f.write(f" Specific Gravity   \t{opts.specific_gravity}\n")
        f.write(f" Viscosity          \t{opts.viscosity}\n")
        f.write(f" Trials             \t{opts.trials}\n")
        f.write(f" Accuracy           \t{opts.accuracy}\n")
        f.write(f" CHECKFREQ          \t{opts.checkfreq}\n")
        f.write(f" MAXCHECK           \t{opts.maxcheck}\n")
        f.write(f" DAMPLIMIT          \t{opts.damplimit}\n")
        f.write(f" Unbalanced         \t{opts.unbalanced} {opts.unbalanced_continue}\n")
        if opts.default_pattern:
            f.write(f" Pattern            \t{opts.default_pattern}\n")
        f.write(f" Demand Multiplier  \t{opts.demand_multiplier}\n")
        f.write(f" Emitter Exponent   \t{opts.emitter_exponent}\n")
        
        # Quality
        if opts.quality_type.name == "NONE":
            f.write(f" Quality            \tNONE\n")
        elif opts.quality_type.name == "CHEM":
            f.write(f" Quality            \tCHEMICAL {opts.chemical_name} {opts.chemical_units}\n")
        elif opts.quality_type.name == "AGE":
            f.write(f" Quality            \tAGE\n")
        elif opts.quality_type.name == "TRACE":
            f.write(f" Quality            \tTRACE {opts.trace_node}\n")
            
        f.write(f" Diffusivity        \t{opts.diffusivity}\n")
        f.write(f" Tolerance          \t{opts.quality_tolerance}\n")
        f.write("\n")
        
        f.write("[END]\n")

def import_scenario(project, filepath: str):
    """Import scenario data from INP file.
    
    Updates:
    - Demands
    - Initial Quality
    - Status
    - Controls
    - Rules
    - Energy
    - Options
    
    Args:
        project: EPANETProject instance
        filepath: Input file path
    """
    network = project.network
    
    current_section = None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
                
            if line.startswith('['):
                current_section = line[1:-1].upper()
                continue
                
            tokens = line.split()
            if not tokens: continue
            
            try:
                if current_section == "DEMANDS":
                    # Format: ID Demand Pattern
                    node_id = tokens[0]
                    if node_id in network.nodes:
                        node = network.nodes[node_id]
                        if len(tokens) >= 2:
                            node.base_demand = float(tokens[1])
                        if len(tokens) >= 3:
                            node.demand_pattern = tokens[2]
                            
                elif current_section == "QUALITY":
                    # Format: NodeID Value
                    node_id = tokens[0]
                    if node_id in network.nodes:
                        node = network.nodes[node_id]
                        if len(tokens) >= 2:
                            node.initial_quality = float(tokens[1])
                            
                elif current_section == "STATUS":
                    # Format: ID Status/Setting
                    link_id = tokens[0]
                    if link_id in network.links:
                        link = network.links[link_id]
                        if len(tokens) >= 2:
                            val = tokens[1]
                            # Try to determine if it's status or setting
                            if val.upper() in ['OPEN', 'CLOSED']:
                                link.initial_status = val.upper()
                            else:
                                try:
                                    link.initial_setting = float(val)
                                except ValueError:
                                    pass
                                    
                elif current_section == "CONTROLS":
                    # Replace controls? Or append? usually replace for scenario.
                    # But we need to clear them first.
                    # Let's clear on first control found? No, clear before loop.
                    # We'll handle clearing at the start of import if we see the section.
                    # For now, just append, but we should probably clear existing controls if we are importing a scenario.
                    # Let's assume the user wants to replace controls.
                    pass # TODO: Implement control parsing. It's complex text.
                    
                elif current_section == "RULES":
                    pass # TODO: Implement rule parsing.
                    
                elif current_section == "ENERGY":
                    # Global or Pump specific
                    keyword = tokens[0].upper()
                    if keyword == "GLOBAL":
                        param = tokens[1].upper()
                        val = tokens[2]
                        if param == "EFFICIENCY": network.options.global_efficiency = float(val)
                        elif param == "PRICE": network.options.global_price = float(val)
                    elif keyword == "DEMAND":
                        if tokens[1].upper() == "CHARGE":
                            network.options.demand_charge = float(tokens[2])
                            
                elif current_section == "OPTIONS":
                    keyword = tokens[0].upper()
                    if len(tokens) >= 2:
                        val = tokens[1]
                        opts = network.options
                        
                        if keyword == "UNITS": 
                            # Map string to Enum
                            try:
                                from core.constants import FlowUnits
                                opts.flow_units = FlowUnits[val.upper()]
                            except KeyError:
                                pass
                                
                        elif keyword == "HEADLOSS": 
                            from core.constants import HeadLossType
                            if val.upper() == "H-W": opts.headloss_formula = HeadLossType.HW
                            elif val.upper() == "D-W": opts.headloss_formula = HeadLossType.DW
                            elif val.upper() == "C-M": opts.headloss_formula = HeadLossType.CM
                            
                        elif keyword == "QUALITY": 
                            from core.constants import QualityType
                            qual_type = val.upper()
                            if qual_type == "NONE":
                                opts.quality_type = QualityType.NONE
                            elif qual_type == "CHEMICAL":
                                opts.quality_type = QualityType.CHEM
                                if len(tokens) > 2: opts.chemical_name = tokens[2]
                                if len(tokens) > 3: opts.chemical_units = tokens[3]
                            elif qual_type == "AGE":
                                opts.quality_type = QualityType.AGE
                            elif qual_type == "TRACE":
                                opts.quality_type = QualityType.TRACE
                                if len(tokens) > 2: opts.trace_node = tokens[2]
                                
                        elif keyword == "VISCOSITY": opts.viscosity = float(val)
                        elif keyword == "DIFFUSIVITY": opts.diffusivity = float(val)
                        elif keyword == "SPECIFIC": opts.specific_gravity = float(tokens[2]) # SPECIFIC GRAVITY
                        elif keyword == "TRIALS": opts.trials = int(val)
                        elif keyword == "ACCURACY": opts.accuracy = float(val)
                        elif keyword == "TOLERANCE": opts.quality_tolerance = float(val)
                        elif keyword == "PATTERN": opts.default_pattern = val
                        elif keyword == "DEMAND": 
                            if tokens[1].upper() == "MULTIPLIER": opts.demand_multiplier = float(tokens[2])
                        elif keyword == "CHECKFREQ": opts.checkfreq = int(val)
                        elif keyword == "MAXCHECK": opts.maxcheck = int(val)
                        elif keyword == "DAMPLIMIT": opts.damplimit = float(val)
                        elif keyword == "UNBALANCED": 
                            opts.unbalanced = val.upper()
                            if len(tokens) > 2: opts.unbalanced_continue = int(tokens[2])
                            
            except Exception as e:
                print(f"Error parsing line '{line}' in section {current_section}: {e}")
                continue
    
    # Note: Controls and Rules parsing is non-trivial and skipped for this simplified implementation.
    # In a full implementation, we would need a robust parser for these.


def export_network(project, filepath: str):
    """Export full network data to INP file using WNTR.
    
    Args:
        project: EPANETProject instance
        filepath: Output file path
    """
    import wntr
    
    # Sync internal model to WNTR model
    # Accessing protected method as we are in a core module helper
    if hasattr(project, '_sync_network_to_wntr'):
        project._sync_network_to_wntr()
        
    # Get WNTR model from engine
    wn = project.engine.wn
    
    if wn:
        try:
            # Write base INP file using WNTR
            wntr.network.write_inpfile(wn, filepath)
            
            # Append Controls and Rules manually
            # WNTR might not write them if they are not in the WNTR model
            # So we append them from our internal model
            
            # Read the file back to insert before [END]
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find [END]
            end_tag = "[END]"
            insert_pos = content.find(end_tag)
            
            new_content = ""
            controls_text = ""
            
            # Controls
            if project.network.controls:
                controls_text += "\n[CONTROLS]\n"
                for control in project.network.controls:
                    controls_text += f"{control.to_string()}\n"
                controls_text += "\n"
            
            # Rules
            if project.network.rules:
                controls_text += "\n[RULES]\n"
                for rule in project.network.rules:
                    controls_text += f"{rule.to_string()}\n"
                controls_text += "\n"
                
            if insert_pos != -1:
                new_content = content[:insert_pos] + controls_text + content[insert_pos:]
            else:
                new_content = content + controls_text + "\n[END]\n"
                
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
                    
        except Exception as e:
            import traceback
            print("Error exporting network to INP:")
            traceback.print_exc()
            # Also print some debug info about the model
            print("\nDebug Info:")
            try:
                print(f"Nodes: {len(wn.nodes)}")
                print(f"Links: {len(wn.links)}")
                print(f"Options: {wn.options}")
            except:
                pass
            raise e
    else:
        raise RuntimeError("No WNTR network model available to export.")

