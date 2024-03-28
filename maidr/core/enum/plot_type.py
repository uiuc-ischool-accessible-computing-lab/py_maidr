from enum import Enum


class PlotType(str, Enum):
    BAR = "bar"
    BOX = "box"
    DODGED = "dodged_bar"
    HEAT = "heat"
    HIST = "hist"
    LINE = "line"
    SCATTER = "point"
    STACKED = "stacked_bar"
