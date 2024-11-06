import arcade, arcade.color
from arcade import Window, key, Text, Camera
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
import agents
from agents import Map, Grass, Herbivore, Carnivore, Agent
from historical_data import HistoricalData
from typing import List, Type

SPEED_MULTIPLIER: int = 1

class Game(Window):
    map: Map
    cur_agent: Type[Agent] = Grass
    graph: HistoricalData
    previous_pause_val: int = 0
    gui_camera: Camera
    map_camera: Camera
    score: float = 0
    time_no_modif: float = 0

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Equilibrium") # type: ignore
        arcade.set_background_color(arcade.color.WHITE)
        self.simulation_speed = Text("", 10, SCREEN_HEIGHT - 20, arcade.color.BLACK, 12)
        self.cur_agent_text = Text("", 10, SCREEN_HEIGHT - 40, arcade.color.BLACK, 12)
        self.grass_count = Text("", 10, SCREEN_HEIGHT - 60, arcade.color.BLACK, 12)
        self.herbivore_count = Text("", 10, SCREEN_HEIGHT - 80, arcade.color.BLACK, 12)
        self.carnivore_count = Text("", 10, SCREEN_HEIGHT - 100, arcade.color.BLACK, 12)
        map_size = 1000
        self.map = Map(map_size)
        self.map_camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.map_camera.scale = map_size / 800.0
        self.gui_camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.graph = HistoricalData((SCREEN_WIDTH - 450, SCREEN_HEIGHT / 2), (200, 200), self.get_data)
        self.time_no_modif_text = Text("", SCREEN_WIDTH - 450, SCREEN_HEIGHT / 2 - 30, arcade.color.BLACK, 13)
        self.score_text = Text("", SCREEN_WIDTH - 450, SCREEN_HEIGHT / 2 - 60, arcade.color.BLACK, 15)
        self.update_agent_text()
        self.update_counts()

    def on_draw(self):
        arcade.start_render()
        self.gui_camera.use()
        for drawable in [self.simulation_speed, self.cur_agent_text, self.grass_count, self.herbivore_count, self.carnivore_count, self.graph, self.time_no_modif_text, self.score_text]:
            drawable.draw()
        self.map_camera.use()
        self.map.draw()
    
    def on_update(self, delta_time: float):
        self.time_no_modif += SPEED_MULTIPLIER * delta_time
        self.score += SPEED_MULTIPLIER * delta_time
        for _ in range(SPEED_MULTIPLIER):
            self.map.update()
            self.graph.update()
        self.update_counts()
    
    def update_agent_text(self):
        self.cur_agent_text.text = f"Click to create: {self.cur_agent.__name__} (use G, H, C to change)"
    
    def get_data(self) -> List[float]:
        return [
            len(self.map.agents(Grass)),
            len(self.map.agents(Herbivore)),
            len(self.map.agents(Carnivore))
        ]
        
    
    def update_counts(self):
        [grass_count, herbivore_count, carnivore_count] = self.get_data()
        self.grass_count.text = f"Grass total: {grass_count}"
        self.herbivore_count.text = f"Herbivores total: {herbivore_count}"
        self.carnivore_count.text = f"Carnivores total: {carnivore_count}"
        self.simulation_speed.text = f"Simulation speed: {SPEED_MULTIPLIER}x (use arrows to change, P to pause/resume)"
        self.time_no_modif_text.text = f"Time without modification: {self.time_no_modif:.1f}s"
        self.score_text.text = f"Score: {self.score:.0f}"
    
    def on_key_press(self, symbol: int, modifiers: int):
        global SPEED_MULTIPLIER
        if symbol == key.H:
            self.cur_agent = Herbivore
        elif symbol == key.G:
            self.cur_agent = Grass
        elif symbol == key.C:
            self.cur_agent = Carnivore
        elif symbol == key.RIGHT:
            SPEED_MULTIPLIER = SPEED_MULTIPLIER + 1
        elif symbol == key.LEFT:
            SPEED_MULTIPLIER = max(0, SPEED_MULTIPLIER - 1)
        elif symbol == key.P:
            if SPEED_MULTIPLIER == 0:
                SPEED_MULTIPLIER = self.previous_pause_val
            else:
                self.previous_pause_val = SPEED_MULTIPLIER
                SPEED_MULTIPLIER = 0
        else:
            return
        self.update_agent_text()
    
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT and self.map.collides_with_point((x, y)):
            if self.map.create_agent(x, y, self.cur_agent):
                self.graph.add_vertical_mark()
                self.time_no_modif = 0
                self.score = max(0, self.score - 10)

def main():
    game = Game()
    arcade.run()

if __name__ == "__main__":
    main()
