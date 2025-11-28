"""Export utilities for EPANET data and reports."""

import os
from datetime import datetime
from typing import Optional

class ExportUtils:
    """Utilities for exporting network data and generating reports."""
    
    @staticmethod
    def export_network_data(project, filepath: str, include_results: bool = False):
        """Export network data to text file.
        
        Args:
            project: EPANETProject instance
            filepath: Output file path
            include_results: Whether to include simulation results
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            # Header
            f.write("=" * 80 + "\n")
            f.write("EPANET Network Data Export\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Project Info
            f.write(f"Project: {project.network.title or 'Untitled'}\n")
            f.write(f"Notes: {project.network.notes or 'None'}\n\n")
            
            # Nodes
            f.write("-" * 80 + "\n")
            f.write("NODES\n")
            f.write("-" * 80 + "\n\n")
            
            # Junctions
            junctions = [n for n in project.network.nodes.values() 
                        if n.node_type.name == 'JUNCTION']
            if junctions:
                f.write("Junctions:\n")
                f.write(f"{'ID':<15} {'Elevation':<12} {'Demand':<12} {'Pattern':<15}\n")
                f.write("-" * 60 + "\n")
                for node in junctions:
                    f.write(f"{node.id:<15} {node.elevation:<12.2f} "
                           f"{node.base_demand:<12.2f} {node.demand_pattern or '-':<15}\n")
                f.write("\n")
            
            # Reservoirs
            reservoirs = [n for n in project.network.nodes.values() 
                         if n.node_type.name == 'RESERVOIR']
            if reservoirs:
                f.write("Reservoirs:\n")
                f.write(f"{'ID':<15} {'Head':<12} {'Pattern':<15}\n")
                f.write("-" * 45 + "\n")
                for node in reservoirs:
                    f.write(f"{node.id:<15} {node.total_head:<12.2f} "
                           f"{node.head_pattern or '-':<15}\n")
                f.write("\n")
            
            # Tanks
            tanks = [n for n in project.network.nodes.values() 
                    if n.node_type.name == 'TANK']
            if tanks:
                f.write("Tanks:\n")
                f.write(f"{'ID':<15} {'Elevation':<12} {'Init Level':<12} "
                       f"{'Min Level':<12} {'Max Level':<12} {'Diameter':<12}\n")
                f.write("-" * 80 + "\n")
                for node in tanks:
                    f.write(f"{node.id:<15} {node.elevation:<12.2f} "
                           f"{node.init_level:<12.2f} {node.min_level:<12.2f} "
                           f"{node.max_level:<12.2f} {node.diameter:<12.2f}\n")
                f.write("\n")
            
            # Links
            f.write("-" * 80 + "\n")
            f.write("LINKS\n")
            f.write("-" * 80 + "\n\n")
            
            # Pipes
            pipes = [l for l in project.network.links.values() 
                    if l.link_type.name == 'PIPE']
            if pipes:
                f.write("Pipes:\n")
                f.write(f"{'ID':<15} {'From':<12} {'To':<12} {'Length':<12} "
                       f"{'Diameter':<12} {'Roughness':<12}\n")
                f.write("-" * 80 + "\n")
                for link in pipes:
                    f.write(f"{link.id:<15} {link.from_node:<12} {link.to_node:<12} "
                           f"{link.length:<12.2f} {link.diameter:<12.2f} "
                           f"{link.roughness:<12.2f}\n")
                f.write("\n")
            
            # Pumps
            pumps = [l for l in project.network.links.values() 
                    if l.link_type.name == 'PUMP']
            if pumps:
                f.write("Pumps:\n")
                f.write(f"{'ID':<15} {'From':<12} {'To':<12} {'Power':<12} "
                       f"{'Curve':<15}\n")
                f.write("-" * 70 + "\n")
                for link in pumps:
                    f.write(f"{link.id:<15} {link.from_node:<12} {link.to_node:<12} "
                           f"{link.power:<12.2f} {link.pump_curve or '-':<15}\n")
                f.write("\n")
            
            # Valves
            valves = [l for l in project.network.links.values() 
                     if l.link_type.name in ['PRV', 'PSV', 'PBV', 'FCV', 'TCV', 'GPV']]
            if valves:
                f.write("Valves:\n")
                f.write(f"{'ID':<15} {'Type':<8} {'From':<12} {'To':<12} "
                       f"{'Setting':<12}\n")
                f.write("-" * 65 + "\n")
                for link in valves:
                    f.write(f"{link.id:<15} {link.link_type.name:<8} "
                           f"{link.from_node:<12} {link.to_node:<12} "
                           f"{link.valve_setting:<12.2f}\n")
                f.write("\n")
            
            # Patterns
            if project.network.patterns:
                f.write("-" * 80 + "\n")
                f.write("PATTERNS\n")
                f.write("-" * 80 + "\n\n")
                for pattern_id, pattern in project.network.patterns.items():
                    f.write(f"Pattern: {pattern_id}\n")
                    f.write(f"Multipliers: {' '.join(f'{m:.2f}' for m in pattern.multipliers)}\n\n")
            
            # Curves
            if project.network.curves:
                f.write("-" * 80 + "\n")
                f.write("CURVES\n")
                f.write("-" * 80 + "\n\n")
                for curve_id, curve in project.network.curves.items():
                    f.write(f"Curve: {curve_id} (Type: {curve.curve_type})\n")
                    f.write(f"{'X':<15} {'Y':<15}\n")
                    f.write("-" * 30 + "\n")
                    for x, y in zip(curve.x_values, curve.y_values):
                        f.write(f"{x:<15.2f} {y:<15.2f}\n")
                    f.write("\n")
            
            # Results (if requested and available)
            if include_results and project.has_results():
                f.write("-" * 80 + "\n")
                f.write("SIMULATION RESULTS SUMMARY\n")
                f.write("-" * 80 + "\n\n")
                f.write("Note: Full results available in separate report.\n\n")
    
    @staticmethod
    def export_results_csv(project, filepath: str):
        """Export simulation results to CSV file.
        
        Args:
            project: EPANETProject instance
            filepath: Output file path
        """
        if not project.has_results():
            raise ValueError("No simulation results available")
        
        import csv
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Node results
            writer.writerow(['Node Results'])
            writer.writerow(['ID', 'Demand', 'Head', 'Pressure', 'Quality'])
            
            for node_id, node in project.network.nodes.items():
                writer.writerow([
                    node_id,
                    f"{node.demand:.2f}",
                    f"{node.head:.2f}",
                    f"{node.pressure:.2f}",
                    f"{node.quality:.2f}"
                ])
            
            writer.writerow([])  # Empty row
            
            # Link results
            writer.writerow(['Link Results'])
            writer.writerow(['ID', 'Flow', 'Velocity', 'Headloss'])
            
            for link_id, link in project.network.links.items():
                writer.writerow([
                    link_id,
                    f"{link.flow:.2f}",
                    f"{link.velocity:.2f}",
                    f"{link.headloss:.2f}"
                ])
    
    @staticmethod
    def generate_full_report(project, filepath: str):
        """Generate comprehensive analysis report.
        
        Args:
            project: EPANETProject instance
            filepath: Output file path
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            # Title
            f.write("=" * 80 + "\n")
            f.write("EPANET ANALYSIS REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Project: {project.network.title or 'Untitled'}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Network Summary
            f.write("-" * 80 + "\n")
            f.write("NETWORK SUMMARY\n")
            f.write("-" * 80 + "\n\n")
            
            num_junctions = sum(1 for n in project.network.nodes.values() 
                               if n.node_type.name == 'JUNCTION')
            num_reservoirs = sum(1 for n in project.network.nodes.values() 
                                if n.node_type.name == 'RESERVOIR')
            num_tanks = sum(1 for n in project.network.nodes.values() 
                           if n.node_type.name == 'TANK')
            num_pipes = sum(1 for l in project.network.links.values() 
                           if l.link_type.name == 'PIPE')
            num_pumps = sum(1 for l in project.network.links.values() 
                           if l.link_type.name == 'PUMP')
            num_valves = sum(1 for l in project.network.links.values() 
                            if l.link_type.name not in ['PIPE', 'PUMP'])
            
            f.write(f"Junctions:   {num_junctions}\n")
            f.write(f"Reservoirs:  {num_reservoirs}\n")
            f.write(f"Tanks:       {num_tanks}\n")
            f.write(f"Pipes:       {num_pipes}\n")
            f.write(f"Pumps:       {num_pumps}\n")
            f.write(f"Valves:      {num_valves}\n")
            f.write(f"Patterns:    {len(project.network.patterns)}\n")
            f.write(f"Curves:      {len(project.network.curves)}\n\n")
            
            # Analysis Options
            f.write("-" * 80 + "\n")
            f.write("ANALYSIS OPTIONS\n")
            f.write("-" * 80 + "\n\n")
            
            opts = project.network.options
            f.write(f"Flow Units:       {opts.flow_units}\n")
            f.write(f"Headloss Formula: {opts.headloss}\n")
            f.write(f"Quality Analysis: {opts.quality}\n")
            f.write(f"Duration:         {opts.duration} hours\n")
            f.write(f"Hydraulic Step:   {opts.hydraulic_timestep} hours\n")
            f.write(f"Quality Step:     {opts.quality_timestep} minutes\n\n")
            
            # Simulation Results
            if project.has_results():
                f.write("-" * 80 + "\n")
                f.write("SIMULATION RESULTS\n")
                f.write("-" * 80 + "\n\n")
                f.write("Results available. See detailed output for complete data.\n\n")
            else:
                f.write("-" * 80 + "\n")
                f.write("No simulation results available.\n")
                f.write("Run hydraulic analysis to generate results.\n")
                f.write("-" * 80 + "\n\n")
