# risklens/simulation/sampler.py

import math
import random


class DistributionSampler:
    def __init__(self, rng: random.Random):
        self._rng = rng

    def sample(self, distribution: str, sigma: float) -> float:
        if distribution == "normal":
            return self._rng.normalvariate(0.0, sigma)

        if distribution == "lognormal":
            # mean = 0 ensures median = 1.0
            return self._rng.lognormvariate(0.0, sigma)

        raise ValueError(f"Unsupported distribution: {distribution}")
