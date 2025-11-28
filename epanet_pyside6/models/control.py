"""Control and Rule models for EPANET."""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class SimpleControl:
    """Simple control statement.
    
    Format: LINK <linkid> <status> IF NODE <nodeid> <operator> <value>
    or: LINK <linkid> <status> AT TIME <time>
    or: LINK <linkid> <status> AT CLOCKTIME <clocktime>
    """
    link_id: str
    status: str  # OPEN, CLOSED, or numeric setting
    control_type: str  # IF_NODE, AT_TIME, AT_CLOCKTIME
    node_id: Optional[str] = None
    operator: Optional[str] = None  # ABOVE, BELOW
    value: Optional[float] = None
    time: Optional[str] = None  # For AT_TIME or AT_CLOCKTIME
    
    def to_string(self) -> str:
        """Convert to EPANET control string."""
        if self.control_type == "IF_NODE":
            val_str = f"{self.value:g}"
            return f"LINK {self.link_id} {self.status} IF NODE {self.node_id} {self.operator} {val_str}"
        elif self.control_type == "AT_TIME":
            return f"LINK {self.link_id} {self.status} AT TIME {self.time}"
        elif self.control_type == "AT_CLOCKTIME":
            return f"LINK {self.link_id} {self.status} AT CLOCKTIME {self.time}"
        return ""
    
    @staticmethod
    def from_string(text: str) -> Optional['SimpleControl']:
        """Parse EPANET control string."""
        try:
            parts = text.strip().split()
            if len(parts) < 4 or parts[0].upper() != "LINK":
                return None
            
            link_id = parts[1]
            status = parts[2]
            
            if "IF" in [p.upper() for p in parts]:
                # IF NODE control
                if_idx = [i for i, p in enumerate(parts) if p.upper() == "IF"][0]
                node_idx = [i for i, p in enumerate(parts) if p.upper() == "NODE"][0]
                node_id = parts[node_idx + 1]
                operator = parts[node_idx + 2]
                value = float(parts[node_idx + 3])
                
                return SimpleControl(
                    link_id=link_id,
                    status=status,
                    control_type="IF_NODE",
                    node_id=node_id,
                    operator=operator,
                    value=value
                )
            elif "AT" in [p.upper() for p in parts]:
                # AT TIME or AT CLOCKTIME
                at_idx = [i for i, p in enumerate(parts) if p.upper() == "AT"][0]
                time_type = parts[at_idx + 1].upper()
                time_value = parts[at_idx + 2]
                
                control_type = "AT_TIME" if time_type == "TIME" else "AT_CLOCKTIME"
                
                return SimpleControl(
                    link_id=link_id,
                    status=status,
                    control_type=control_type,
                    time=time_value
                )
        except (IndexError, ValueError):
            return None
        
        return None


@dataclass
class Rule:
    """Rule-based control.
    
    Format:
    RULE <ruleid>
    IF <condition>
    THEN <action>
    ELSE <action>
    PRIORITY <value>
    """
    rule_id: str
    conditions: List[str]  # IF/AND/OR conditions
    then_actions: List[str]  # THEN actions
    else_actions: List[str]  # ELSE actions (optional)
    priority: Optional[float] = None
    
    def to_string(self) -> str:
        """Convert to EPANET rule string."""
        lines = [f"RULE {self.rule_id}"]
        
        for condition in self.conditions:
            lines.append(condition)
        
        for action in self.then_actions:
            lines.append(action)
        
        for action in self.else_actions:
            lines.append(action)
        
        if self.priority is not None:
            lines.append(f"PRIORITY {self.priority}")
        
        return "\n".join(lines)
    
    @staticmethod
    def from_string(text: str) -> Optional['Rule']:
        """Parse EPANET rule string."""
        try:
            lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
            
            if not lines or not lines[0].upper().startswith("RULE"):
                return None
            
            rule_id = lines[0].split(None, 1)[1] if len(lines[0].split(None, 1)) > 1 else ""
            
            conditions = []
            then_actions = []
            else_actions = []
            priority = None
            
            current_section = None
            
            for line in lines[1:]:
                upper_line = line.upper()
                
                if upper_line.startswith("IF") or upper_line.startswith("AND") or upper_line.startswith("OR"):
                    current_section = "conditions"
                    conditions.append(line)
                elif upper_line.startswith("THEN"):
                    current_section = "then"
                    then_actions.append(line)
                elif upper_line.startswith("ELSE"):
                    current_section = "else"
                    else_actions.append(line)
                elif upper_line.startswith("PRIORITY"):
                    priority = float(line.split()[1])
                elif current_section == "then":
                    then_actions.append(line)
                elif current_section == "else":
                    else_actions.append(line)
            
            return Rule(
                rule_id=rule_id,
                conditions=conditions,
                then_actions=then_actions,
                else_actions=else_actions,
                priority=priority
            )
        except (IndexError, ValueError):
            return None
