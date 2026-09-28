from dataclasses import dataclass
import numpy as np
from .config import Config, DEFAULT_CONFIG
from .ranging import DetectFn


@dataclass(frozen=True)
class NoiseModel:
    ambient_noise_std_dac: float
    miss_detection_prob: float
    false_positive_prob: float

    @classmethod
    def from_config(cls, config: Config = DEFAULT_CONFIG) -> "NoiseModel":
        return cls(
            ambient_noise_std_dac=config.AMBIENT_NOISE_STD_DAC,
            miss_detection_prob=config.MISS_DETECTION_PROB,
            false_positive_prob=config.FALSE_POSITIVE_PROB,
        )

    def make_detect_fn(self, i_min: float, rng: np.random.Generator) -> DetectFn:
        def detect(dac_value: float) -> bool:
            noisy_dac = dac_value + rng.normal(0.0, self.ambient_noise_std_dac)
            ideal_hit = noisy_dac >= i_min

            if ideal_hit:
                return not (rng.random() < self.miss_detection_prob)
            else:
                return rng.random() < self.false_positive_prob

        return detect


DEFAULT_NOISE_MODEL = NoiseModel.from_config()