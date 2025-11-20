"""Constants for EPANET API and GUI."""

from enum import IntEnum

# EPANET API Constants
EN_MAXID = 31
EN_MAXMSG = 255

# Node Types
class NodeType(IntEnum):
    JUNCTION = 0
    RESERVOIR = 1
    TANK = 2

# Link Types
class LinkType(IntEnum):
    CVPIPE = 0
    PIPE = 1
    PUMP = 2
    PRV = 3
    PSV = 4
    PBV = 5
    FCV = 6
    TCV = 7
    GPV = 8

# Quality Analysis Types
class QualityType(IntEnum):
    NONE = 0
    CHEM = 1
    AGE = 2
    TRACE = 3

# Flow Units
class FlowUnits(IntEnum):
    CFS = 0   # cubic feet per second
    GPM = 1   # gallons per minute
    MGD = 2   # million gallons per day
    IMGD = 3  # imperial MGD
    AFD = 4   # acre-feet per day
    LPS = 5   # liters per second
    LPM = 6   # liters per minute
    MLD = 7   # million liters per day
    CMH = 8   # cubic meters per hour
    CMD = 9   # cubic meters per day

# Head Loss Formulas
class HeadLossType(IntEnum):
    HW = 0  # Hazen-Williams
    DW = 1  # Darcy-Weisbach
    CM = 2  # Chezy-Manning

# Link Status
class LinkStatus(IntEnum):
    CLOSED = 0
    OPEN = 1
    CV = 2

# Mixing Models
class MixingModel(IntEnum):
    MIX1 = 0  # Complete mixing
    MIX2 = 1  # 2-compartment mixing
    FIFO = 2  # First in, first out
    LIFO = 3  # Last in, first out

# Source Types
class SourceType(IntEnum):
    CONCEN = 0
    MASS = 1
    SETPOINT = 2
    FLOWPACED = 3

# Node Parameters
class NodeParam(IntEnum):
    ELEVATION = 0
    BASEDEMAND = 1
    PATTERN = 2
    EMITTER = 3
    INITQUAL = 4
    SOURCEQUAL = 5
    SOURCEPAT = 6
    SOURCETYPE = 7
    TANKLEVEL = 8
    DEMAND = 9
    HEAD = 10
    PRESSURE = 11
    QUALITY = 12
    SOURCEMASS = 13

# Link Parameters
class LinkParam(IntEnum):
    DIAMETER = 0
    LENGTH = 1
    ROUGHNESS = 2
    MINORLOSS = 3
    INITSTATUS = 4
    INITSETTING = 5
    KBULK = 6
    KWALL = 7
    FLOW = 8
    VELOCITY = 9
    HEADLOSS = 10
    STATUS = 11
    SETTING = 12
    ENERGY = 13

# Time Parameters
class TimeParam(IntEnum):
    DURATION = 0
    HYDSTEP = 1
    QUALSTEP = 2
    PATTERNSTEP = 3
    PATTERNSTART = 4
    REPORTSTEP = 5
    REPORTSTART = 6
    RULESTEP = 7
    STATISTIC = 8
    PERIODS = 9

# GUI Constants
MAXINTERVALS = 4
SYMBOLSIZE = 4
PIXTOL = 5

# Default Colors
DEFAULT_LEGEND_COLORS = [
    (255, 0, 0),      # Red
    (255, 255, 0),    # Yellow
    (0, 255, 0),      # Green
    (0, 255, 255),    # Cyan
    (0, 0, 255),      # Blue
]

# Map Units
class MapUnits(IntEnum):
    FEET = 0
    METERS = 1
    DEGREES = 2
    NONE = 3
