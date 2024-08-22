import random

def rand(min: float, max: float) -> float:
    return random.random() * (max - min) + min