from arcade.arcade_types import Point, Vector
from typing import List

Vec = List[float]


class Updatable:
    def update(self):
        pass


def len2(v: Vector) -> float:
    return v[0] ** 2 + v[1] ** 2


def max_norm(v: Vec, max_len: float) -> None:
    if max_len == 0:
        v[0] = 0
        v[1] = 0
        return
    factor = len2(v) / max_len**2
    if factor > 1:
        factor = 1 / factor**0.5
        v[0] *= factor
        v[1] *= factor
