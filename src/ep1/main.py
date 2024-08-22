import arcade, arcade.color
from arcade import Window, key, Text
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from agents import Map, Agents

class Game(Window):
    map = Map()
    cur_agent: Agents = Agents.Grass
    cur_agent_text: Text
    grass_count: Text
    herbivore_count: Text

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "EP1") # type: ignore
        arcade.set_background_color(arcade.color.WHITE)
        self.cur_agent_text = Text("", 10, SCREEN_HEIGHT - 20, arcade.color.BLACK, 12)
        self.grass_count = Text("", 10, SCREEN_HEIGHT - 40, arcade.color.BLACK, 12)
        self.herbivore_count = Text("", 10, SCREEN_HEIGHT - 60, arcade.color.BLACK, 12)
        self.update_agent_text()
        self.update_counts()

    def on_draw(self):
        arcade.start_render()
        self.cur_agent_text.draw()
        self.grass_count.draw()
        self.herbivore_count.draw()
        self.map.draw()
    
    def on_update(self, delta_time: float):
        self.map.update()
        self.update_counts()
    
    def update_agent_text(self):
        self.cur_agent_text.text = f"Click to create: {self.cur_agent.name}"
    
    def update_counts(self):
        grass_count = len(self.map.scene[Agents.Grass.name])
        herbivore_count = len(self.map.scene[Agents.Herbivore.name])
        self.grass_count.text = f"Grass total: {grass_count}"
        self.herbivore_count.text = f"Herbivores total: {herbivore_count}"
    
    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == key.H:
            self.cur_agent = Agents.Herbivore
        elif symbol == key.G:
            self.cur_agent = Agents.Grass
        else:
            return
        self.update_agent_text()
    
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT and self.map.collides_with_point((x, y)):
            self.map.create_agent(x, y, self.cur_agent)

def main():
    game = Game()
    arcade.run()

if __name__ == "__main__":
    main()
