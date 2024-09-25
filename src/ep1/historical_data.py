from typing import DefaultDict, List, Callable, Dict
from collections import defaultdict
from constants import DT, SCREEN_HEIGHT, SCREEN_WIDTH
from common import Updatable
import arcade, arcade.color
from arcade import Sprite
from arcade.arcade_types import Point, Vector

COLLECT_INTERVAL: float = 6.0
COLORS = [arcade.color.GREEN, arcade.color.BLUE, arcade.color.RED]

class HistoricalData(Updatable):
    data: List[List[float]]
    time_till_collect: float
    data_collector: Callable[[], List[float]]
    
    def __init__(self, data_collector: Callable[[], List[float]]):
        self.data = []
        self.time_till_collect = COLLECT_INTERVAL
        self.data_collector = data_collector
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
    
    def draw(self):
        x = SCREEN_WIDTH - 450
        y = SCREEN_HEIGHT / 2
        arcade.draw_line_strip(
            [
                (x, y + 200),
                (x, y),
                (x + 400, y),
            ],
            arcade.color.BLACK,
            3
        )
        for i in range(len(self.data[0])):
            points = []
            for di in range(len(self.data)):
                points.append((x + di * 10, y + self.data[di][i] * 10))
            arcade.draw_line_strip(
                points,
                COLORS[i],
                2
            )
