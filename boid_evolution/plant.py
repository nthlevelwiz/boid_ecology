"""Plant resource entity."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class Plant:
    position: np.ndarray
    energy_value: float
