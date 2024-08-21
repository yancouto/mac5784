import arcade, arcade.color
from arcade import Sprite, SpriteSolidColor, Window
import random
from constants import OBJ_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from agents import Herbivore, Grass


class Map(SpriteSolidColor):
    all_objs = arcade.SpriteList()
    def __init__(self) -> None:
        super().__init__(500, 500, (0, 0, 0))
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2
        for _ in range(10):
            x = self.center_x + (random.random() - 0.5) * (self.width - OBJ_SIZE)
            y = self.center_y + (random.random() - 0.5) * (self.height - OBJ_SIZE)
            if random.random() < 0.2:
                self.all_objs.append(Herbivore(x, y))
            else:
                self.all_objs.append(Grass(x, y))
    def update(self):
        for obj in self.all_objs.sprite_list:
            obj.update()
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
