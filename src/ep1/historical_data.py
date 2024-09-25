from typing import List, Callable
from constants import DT, SCREEN_HEIGHT, SCREEN_WIDTH
from common import Updatable
import arcade, arcade.color
from arcade.arcade_types import Point, Vector
from enum import Enum

COLLECT_INTERVAL: float = 6.0
COLORS = [arcade.color.GREEN, arcade.color.BLUE, arcade.color.RED]
DX = 10

class GraphMode(Enum):
    Lines = 0
    AreaPct = 1


class HistoricalData(Updatable):
    data: List[List[float]]
    time_till_collect: float
    data_collector: Callable[[], List[float]]
    bottom_left: Point
    size: Vector
    mode: GraphMode = GraphMode.AreaPct
    
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
        for line in [
            [
                (x, y + h),
                (x, y),
                (x + w, y),
            ],
            [
                (x - 7, y + h - 10),
                (x, y + h),
                (x + 7, y + h - 10),
            ],
            [
                (x + w - 10, y - 7),
                (x + w, y),
                (x + w - 10, y + 7),
            ],
        ]:
            arcade.draw_line_strip(
                line,
                arcade.color.BLACK,
                3
            )
    
    def draw_lines(self) -> None:
        (x, y) = self.bottom_left
        for i in range(len(self.data[0])):
            points = []
            for di in range(len(self.data)):
                points.append((x + di * DX, y + self.data[di][i] * 10))
            arcade.draw_line_strip(
                points,
                COLORS[i],
                2
            )
    
    def draw_area_pct(self) -> None:
        (x, y) = self.bottom_left
        (w, h) = self.size
        points = []
        for i in range(len(self.data[0])):
            points.append([])
        for di in range(len(self.data)):
            tot = sum(self.data[di])
            cur = 0
            for i in range(len(self.data[di])):
                cur += self.data[di][i]
                pct = cur / tot if tot > 0 else 0
                points[i].append((x + di * DX, y + pct * h))
        for ps in points:
            ps.append((ps[-1][0] + DX, ps[-1][1]))
        points.insert(0, [(x, y), (x + DX * len(self.data), y)])
        for i in range(len(points) - 1):
            arcade.draw_polygon_filled(
                points[i] + points[i + 1][::-1],
                COLORS[i],
            )
            
    
    def draw(self) -> None:
        self.draw_outline()
        (w, h) = self.size
        while len(self.data) * DX > w:
            self.data.pop(0)
        match self.mode:
            case GraphMode.Lines:
                self.draw_lines()
            case GraphMode.AreaPct:
                self.draw_area_pct()
