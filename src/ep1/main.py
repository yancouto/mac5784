import arcade, arcade.color
from arcade import Sprite, SpriteSolidColor, Window
import random

SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 900
OBJ_SIZE = 50
DT = 1 / 60

class ObjWithHealth(Sprite):
    health = 100.0

    def draw(self): # type: ignore
        super().draw()
        health_bar_width = self.width * (self.health / 100)
        health_bar_height = 5
        health_bar_x = self.center_x - (self.width - health_bar_width) / 2
        health_bar_y = self.center_y + self.height / 2 - health_bar_height / 2 - 2
        arcade.draw_rectangle_filled(health_bar_x, health_bar_y, health_bar_width, health_bar_height, arcade.color.GREEN)
        self.draw_hit_box(arcade.color.RED, 1)
    
    def update(self):
        if self.health < 0:
            print("%s died" % self)
            self.kill()

class Grass(ObjWithHealth):
    def __init__(self, x, y):
        super().__init__(":resources:images/tiles/cactus.png", scale=OBJ_SIZE / 128, hit_box_algorithm="None")
        self.center_x = x
        self.center_y = y
        self.health = 20 + random.random() * 80
        assert(self.width == OBJ_SIZE and self.height == OBJ_SIZE)
    
    def update(self):
        self.health += 1.0 * DT

class Herbivore(ObjWithHealth):
    def __init__(self, x, y):
        super().__init__(":resources:images/enemies/wormPink.png", scale=OBJ_SIZE / 128, hit_box_algorithm="None")
        self.center_x = x
        self.center_y = y
        assert(self.width == OBJ_SIZE and self.height == OBJ_SIZE)

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
