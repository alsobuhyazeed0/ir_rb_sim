from enum import Enum, auto


class RoundPhase(Enum):
    """Phases of the IR range-and-bearing communication cycle."""

    PHASE1 = auto()
    PHASE2 = auto()