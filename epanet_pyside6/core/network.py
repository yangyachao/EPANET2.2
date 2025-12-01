"""Network data container."""

from typing import Dict, List, Optional
from models import Node, Junction, Reservoir, Tank
from models import Link, Pipe, Pump, Valve
from models import Pattern, Curve, Options
from models.control import SimpleControl, Rule


class Network:
    """Container for all network data."""
    
    def __init__(self):
        """Initialize empty network."""
        self.nodes: Dict[str, Node] = {}
        self.links: Dict[str, Link] = {}
        self.patterns: Dict[str, Pattern] = {}
        self.curves: Dict[str, Curve] = {}
        self.controls: List[SimpleControl] = []
        self.rules: List[Rule] = []
        self.labels: Dict[str, Any] = {} # Dict[str, Label]
        self.options: Options = Options()
        
        # Project metadata
        self.title: List[str] = ["", "", ""]
        self.notes: str = ""
        
        # Calibration Data: {parameter_name: file_path}
        self.calibration_data: Dict[str, str] = {}
        
        # Map dimensions
        # Initialize with a default 10000x10000 canvas to prevent jumps
        self.map_bounds: Dict[str, float] = {
            'min_x': 0.0,
            'min_y': 0.0,
            'max_x': 10000.0,
            'max_y': 10000.0
        }
        self.map_units: str = "None" # Feet, Meters, Degrees, None
    
    def clear(self):
        """Clear all network data."""
        self.nodes.clear()
        self.links.clear()
        self.patterns.clear()
        self.curves.clear()
        self.controls.clear()
        self.rules.clear()
        self.options = Options()
        self.title = ["", "", ""]
        self.notes = ""
        self.calibration_data.clear()
        self.map_units = "None"
        self.map_bounds = {
            'min_x': 0.0,
            'min_y': 0.0,
            'max_x': 10000.0,
            'max_y': 10000.0
        }
    
    # Node operations
    
    def add_node(self, node: Node):
        """Add a node to the network."""
        if node.id in self.nodes:
            raise ValueError(f"Node {node.id} already exists")
        self.nodes[node.id] = node
        self._update_map_bounds(node.x, node.y)
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get node by ID."""
        return self.nodes.get(node_id)
    
    def remove_node(self, node_id: str):
        """Remove node from network."""
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} does not exist")
            
        # Check if node is referenced by any links
        for link in self.links.values():
            if link.from_node == node_id or link.to_node == node_id:
                raise ValueError(
                    f"Cannot delete node {node_id}: "
                    f"it is connected to link {link.id}"
                )
        del self.nodes[node_id]
    
    def get_junctions(self) -> List[Junction]:
        """Get all junctions."""
        return [n for n in self.nodes.values() if isinstance(n, Junction)]
    
    def get_reservoirs(self) -> List[Reservoir]:
        """Get all reservoirs."""
        return [n for n in self.nodes.values() if isinstance(n, Reservoir)]
    
    def get_tanks(self) -> List[Tank]:
        """Get all tanks."""
        return [n for n in self.nodes.values() if isinstance(n, Tank)]
    
    # Link operations
    
    def add_link(self, link: Link):
        """Add a link to the network."""
        if link.id in self.links:
            raise ValueError(f"Link {link.id} already exists")
        
        # Verify nodes exist
        if link.from_node not in self.nodes:
            raise ValueError(f"From node {link.from_node} does not exist")
        if link.to_node not in self.nodes:
            raise ValueError(f"To node {link.to_node} does not exist")
        
        self.links[link.id] = link
    
    def get_link(self, link_id: str) -> Optional[Link]:
        """Get link by ID."""
        return self.links.get(link_id)
    
    def remove_link(self, link_id: str):
        """Remove link from network."""
        if link_id in self.links:
            del self.links[link_id]
    
    def get_pipes(self) -> List[Pipe]:
        """Get all pipes."""
        return [l for l in self.links.values() if isinstance(l, Pipe)]
    
    def get_pumps(self) -> List[Pump]:
        """Get all pumps."""
        return [l for l in self.links.values() if isinstance(l, Pump)]
    
    def get_valves(self) -> List[Valve]:
        """Get all valves."""
        return [l for l in self.links.values() if isinstance(l, Valve)]
    
    # Pattern operations
    
    def add_pattern(self, pattern: Pattern):
        """Add a pattern to the network."""
        if pattern.id in self.patterns:
            raise ValueError(f"Pattern {pattern.id} already exists")
        self.patterns[pattern.id] = pattern
    
    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Get pattern by ID."""
        return self.patterns.get(pattern_id)
    
    def remove_pattern(self, pattern_id: str):
        """Remove pattern from network."""
        if pattern_id in self.patterns:
            # Check if pattern is referenced
            for node in self.nodes.values():
                if isinstance(node, Junction) and node.demand_pattern == pattern_id:
                    raise ValueError(
                        f"Cannot delete pattern {pattern_id}: "
                        f"it is referenced by junction {node.id}"
                    )
            del self.patterns[pattern_id]
    
    # Curve operations
    
    def add_curve(self, curve: Curve):
        """Add a curve to the network."""
        if curve.id in self.curves:
            raise ValueError(f"Curve {curve.id} already exists")
        self.curves[curve.id] = curve
    
    def get_curve(self, curve_id: str) -> Optional[Curve]:
        """Get curve by ID."""
        return self.curves.get(curve_id)
    
    def remove_curve(self, curve_id: str):
        """Remove curve from network."""
        if curve_id in self.curves:
            # Check if curve is referenced
            for link in self.links.values():
                if isinstance(link, Pump) and link.pump_curve == curve_id:
                    raise ValueError(
                        f"Cannot delete curve {curve_id}: "
                        f"it is referenced by pump {link.id}"
                    )
            del self.curves[curve_id]
            
    # Label operations
    
    def add_label(self, label):
        """Add a label to the network."""
        if label.id in self.labels:
            raise ValueError(f"Label {label.id} already exists")
        self.labels[label.id] = label
        
    def get_label(self, label_id: str):
        """Get label by ID."""
        return self.labels.get(label_id)
        
    def remove_label(self, label_id: str):
        """Remove label from network."""
        if label_id in self.labels:
            del self.labels[label_id]
    
    # Utility methods
    
    def _update_map_bounds(self, x: float, y: float):
        """Update map bounds based on node coordinates."""
        self.map_bounds['min_x'] = min(self.map_bounds['min_x'], x)
        self.map_bounds['min_y'] = min(self.map_bounds['min_y'], y)
        self.map_bounds['max_x'] = max(self.map_bounds['max_x'], x)
        self.map_bounds['max_y'] = max(self.map_bounds['max_y'], y)
    
    def get_node_count(self) -> int:
        """Get total number of nodes."""
        return len(self.nodes)
    
    def get_link_count(self) -> int:
        """Get total number of links."""
        return len(self.links)
    
    @property
    def graph(self):
        """Get networkx graph representation."""
        import networkx as nx
        G = nx.MultiDiGraph()
        
        for node_id, node in self.nodes.items():
            G.add_node(node_id, pos=(node.x, node.y))
            
        for link_id, link in self.links.items():
            G.add_edge(link.from_node, link.to_node, id=link_id, weight=link.length if hasattr(link, 'length') else 0)
            
        return G

    def validate(self) -> List[str]:
        """Validate network data.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Check for isolated nodes
        connected_nodes = set()
        for link in self.links.values():
            connected_nodes.add(link.from_node)
            connected_nodes.add(link.to_node)
        
        for node_id in self.nodes:
            if node_id not in connected_nodes:
                errors.append(f"Node {node_id} is not connected to any links")
        
        # Check for duplicate coordinates
        coords = {}
        for node in self.nodes.values():
            coord = (node.x, node.y)
            if coord in coords:
                errors.append(
                    f"Nodes {coords[coord]} and {node.id} "
                    f"have the same coordinates"
                )
            coords[coord] = node.id
        
        return errors
