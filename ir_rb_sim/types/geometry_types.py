from dataclasses import dataclass


@dataclass(frozen=True)
class Pose:
    x: float
    y: float
    heading_deg: float