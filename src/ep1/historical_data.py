from typing import List, Callable
from constants import DT, SCREEN_HEIGHT, SCREEN_WIDTH
from common import Updatable
import arcade, arcade.color
from arcade.arcade_types import Point, Vector

COLLECT_INTERVAL: float = 6.0
COLORS = [arcade.color.GREEN, arcade.color.BLUE, arcade.color.RED]
DX = 10

class HistoricalData(Updatable):
    data: List[List[float]]
    time_till_collect: float
    data_collector: Callable[[], List[float]]
    bottom_left: Point
    size: Vector
    
    def __init__(self, bottom_left: Point, size: Vector, data_collector: Callable[[], List[float]]):
        self.data = []
        self.time_till_collect = COLLECT_INTERVAL
        self.data_collector = data_collector
        self.bottom_left = bottom_left
        self.size = size
        self.collect_data()
    
    def collect_data(self):
        self.data.append(self.data_collector())
        if len(self.data) > 1:
            assert(len(self.data[-1]) == len(self.data[-2]))
        
    def update(self):
        self.time_till_collect -= DT
        if self.time_till_collect <= 0:
            self.time_till_collect += COLLECT_INTERVAL
            self.collect_data()
    
    def draw_outline(self) -> None:
        (x, y) = self.bottom_left
        (w, h) = self.size
        arcade.draw_line_strip(
            [
                (x, y + h),
                (x, y),
                (x + w, y),
            ],
            arcade.color.BLACK,
            3
        )
    
    def draw(self) -> None:
        self.draw_outline()
        (x, y) = self.bottom_left
        (w, h) = self.size
        while len(self.data) * DX > w:
            self.data.pop(0)
        for i in range(len(self.data[0])):
            points = []
            for di in range(len(self.data)):
                points.append((x + di * DX, y + self.data[di][i] * 10))
            arcade.draw_line_strip(
                points,
                COLORS[i],
                2
            )
