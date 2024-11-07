from arcade import Sprite, SpriteList, Text, color
from typing import List, cast
import arcade


class SliderButton(Sprite):
    def __init__(
        self, left: float, top: float, height: float, increase: bool, parent: "Slider"
    ) -> None:
        super().__init__(
            ":resources:onscreen_controls/shaded_light/%s.png"
            % ("right" if increase else "left"),
            scale=height / 80.0,
        )
        self.increase: bool = increase
        self.parent: Slider = parent
        self.left = left
        self.top = top

    def on_click(self) -> None:
        self.parent.click(self.increase)


class Slider:
    ALL_BUTTONS: SpriteList = SpriteList(use_spatial_hash=True)
    INSTANCES: List["Slider"] = []

    @staticmethod
    def draw_all() -> None:
        Slider.ALL_BUTTONS.draw()
        for slider in Slider.INSTANCES:
            slider.draw()

    @staticmethod
    def check_click(x: float, y: float) -> None:
        clicked = arcade.get_sprites_at_point((x, y), Slider.ALL_BUTTONS)
        for button in clicked:
            cast(SliderButton, button).on_click()

    text: Text
    obj: object
    field_name: str
    pretty_name: str
    min_val: float
    max_val: float

    def get_step(self) -> float:
        return (self.max_val - self.min_val) / 10

    def get_val(self) -> float:
        return getattr(self.obj, self.field_name)

    def set_val(self, val: float) -> None:
        setattr(self.obj, self.field_name, val)

    def __init__(
        self,
        left: float,
        top: float,
        height: float,
        obj: object,
        field_name: str,
        pretty_name: str,
        min_val: float,
        max_val: float,
    ) -> None:
        Slider.ALL_BUTTONS.append(SliderButton(left, top, height, False, self))
        self.text = Text(
            "", left + 2 * height + 5, top - height / 2, color.BLACK, anchor_y="center"
        )
        Slider.ALL_BUTTONS.append(SliderButton(left + height, top, height, True, self))
        Slider.INSTANCES.append(self)
        self.obj = obj
        self.field_name = field_name
        self.pretty_name = pretty_name
        self.min_val = min_val
        self.max_val = max_val

    def draw(self) -> None:
        self.text.text = f"{self.pretty_name}: {self.get_val():.1f}"
        self.text.draw()

    def click(self, increase: bool) -> None:
        new_val = self.get_val() + self.get_step() * (1 if increase else -1)
        new_val = min(self.max_val, max(self.min_val, new_val))
        self.set_val(new_val)
