from arcade import Sprite
import arcade, arcade.color
from constants import OBJ_SIZE, DT
import random

class ObjWithHealth(Sprite):
    health = 100.0
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, hit_box_algorithm="None")

    def draw(self, **kwargs):
        super().draw(**kwargs)
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
        super().__init__(":resources:images/tiles/cactus.png", scale=OBJ_SIZE / 128)
        self.center_x = x
        self.center_y = y
        self.health = 20 + random.random() * 80
        assert(self.width == OBJ_SIZE and self.height == OBJ_SIZE)
    
    def update(self):
        self.health += 1.0 * DT

class Herbivore(ObjWithHealth):
    def __init__(self, x, y):
        super().__init__(":resources:images/enemies/wormPink.png", scale=OBJ_SIZE / 128)
        self.center_x = x
        self.center_y = y
        assert(self.width == OBJ_SIZE and self.height == OBJ_SIZE)