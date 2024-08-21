import arcade, arcade.color
from arcade import Sprite, SpriteSolidColor, Window
import random

SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 900
OBJ_SIZE = 50

class Grass(Sprite):
    def __init__(self, x, y):
        super().__init__(":resources:images/tiles/cactus.png", scale=OBJ_SIZE / 128)
        self.center_x = x
        self.center_y = y

class Map(SpriteSolidColor):
    all_objs = arcade.SpriteList()
    def __init__(self) -> None:
        super().__init__(500, 500, (0, 0, 0))
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2
        for _ in range(10):
            x = random.randint(0, 500 - OBJ_SIZE)
            y = random.randint(0, 500 - OBJ_SIZE)
            grass = Grass(self.center_x - self.width / 2 + x + OBJ_SIZE / 2, self.center_y - self.height / 2 + y + OBJ_SIZE / 2)
            self.all_objs.append(grass)
    def draw(self) -> None: # type: ignore
        super().draw()
        self.all_objs.draw()

class Game(Window):
    map = Map()
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "EP1") # type: ignore
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        arcade.start_render()
        self.map.draw()

def main():
    game = Game()
    arcade.run()

if __name__ == "__main__":
    main()
