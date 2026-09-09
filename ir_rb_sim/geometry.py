import math
from dataclasses import dataclass
from ir_rb_sim.types.geometry_types import Pose

def normalize_angle_deg(angle_deg: float) -> float:
    return angle_deg % 360.0

def angular_diff_deg(a_deg: float, b_deg: float) -> float:
    return (a_deg - b_deg + 180.0) % 360.0 - 180.0

def relative_bearing_and_distance(observer: Pose, target: Pose) -> tuple[float, float]:

    dx = target.x - observer.x
    dy = target.y - observer.y
    distance = math.hypot(dx, dy)

    absolute_angle = math.degrees(math.atan2(dy, dx))
    relative_bearing = normalize_angle_deg(absolute_angle - observer.heading_deg)

    return relative_bearing, distance