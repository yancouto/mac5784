from arcade import Sprite, SpriteSolidColor
import arcade, arcade.color
from constants import OBJ_SIZE, DT, SCREEN_HEIGHT, SCREEN_WIDTH
import random
from util import rand
from dataclasses import dataclass
from enum import Enum

class Agent(Sprite):
    map: "Map"
    
    def __init__(self, map, left, top, *args, **kwargs):
        super().__init__(*args, **kwargs, hit_box_algorithm="Simple")
        self.left = left
        self.top = top
        self.map = map
    
    @property
    def hitbox_width(self) -> float:
        return self.right - self.left
    
    @property
    def hitbox_height(self) -> float:
        return self.top - self.bottom

class AgentWithHealth(Agent):
    health = 100.0
    health_regen = 0.0

    def draw(self, **kwargs):
        super().draw(**kwargs)
        health_bar_width = self.hitbox_width * (self.health / 100)
        health_bar_height = 5
        health_bar_x = self.left + health_bar_width / 2
        health_bar_y = self.top + health_bar_height / 2
        arcade.draw_rectangle_filled(health_bar_x, health_bar_y, health_bar_width, health_bar_height, arcade.color.GREEN)
        self.draw_hit_box(arcade.color.RED, 1)
    
    @property
    def is_dead(self) -> bool:
        return self.health <= 0
    
    def remove_health(self, damage: float) -> float:
        health_drop = min(self.health, damage)
        self.health -= health_drop
        return health_drop
    
    def update(self):
        super().update()
        if self.health <= 0:
            print("%s died" % self)
            self.kill()
        else:
            self.health = min(100, self.health + self.health_regen * DT)

class Grass(AgentWithHealth):
    health_regen = 5.0
    def __init__(self, *args):
        super().__init__(*args, ":resources:images/tiles/cactus.png", scale=OBJ_SIZE / 128)

class AgentWithHunger(AgentWithHealth):
    HUNGER_DAMAGE: float = 10.0
    hunger: float
    hunger_buildup: float = 5.0
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hunger = rand(0, 10)

    def update(self):
        self.hunger = min(100, self.hunger + self.hunger_buildup * DT)
        if self.hunger >= 100:
            self.health -= AgentWithHunger.HUNGER_DAMAGE * DT
        super().update()
    
    def draw(self, **kwargs):
        super().draw(**kwargs)
        hunger_bar_width = self.hitbox_width * (self.hunger / 100)
        hunger_bar_height = 5
        hunger_bar_x = self.left + hunger_bar_width / 2
        hunger_bar_y = self.top + hunger_bar_height / 2 + 5
        arcade.draw_rectangle_filled(hunger_bar_x, hunger_bar_y, hunger_bar_width, hunger_bar_height, arcade.color.RED)
    
    def remove_hunger(self, amount: float):
        self.hunger = max(0, self.hunger - amount)

    @property
    def is_hungry(self) -> bool:
        return self.hunger >= 50.0

class Herbivore(AgentWithHunger):
    HEALTH_TO_HUNGER: float = 1.2
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
    
    def __init__(self, *args):
        super().__init__(*args, ":resources:images/enemies/wormPink.png", scale=OBJ_SIZE / 128)
        self.state = Herbivore.Idle.random(3)
        self.idle_speed: float = rand(0.3, 0.8)
        self.chase_speed: float = rand(1.0, 2.0)
        self.eat_speed: float = rand(15, 20)
    
    def update(self):
        super().update()
        match self.state:
            case Herbivore.Idle(_) as state:
                state.time_to_move -= DT
                if self.hunger >= 70 or (self.hunger >= 50 and state.time_to_move <= 0):
                    grasses = self.map.scene.get_sprite_list(Agents.Grass.name).sprite_list
                    distances = [arcade.get_distance_between_sprites(self, s) for s in grasses]
                    max_dist = max(distances)
                    chase = random.choices(grasses, [max_dist + 1 - d for d in distances])
                    if len(chase) > 0 and isinstance(chase[0], Grass):
                        self.state = Herbivore.ChasingFood(chase[0])
                        return
                elif state.time_to_move <= 0:
                    if random.random() < 0.3:
                        self.velocity = [0, 0]
                    else:
                        self.velocity = arcade.rotate_point(self.idle_speed, 0, 0, 0, rand(0, 360))
                    self.state = Herbivore.Idle.random(8)
            case Herbivore.ChasingFood(target):
                if target.is_dead:
                    self.state = Herbivore.Idle.random(1)
                elif self.collides_with_sprite(target):
                    self.velocity = [0, 0]
                    self.state = Herbivore.Eating(target)
                else:
                    self.angle = 0
                    self.velocity = [0, 0]
                    self.face_point(target.position)
                    self.angle += 90
                    self.forward(self.chase_speed)
            case Herbivore.Eating(target):
                if target.is_dead:
                    self.state = Herbivore.Idle.random(1)
                else:
                    eaten = target.remove_health(self.eat_speed * DT)
                    self.remove_hunger(eaten * Herbivore.HEALTH_TO_HUNGER)
                    if self.hunger <= 0:
                        self.state = Herbivore.Idle.random(0.5)
            case _:
                raise ValueError("Unknown state")

class Agents(Enum):
    Grass = Grass
    Herbivore = Herbivore

class Map(SpriteSolidColor):
    scene = arcade.Scene()
    def __init__(self) -> None:
        super().__init__(800, 800, (0, 0, 0))
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2
        for _ in range(30):
            left = self.left + random.random() * (self.width - OBJ_SIZE)
            top = self.top - random.random() * (self.height - OBJ_SIZE)
            if random.random() < 0.4:
                self.scene.add_sprite(Agents.Herbivore.name, Herbivore(self, left, top))
            else:
                self.scene.add_sprite(Agents.Grass.name, Grass(self, left, top))

    def update(self):
        for list in self.scene.sprite_lists:
            for obj in list.sprite_list:
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
        for obj in self.scene.sprite_lists:
            for obj in obj.sprite_list:
                obj.draw()
    
    def create_agent(self, x: int, y: int, agent: Agents) -> None:
        self.scene.add_sprite(agent.name, agent.value(self, x, y))