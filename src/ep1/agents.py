from arcade import Sprite
import arcade, arcade.color
from constants import OBJ_SIZE, DT
import random
from util import rand
from dataclasses import dataclass

class AgentWithHealth(Sprite):
    health = 100.0
    health_regen = 0.0
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, hit_box_algorithm="None")

    def draw(self, **kwargs):
        super().draw(**kwargs)
        health_bar_width = self.width * (self.health / 100)
        health_bar_height = 5
        health_bar_x = self.left + health_bar_width / 2
        health_bar_y = self.top - health_bar_height / 2
        arcade.draw_rectangle_filled(health_bar_x, health_bar_y, health_bar_width, health_bar_height, arcade.color.GREEN)
        self.draw_hit_box(arcade.color.RED, 1)
    
    @property
    def is_dead(self) -> bool:
        return self.health <= 0
    
    def update(self):
        super().update()
        self.health = min(100, self.health + self.health_regen * DT)
        if self.health <= 0:
            print("%s died" % self)
            self.kill()

class Grass(AgentWithHealth):
    health_regen = 5.0
    def __init__(self, left, top):
        super().__init__(":resources:images/tiles/cactus.png", scale=OBJ_SIZE / 128)
        self.left = left
        self.top = top
        assert(self.width == OBJ_SIZE and self.height == OBJ_SIZE)

class AgentWithHunger(AgentWithHealth):
    HUNGER_DAMAGE: float = 10.0
    hunger: float
    hunger_buildup: float = 5.0
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hunger = rand(0, 20)

    def update(self):
        self.hunger = min(100, self.hunger + self.hunger_buildup * DT)
        if self.hunger >= 100:
            self.health -= AgentWithHunger.HUNGER_DAMAGE * DT
        super().update()
    
    def draw(self, **kwargs):
        super().draw(**kwargs)
        hunger_bar_width = self.width * (self.hunger / 100)
        hunger_bar_height = 5
        hunger_bar_x = self.left + hunger_bar_width / 2
        hunger_bar_y = self.top - hunger_bar_height / 2 - 5
        arcade.draw_rectangle_filled(hunger_bar_x, hunger_bar_y, hunger_bar_width, hunger_bar_height, arcade.color.RED)

    @property
    def is_hungry(self) -> bool:
        return self.hunger >= 50.0

class Herbivore(AgentWithHunger):
    health_regen = 1.0
    class HState: pass
    @dataclass
    class Idle(HState):
        time_to_move: float
        @staticmethod
        def random(max: float):
            return Herbivore.Idle(rand(max / 4, max))
    @dataclass
    class ChasingFood(HState):
        target: Grass
    @dataclass
    class Eating(HState):
        target: Grass
    state: HState
    
    def __init__(self, left, top):
        super().__init__(":resources:images/enemies/wormPink.png", scale=OBJ_SIZE / 128)
        self.state = Herbivore.Idle.random(3)
        self.left = left
        self.top = top
        self.idle_speed: float = rand(0.1, 0.5)
        assert(self.width == OBJ_SIZE and self.height == OBJ_SIZE)
    
    def update(self):
        super().update()
        match self.state:
            case Herbivore.Idle(_) as state:
                state.time_to_move -= DT
                if self.is_hungry:
                    #self.state = Herbivore.ChasingFood(find someone)
                    pass
                elif state.time_to_move <= 0:
                    if random.random() < 0.3:
                        self.velocity = [0, 0]
                    else:
                        self.velocity = arcade.rotate_point(self.idle_speed, 0, 0, 0, rand(0, 360))
                    self.state = Herbivore.Idle.random(8)
            case Herbivore.ChasingFood(target):
                if target.is_dead:
                    self.state = Herbivore.Idle.random(1)
                else:
                    # Chase
                    pass
            case Herbivore.Eating(target):
                if target.is_dead:
                    self.state = Herbivore.Idle.random(1)
                else:
                    # Eat
                    pass
            case _:
                raise ValueError("Unknown state")
        