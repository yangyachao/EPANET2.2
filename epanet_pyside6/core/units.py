"""Unit system utilities for EPANET."""

from core.constants import FlowUnits


def is_metric(flow_units: FlowUnits) -> bool:
    """Check if flow units are metric (SI).
    
    Args:
        flow_units: Flow units enum value
        
    Returns:
        True if metric, False if US Customary
    """
    metric_units = {
        FlowUnits.LPS,  # liters per second
        FlowUnits.LPM,  # liters per minute
        FlowUnits.MLD,  # megaliters per day
        FlowUnits.CMH,  # cubic meters per hour
        FlowUnits.CMD,  # cubic meters per day
    }
    return flow_units in metric_units


def get_unit_label(param_type: str, flow_units: FlowUnits) -> str:
    """Get the unit label for a parameter based on flow units.
    
    Args:
        param_type: Type of parameter (e.g., 'elevation', 'diameter', 'flow')
        flow_units: Current flow units setting
        
    Returns:
        Unit label string (e.g., 'm', 'ft', 'mm', 'in')
    """
    metric = is_metric(flow_units)
    
    # Unit mappings
    units = {
        'elevation': 'm' if metric else 'ft',
        'head': 'm' if metric else 'ft',
        'pressure': 'm' if metric else 'psi',
        'diameter': 'mm' if metric else 'in',
        'length': 'm' if metric else 'ft',
        'roughness': 'mm' if metric else '',  # Depends on formula
        'flow': _get_flow_label(flow_units),
        'velocity': 'm/s' if metric else 'ft/s',
        'headloss': 'm/km' if metric else 'ft/kft',
        'demand': 'L/s' if metric else 'gpm',
        'level': 'm' if metric else 'ft',
        'volume': 'm³' if metric else 'ft³',
    }
    
    return units.get(param_type.lower(), '')


def _get_flow_label(flow_units: FlowUnits) -> str:
    """Get the flow unit label.
    
    Args:
        flow_units: Flow units enum value
        
    Returns:
        Flow unit label string
    """
    labels = {
        FlowUnits.CFS: 'cfs',
        FlowUnits.GPM: 'gpm',
        FlowUnits.MGD: 'MGD',
        FlowUnits.IMGD: 'IMGD',
        FlowUnits.AFD: 'AFD',
        FlowUnits.LPS: 'L/s',
        FlowUnits.LPM: 'L/min',
        FlowUnits.MLD: 'ML/d',
        FlowUnits.CMH: 'm³/h',
        FlowUnits.CMD: 'm³/d',
    }
    return labels.get(flow_units, '')


def get_flow_unit_name(flow_units: FlowUnits) -> str:
    """Get the full name of flow units.
    
    Args:
        flow_units: Flow units enum value
        
    Returns:
        Full name string
    """
    names = {
        FlowUnits.CFS: 'Cubic Feet per Second',
        FlowUnits.GPM: 'Gallons per Minute',
        FlowUnits.MGD: 'Million Gallons per Day',
        FlowUnits.IMGD: 'Imperial Million Gallons per Day',
        FlowUnits.AFD: 'Acre-Feet per Day',
        FlowUnits.LPS: 'Liters per Second',
        FlowUnits.LPM: 'Liters per Minute',
        FlowUnits.MLD: 'Megaliters per Day',
        FlowUnits.CMH: 'Cubic Meters per Hour',
        FlowUnits.CMD: 'Cubic Meters per Day',
    }
    return names.get(flow_units, 'Unknown')


# Unit Conversion Functions

def convert_diameter_to_mm(value: float, from_flow_units: FlowUnits) -> float:
    """Convert diameter to millimeters.
    
    Args:
        value: Diameter value in current units
        from_flow_units: Current flow units
        
    Returns:
        Diameter in millimeters
    """
    if is_metric(from_flow_units):
        # Already in mm
        return value
    else:
        # Convert from inches to mm
        return value * 25.4


def convert_diameter_from_mm(value: float, to_flow_units: FlowUnits) -> float:
    """Convert diameter from millimeters to target units.
    
    Args:
        value: Diameter value in millimeters
        to_flow_units: Target flow units
        
    Returns:
        Diameter in target units (mm for metric, inches for US)
    """
    if is_metric(to_flow_units):
        # Keep in mm
        return value
    else:
        # Convert from mm to inches
        return value / 25.4


def convert_length_to_m(value: float, from_flow_units: FlowUnits) -> float:
    """Convert length to meters.
    
    Args:
        value: Length value in current units
        from_flow_units: Current flow units
        
    Returns:
        Length in meters
    """
    if is_metric(from_flow_units):
        # Already in meters
        return value
    else:
        # Convert from feet to meters
        return value * 0.3048


def convert_length_from_m(value: float, to_flow_units: FlowUnits) -> float:
    """Convert length from meters to target units.
    
    Args:
        value: Length value in meters
        to_flow_units: Target flow units
        
    Returns:
        Length in target units (m for metric, ft for US)
    """
    if is_metric(to_flow_units):
        # Keep in meters
        return value
    else:
        # Convert from meters to feet
        return value / 0.3048
