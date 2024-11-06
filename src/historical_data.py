from typing import List, Callable
from constants import DT, SCREEN_HEIGHT, SCREEN_WIDTH
from common import Updatable
import arcade, arcade.color
from arcade.arcade_types import Point, Vector
from enum import Enum
from dataclasses import dataclass

COLLECT_INTERVAL: float = 6.0
COLORS = [arcade.color.GREEN, arcade.color.PINK, arcade.color.BLUE]
DX = 10


class GraphMode(Enum):
    Lines = 0
    AreaPct = 1


@dataclass
class DataPoint:
    values: List[float]
    vertical_mark: bool


class HistoricalData(Updatable):
    data: List[DataPoint]
    time_till_collect: float
    data_collector: Callable[[], List[float]]
    bottom_left: Point
    size: Vector
    mode: GraphMode = GraphMode.AreaPct
    pending_mark: bool = False

    def __init__(
        self,
        bottom_left: Point,
        size: Vector,
        data_collector: Callable[[], List[float]],
    ):
        self.data = []
        self.time_till_collect = COLLECT_INTERVAL
        self.data_collector = data_collector
        self.bottom_left = bottom_left
        self.size = size
        self.collect_data()

    def value_count(self) -> int:
        return len(self.data[0].values)

    def add_vertical_mark(self) -> None:
        self.pending_mark = True

    def collect_data(self):
        self.data.append(DataPoint(self.data_collector(), self.pending_mark))
        self.pending_mark = False
        if len(self.data) > 1:
            assert len(self.data[-1].values) == len(self.data[-2].values)

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
            arcade.draw_line_strip(line, arcade.color.BLACK, 3)

    def draw_lines(self) -> None:
        (x, y) = self.bottom_left
        for i in range(self.value_count()):
            points = []
            for di in range(len(self.data)):
                points.append((x + di * DX, y + self.data[di].values[i] * 10))
            arcade.draw_line_strip(points, COLORS[i], 2)

    def draw_area_pct(self) -> None:
        (x, y) = self.bottom_left
        (w, h) = self.size
        points = []
        for i in range(self.value_count()):
            points.append([])
        for di in range(len(self.data)):
            tot = sum(self.data[di].values)
            cur = 0
            for i in range(self.value_count()):
                cur += self.data[di].values[i]
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

    def draw_mark(self, di: int) -> None:
        (x, y) = self.bottom_left
        (w, h) = self.size
        arcade.draw_line(x + di * DX, y, x + di * DX, y + h + 10, arcade.color.BLACK, 1)

    def draw_marks(self) -> None:
        for di in range(len(self.data)):
            if self.data[di].vertical_mark:
                self.draw_mark(di)
        if self.pending_mark:
            self.draw_mark(len(self.data))

    def draw(self) -> None:
        (w, h) = self.size
        while len(self.data) * DX > w:
            self.data.pop(0)
        match self.mode:
            case GraphMode.Lines:
                self.draw_lines()
            case GraphMode.AreaPct:
                self.draw_area_pct()
        self.draw_outline()
        self.draw_marks()
