from typing import Deque, Optional
from arcade import Text, color
from common import Updatable
from dataclasses import dataclass
from constants import DT
from collections import deque
from arcade.arcade_types import Point, Vector


@dataclass
class LogLine:
    raw_text: str
    text: Text
    time_log: float

    def time_elapsed(self, cur_time: float) -> float:
        return cur_time - self.time_log

    def time_str(self, cur_time: float) -> str:
        elapsed = self.time_elapsed(cur_time)
        minutes, seconds = divmod(elapsed, 60)
        if minutes > 0:
            return f"{minutes:.0f}m"
        else:
            return f"{seconds:.0f}s"

    def draw(self, cur_time: float, y: float) -> None:
        self.text.y = y
        self.text.text = f"{self.raw_text} ({self.time_str(cur_time)} ago)"
        self.text.draw()


class Logs(Updatable):
    cur_time: float = 0
    LINE_SIZE: int = 14
    TEXT_DY: float = 18

    def __init__(self, top_left: Point, size: Vector) -> None:
        self.texts: Deque[LogLine] = deque()
        self.top_left: Point = top_left
        self.size: Vector = size
        self.logs_text = Text(
            "Logs:", top_left[0], top_left[1], color.BLACK, self.TEXT_DY - 2
        )

    def max_size(self) -> int:
        return int((self.size[1] - self.TEXT_DY) / self.LINE_SIZE)

    def update(self) -> None:
        self.cur_time += DT

    def pop_old(self) -> None:
        while len(self.texts) > self.max_size():
            self.texts.popleft()

    def last_log(self) -> Optional[LogLine]:
        if len(self.texts) > 0:
            return self.texts[-1]
        else:
            return None

    def draw(self) -> None:
        self.logs_text.draw()
        for i, text in enumerate(reversed(self.texts)):
            text.draw(
                self.cur_time, self.top_left[1] - i * self.LINE_SIZE - self.TEXT_DY
            )

    def log(self, txt: str) -> None:
        self.texts.append(
            LogLine(
                txt,
                Text(txt, self.top_left[0], 10, color.BLACK, self.LINE_SIZE - 4),
                self.cur_time,
            )
        )
        self.pop_old()
