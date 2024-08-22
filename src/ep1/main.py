import arcade, arcade.color
from arcade import Sprite, SpriteSolidColor, Window
import random
from constants import OBJ_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from agents import Herbivore, Grass


class Map(SpriteSolidColor):
    all_objs = arcade.SpriteList()
    def __init__(self) -> None:
        super().__init__(800, 800, (0, 0, 0))
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2
        for _ in range(30):
            left = self.left + random.random() * (self.width - OBJ_SIZE)
            top = self.top - random.random() * (self.height - OBJ_SIZE)
            if random.random() < 0.3:
                self.all_objs.append(Herbivore(left, top))
            else:
                self.all_objs.append(Grass(left, top))
    def update(self):
        for obj in self.all_objs.sprite_list:
            obj.update()
            if obj.left < self.left:
                obj.change_x = abs(obj.change_x)
            elif obj.right > self.right:
                obj.change_x = -abs(obj.change_x)
            elif obj.top > self.top:
                obj.change_y = -abs(obj.change_y)
            elif obj.bottom < self.bottom:
                obj.change_y = abs(obj.change_y)
    def draw(self, **kwargs) -> None:
        super().draw(**kwargs)
        for obj in self.all_objs.sprite_list:
            obj.draw()

class Game(Window):
    map = Map()
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "EP1") # type: ignore
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        arcade.start_render()
        self.map.draw()
    
    def on_update(self, delta_time: float):
        self.map.update()

def main():
    game = Game()
    arcade.run()

if __name__ == "__main__":
    main()
