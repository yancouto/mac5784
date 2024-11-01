from arcade import Sprite, SpriteSolidColor
import arcade, arcade.color
from constants import OBJ_SIZE, DT, SCREEN_HEIGHT, SCREEN_WIDTH
from dataclasses import dataclass
from enum import Enum
from random import Random
from typing import Optional, List, Callable, Type, TypeVar, cast, Sequence
import math

R: Random = Random(2013)

T = TypeVar("T", bound="Agent")

class Agent(Sprite):
    map: "Map"
    
    def __init__(self, map, left, top, *args, type, **kwargs):
        super().__init__(*args, **kwargs, hit_box_algorithm="Simple")
        self.left = left
        self.top = top
        self.map = map
        self.type = type
    
    @property
    def hitbox_width(self) -> float:
        return self.right - self.left
    
    @property
    def hitbox_height(self) -> float:
        return self.top - self.bottom
    
    def find_close(self, agent: Type[T], filter_fn: Optional[Callable[[T], bool]] = None) -> Optional[T]:
        all = list(filter(filter_fn, cast(List[T], self.map.agents(agent))))
        distances = [arcade.get_distance_between_sprites(self, s) ** 2 for s in all]
        if len(distances) > 0:
            mn = min(distances)
            choice = R.choices(all, [mn / d for d in distances])
            if len(choice) > 0:
                return choice[0]
        return None

class DeathReason(Enum):
    Unknown = "unknown"
    Hunger = "hunger"
    Attack = "attack"
    Eaten = "eaten"
    Rotted = "rotted"

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
    
    def add_health(self, amount: float) -> float:
        if self.health <= 0:
            return 0
        health_gain = min(100 - self.health, amount)
        self.health += health_gain
        return health_gain
    
    def death_reason(self) -> DeathReason:
        return DeathReason.Attack
    
    def on_death(self, reason: DeathReason) -> None:
        # By default, just disappear
        self.kill()
    
    def update(self):
        super().update()
        if self.health <= 0:
            reason = self.death_reason()
            #print("%s died of %s" % (self, reason.value))
            self.on_death(reason)
        else:
            self.add_health(self.health_regen * DT)

class Carcass(AgentWithHealth):
    health_regen = 0
    rot_speed: float
    original: Type[Agent]
    total_rotted: float = 0
    def __init__(self, *args, original: Type[Agent], **kwargs):
        self.original = original
        self.rot_speed = R.uniform(1, 5)
        super().__init__(*args, ":resources:images/enemies/wormGreen_dead.png", scale=OBJ_SIZE / 128, **kwargs)
    def update(self):
        self.total_rotted += self.remove_health(self.rot_speed * DT)
        super().update()
    def on_death(self, reason: DeathReason) -> None:
        if R.randint(0, 200) < self.total_rotted:
            self.map.create_agent(self.left, self.top, Grass, health=R.uniform(10, 30))
        return super().on_death(reason)
    def death_reason(self) -> DeathReason:
        if self.total_rotted <= 70:
            return DeathReason.Eaten
        else:
            return DeathReason.Rotted

class Grass(AgentWithHealth):
    health_regen = 5.0
    def __init__(self, *args, **kwargs):
        super().__init__(*args, ":resources:images/tiles/bush.png", scale=OBJ_SIZE / 128, **kwargs)

class AgentWithHunger(AgentWithHealth):
    hunger_damage: float = 10.0
    hunger: float
    hunger_buildup: float = 4.0
    satisfied_health_regen: float = 3.0
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hunger = R.uniform(0, 10)

    def update(self):
        self.hunger = min(100, self.hunger + self.hunger_buildup * DT)
        if self.hunger >= 100:
            self.health -= self.hunger_damage * DT
        elif not self.is_hungry:
            self.add_health(self.satisfied_health_regen * DT)
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

class AgentWithProcreation(AgentWithHunger):
    time_to_procreate: float
    procreate_mean: float = 60.0
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset_procreation()
    
    def reset_procreation(self) -> None:
        self.time_to_procreate = max(10, R.gauss(self.procreate_mean, self.procreate_mean / 2))
    
    def can_procreate(self) -> bool:
        return not self.is_hungry
    
    def update(self):
        super().update()
        if self.can_procreate():
            self.time_to_procreate -= DT
            if self.time_to_procreate <= 0:
                #print("%s procreated" % self)
                self.map.create_agent(max(0, self.left - self.width), self.top, self.__class__, health = 20)
                self.hunger += 30
                self.reset_procreation()

class Herbivore(AgentWithProcreation):
    HEALTH_TO_HUNGER: float = 1.2
    health_regen = 1.0
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
    @dataclass
    class AttackCooldown(HState):
        time_to_wait: float
        target: "Carnivore"
    state: HState
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, ":resources:images/enemies/wormPink.png", scale=OBJ_SIZE / 128, **kwargs)
        self.state = Herbivore.Idle.random(3)
        self.idle_speed: float = R.uniform(0.3, 1.2)
        self.chase_speed: float = R.uniform(0.3, 2.0)
        self.eat_speed: float = R.uniform(15, 20)
        # Less than carnivore
        self.attack_damage: float = R.uniform(5, 15)
    
    def on_death(self, reason: DeathReason) -> None:
        super().on_death(reason)
        init_health = 70 if reason == DeathReason.Hunger else 100
        self.map.create_agent(self.left, self.top, Carcass, original=self.__class__, health = init_health)
    
    def chase_food(self) -> bool:
        grass = self.find_close(Grass)
        if grass is not None:
            self.state = Herbivore.ChasingFood(grass)
        return grass is not None
    
    # This might also attack carnivores attacking other prey, which is kinda nice for group behaviour.
    def try_attack_carnivore(self) -> bool:
        carnivore = self.find_close(Carnivore, lambda c: isinstance(c.state, Carnivore.AttackCooldown) and (arcade.get_distance_between_sprites(self, c) < 100 or self.collides_with_sprite(c)))
        if carnivore is not None:
            carnivore.remove_health(self.attack_damage)
            self.state = Herbivore.AttackCooldown(1.2, carnivore)
        return carnivore is not None
    
    def update(self):
        super().update()
        self.time_to_procreate -= DT
        match self.state:
            case Herbivore.Idle(_) as state:
                state.time_to_move -= DT
                if self.hunger >= 60 and self.chase_food():
                    return
                if self.try_attack_carnivore():
                    return
                if (self.hunger >= 40 and state.time_to_move <= 0) and self.chase_food():
                    return
                if state.time_to_move <= 0:
                    if R.random() < 0.3:
                        self.velocity = [0, 0]
                    else:
                        self.velocity = arcade.rotate_point(self.idle_speed, 0, 0, 0, R.uniform(0, 360))
                    self.state = Herbivore.Idle.random(8)
            case Herbivore.AttackCooldown(_, _) as state:
                state.time_to_wait -= DT
                if state.time_to_wait <= 0:
                    if self.try_attack_carnivore():
                        return
                    else:
                        self.state = Herbivore.Idle(0)
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
    
class Carnivore(AgentWithProcreation):
    health_to_hunger: float = 1.6
    health_regen = 1.0
    procreate_mean = 100.0
    hunger_buildup = 5.0
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, ":resources:images/enemies/slimeBlue.png", scale=OBJ_SIZE / 128, **kwargs)
        self.state = Carnivore.Idle.random(3)
        self.idle_speed: float = R.uniform(0.3, 1.2)
        self.chase_speed: float = R.uniform(0.3, 2.0)
        self.eat_speed: float = R.uniform(15, 20)
        self.attack_damage: float = R.uniform(20, 50)
    
    def on_death(self, reason: DeathReason) -> None:
        super().on_death(reason)
        init_health = 70 if reason == DeathReason.Hunger else 100
        self.map.create_agent(self.left, self.top, Carcass, original=self.__class__, health = init_health)
    
    def update(self):
        super().update()
        while True:
            match self.state:
                case Carnivore.Idle(_) as state:
                    state.time_to_move -= DT
                    if self.hunger >= 50 or (self.hunger >= 30 and state.time_to_move <= 0) or self.hunger - self.health >= 20:
                        carcass = self.find_close(Carcass)
                        if carcass is not None:
                            self.state = Carnivore.ChasingPrey(carcass)
                            return
                        herbivore = self.find_close(Herbivore)
                        if herbivore is not None:
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
                        self.remove_hunger(eaten * self.health_to_hunger)
                        if self.hunger <= 0:
                            self.state = Carnivore.Idle.random(1)
                case _:
                    raise ValueError("Unknown state")
            # The default is to end unless we use continue
            return

ALL_AGENTS = [Grass, Herbivore, Carcass, Carnivore]

class Map(SpriteSolidColor):
    scene = arcade.Scene()
    def __init__(self, size: int) -> None:
        super().__init__(size, size, (0, 0, 0))
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2
        for agent in ALL_AGENTS:
            self.scene.add_sprite_list(agent.__name__)
        for _ in range(50):
            left = R.uniform(self.left, self.right - OBJ_SIZE)
            top = R.uniform(self.bottom + OBJ_SIZE, self.top)
            self.create_agent(left, top, R.choices([Grass, Herbivore, Carnivore], [11, 3, 2])[0])
    
    def agents(self, agent: Type[Agent]) -> Sequence[Agent]:
        return cast(List[Agent], self.scene.get_sprite_list(agent.__name__).sprite_list)

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
    
    def create_agent(self, x: float, y: float, agent: Type[Agent], **kwargs) -> None:
        if len(self.agents(agent)) > 1000:
            print("TOO MANY %s AGENTS" % agent.__name__)
            return
        self.scene.add_sprite(agent.__name__, agent(self, x, y, type=agent, **kwargs))