import arcade, arcade.color
from arcade import Window
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from agents import Map

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
