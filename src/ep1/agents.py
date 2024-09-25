from arcade import Sprite, SpriteSolidColor
import arcade, arcade.color
from constants import OBJ_SIZE, DT, SCREEN_HEIGHT, SCREEN_WIDTH
from dataclasses import dataclass
from enum import Enum
from random import Random
from typing import Optional, List
from common import Updatable
import math

R: Random = Random(2012)
SPEED_MULTIPLIER: int = 1

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
    
    def find_close(self, agent: "Agents") -> Optional[Sprite]:
        all = self.map.scene.get_sprite_list(agent.name).sprite_list
        distances = [arcade.get_distance_between_sprites(self, s) for s in all]
        if len(distances) > 0:
            max_dist = max(distances)
            choice = R.choices(all, [max_dist + 1 - d for d in distances])
            if len(choice) > 0:
                return choice[0]
        return None

class DeathReason(Enum):
    Unknown = "unknown"
    Hunger = "hunger"
    Attack = "attack"
    Eaten = "eaten"

class AgentWithHealth(Agent):
    health = 100.0
    health_regen = 0.0
    
    def __init__(self, *args, **kwargs):
        self.health = kwargs.pop("health", 100.0)
        super().__init__(*args, **kwargs)

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
    
    def death_reason(self) -> DeathReason:
        return DeathReason.Attack
    
    def on_death(self, reason: DeathReason) -> None:
        # By default, just disappear
        self.kill()
    
    def update(self):
        super().update()
        if self.health <= 0:
            reason = self.death_reason()
            print("%s died of %s" % (self, reason.value))
            self.on_death(reason)
        else:
            self.health = max(0, min(100, self.health + self.health_regen * DT))

class Carcass(AgentWithHealth):
    # Rotting
    health_regen = -2
    original: "Agents"
    def __init__(self, *args, agent, **kwargs):
        self.original = agent
        super().__init__(*args, ":resources:images/enemies/wormGreen_dead.png", scale=OBJ_SIZE / 128, **kwargs)
    def death_reason(self) -> DeathReason:
        return DeathReason.Eaten

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
        self.hunger = R.uniform(0, 10)

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
    
    def death_reason(self) -> DeathReason:
        return super().death_reason() if self.hunger >= 99 else DeathReason.Hunger

class Herbivore(AgentWithHunger):
    HEALTH_TO_HUNGER: float = 1.2
    health_regen = 1.0
    time_to_procreate = math.inf
    class HState: pass
    @dataclass
    class Idle(HState):
        time_to_move: float
        @staticmethod
        def random(max: float):
            return Herbivore.Idle(R.uniform(max / 4, max))
    @dataclass
    class ChasingFood(HState):
        target: Grass
    @dataclass
    class Eating(HState):
        target: Grass
    state: HState
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, ":resources:images/enemies/wormPink.png", scale=OBJ_SIZE / 128, **kwargs)
        self.state = Herbivore.Idle.random(3)
        self.idle_speed: float = R.uniform(0.3, 0.8)
        self.chase_speed: float = R.uniform(1.0, 2.0)
        self.eat_speed: float = R.uniform(15, 20)
        self.time_to_procreate = R.uniform(10, 60)
    
    def on_death(self, reason: DeathReason) -> None:
        super().on_death(reason)
        init_health = 70 if reason == DeathReason.Hunger else 100
        self.map.create_agent(self.left, self.top, Agents.Carcass, agent=Agents.Herbivore, health = init_health)
    
    def update(self):
        super().update()
        self.time_to_procreate -= DT
        match self.state:
            case Herbivore.Idle(_) as state:
                state.time_to_move -= DT
                if self.hunger >= 70 or (self.hunger >= 50 and state.time_to_move <= 0):
                    grass = self.find_close(Agents.Grass)
                    if isinstance(grass, Grass):
                        self.state = Herbivore.ChasingFood(grass)
                        return
                if state.time_to_move <= 0:
                    if R.random() < 0.3:
                        self.velocity = [0, 0]
                    else:
                        self.velocity = arcade.rotate_point(self.idle_speed, 0, 0, 0, R.uniform(0, 360))
                    self.state = Herbivore.Idle.random(8)
                elif self.time_to_procreate <= 0:
                    print("%s procreated" % self)
                    self.map.create_agent(max(0, self.left - self.width), self.top, Agents.Herbivore, health = 20)
                    self.time_to_procreate = R.uniform(10, 60)
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
    
class Carnivore(AgentWithHunger):
    HEALTH_TO_HUNGER: float = 1.4
    health_regen = 1.0
    class CState: pass
    @dataclass
    class Idle(CState):
        time_to_move: float
        @staticmethod
        def random(max: float):
            return Carnivore.Idle(R.uniform(max / 4, max))
    @dataclass
    class ChasingPrey(CState):
        target: Herbivore | Carcass
    @dataclass
    class AttackCooldown(CState):
        time_to_wait: float
        target: Herbivore
    @dataclass
    class Eating(CState):
        target: Carcass
    state: CState
    
    def __init__(self, *args):
        super().__init__(*args, ":resources:images/enemies/frog.png", scale=OBJ_SIZE / 128)
        self.state = Carnivore.Idle.random(3)
        self.idle_speed: float = R.uniform(0.3, 0.8)
        self.chase_speed: float = R.uniform(1.0, 2.0)
        self.eat_speed: float = R.uniform(15, 20)
        self.attack_damage: float = R.uniform(20, 50)
    
    def on_death(self, reason: DeathReason) -> None:
        super().on_death(reason)
        init_health = 70 if reason == DeathReason.Hunger else 100
        self.map.create_agent(self.left, self.top, Agents.Carcass, agent=Agents.Carnivore, health = init_health)
    
    def update(self):
        super().update()
        while True:
            match self.state:
                case Carnivore.Idle(_) as state:
                    state.time_to_move -= DT
                    if self.hunger >= 70 or (self.hunger >= 50 and state.time_to_move <= 0):
                        carcass = self.find_close(Agents.Carcass)
                        if isinstance(carcass, Carcass):
                            self.state = Carnivore.ChasingPrey(carcass)
                            return
                        herbivore = self.find_close(Agents.Herbivore)
                        if isinstance(herbivore, Herbivore):
                            self.state = Carnivore.ChasingPrey(herbivore)
                            return
                    if state.time_to_move <= 0:
                        if R.random() < 0.3:
                            self.velocity = [0, 0]
                        else:
                            self.velocity = arcade.rotate_point(self.idle_speed, 0, 0, 0, R.uniform(0, 360))
                        self.state = Carnivore.Idle.random(8)
                case Carnivore.ChasingPrey(target):
                    if target.is_dead:
                        self.state = Carnivore.Idle(0)
                        continue
                    elif self.collides_with_sprite(target):
                        self.velocity = [0, 0]
                        if isinstance(target, Carcass):
                            self.state = Carnivore.Eating(target)
                        elif isinstance(target, Herbivore):
                            target.remove_health(self.attack_damage)
                            self.state = Carnivore.AttackCooldown(1, target)
                        else:
                            raise ValueError("Unknown target type")
                    else:
                        self.angle = 0
                        self.velocity = [0, 0]
                        self.face_point(target.position)
                        self.angle += 90
                        self.forward(self.chase_speed)
                case Carnivore.AttackCooldown(_, target) as state:
                    state.time_to_wait -= DT
                    if state.time_to_wait <= 0:
                        self.state = Carnivore.ChasingPrey(target)
                        continue
                case Carnivore.Eating(target):
                    if target.is_dead:
                        self.state = Carnivore.Idle.random(1)
                    else:
                        eaten = target.remove_health(self.eat_speed * DT)
                        self.remove_hunger(eaten * Carnivore.HEALTH_TO_HUNGER)
                        if self.hunger <= 0:
                            self.state = Carnivore.Idle.random(1)
                case _:
                    raise ValueError("Unknown state")
            # The default is to end unless we use continue
            return

class Agents(Enum):
    Grass = Grass
    Herbivore = Herbivore
    Carcass = Carcass
    Carnivore = Carnivore

class Map(SpriteSolidColor):
    scene = arcade.Scene()
    updatables: List[Updatable] = []
    def __init__(self) -> None:
        super().__init__(800, 800, (0, 0, 0))
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2
        for agent in Agents:
            self.scene.add_sprite_list(agent.name)
        for _ in range(30):
            left = R.uniform(self.left, self.right - OBJ_SIZE)
            top = R.uniform(self.bottom + OBJ_SIZE, self.top)
            self.create_agent(left, top, R.choices([Agents.Grass, Agents.Herbivore, Agents.Carnivore], [6, 3, 1])[0])

    def update(self):
        for _ in range(SPEED_MULTIPLIER):
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
            for update in self.updatables:
                update.update()

    def draw(self, **kwargs) -> None:
        super().draw(**kwargs)
        for obj in self.scene.sprite_lists:
            for obj in obj.sprite_list:
                obj.draw()
    
    def create_agent(self, x: float, y: float, agent_type: Agents, **kwargs) -> None:
        if len(self.scene.get_sprite_list(agent_type.name)) > 1000:
            # TOO MANY
            return
        self.scene.add_sprite(agent_type.name, agent_type.value(self, x, y, **kwargs))