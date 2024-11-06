import arcade, arcade.color
from arcade import Window, key, Text, Camera
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
import agents
from agents import Map, Grass, Herbivore, Carnivore, Agent
from historical_data import HistoricalData
from typing import List, Type, Tuple
from logs import Logs
import argparse

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
    prev_count: List[float] = [0, 0, 0]

    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Equilibrium")  # type: ignore
        arcade.set_background_color(arcade.color.WHITE)
        self.simulation_speed = Text("", 10, SCREEN_HEIGHT - 20, arcade.color.BLACK, 12)
        self.cur_agent_text = Text("", 10, SCREEN_HEIGHT - 40, arcade.color.BLACK, 12)
        self.tab_text = Text(
            "Press TAB to toggle health and hunger bars.",
            10,
            SCREEN_HEIGHT - 60,
            arcade.color.BLACK,
        )
        self.right_click_text = Text(
            "Right click on an agent to destroy it.",
            10,
            SCREEN_HEIGHT - 80,
            arcade.color.BLACK,
        )
        self.grass_count = Text("", 10, SCREEN_HEIGHT - 120, arcade.color.BLACK, 12)
        self.herbivore_count = Text("", 10, SCREEN_HEIGHT - 140, arcade.color.BLACK, 12)
        self.carnivore_count = Text("", 10, SCREEN_HEIGHT - 160, arcade.color.BLACK, 12)
        map_size = 1000
        self.map = Map(map_size)
        if args.herbivores_only:
            self.map.gen_random_agents(30, [0, 1, 0])
        elif args.carnivores_only:
            self.map.gen_random_agents(20, [0, 0, 1])
        else:
            self.map.gen_random_agents(50, [11, 5, 2])
        self.map_camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.map_camera.scale = map_size / 800.0
        self.gui_camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        graph_bl = (SCREEN_WIDTH - 450, SCREEN_HEIGHT - 300)
        self.graph = HistoricalData(graph_bl, (400, 200), self.get_data)
        self.time_no_modif_text = Text(
            "", graph_bl[0], graph_bl[1] - 30, arcade.color.BLACK, 13
        )
        self.score_text = Text(
            "", graph_bl[0], graph_bl[1] - 60, arcade.color.BLACK, 15
        )
        self.logs: Logs = Logs((graph_bl[0], graph_bl[1] - 120), (200, 300))
        self.update_agent_text()
        self.update_counts()

    def on_draw(self):
        arcade.start_render()
        self.gui_camera.use()
        for drawable in [
            self.simulation_speed,
            self.cur_agent_text,
            self.tab_text,
            self.right_click_text,
            self.grass_count,
            self.herbivore_count,
            self.carnivore_count,
            self.graph,
            self.time_no_modif_text,
            self.score_text,
            self.logs,
        ]:
            drawable.draw()
        self.map_camera.use()
        self.map.draw()

    def on_update(self, delta_time: float):
        self.time_no_modif += SPEED_MULTIPLIER * delta_time
        self.score += SPEED_MULTIPLIER * delta_time
        for _ in range(SPEED_MULTIPLIER):
            self.map.update()
            self.graph.update()
            self.logs.update()
        self.update_counts()

    def update_agent_text(self):
        self.cur_agent_text.text = (
            f"Click to create: {self.cur_agent.__name__} (use G, H, C to change)"
        )

    def get_data(self) -> List[float]:
        return [
            len(self.map.agents(Grass)),
            len(self.map.agents(Herbivore)),
            len(self.map.agents(Carnivore)),
        ]

    def on_extinction(self, agent: Type[Agent]):
        self.logs.log(f"Extinction of {agent.__name__}")

    def update_counts(self):
        new_count = self.get_data()
        [grass_count, herbivore_count, carnivore_count] = new_count
        self.grass_count.text = f"Grass total: {grass_count}"
        self.herbivore_count.text = f"Herbivores total: {herbivore_count}"
        self.carnivore_count.text = f"Carnivores total: {carnivore_count}"
        self.simulation_speed.text = f"Simulation speed: {SPEED_MULTIPLIER}x (use arrows to change, P to pause/resume)"
        self.time_no_modif_text.text = (
            f"Time without modification: {self.time_no_modif:.1f}s"
        )
        self.score_text.text = f"Score: {self.score:.0f}"
        if min(*new_count) == 0:
            self.score = 0
        for i, agent_type in enumerate([Grass, Herbivore, Carnivore]):
            if new_count[i] == 0 and self.prev_count[i] != 0:
                self.on_extinction(agent_type)
        self.prev_count = new_count

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
        elif symbol == key.TAB:
            agents.SHOW_BARS = not agents.SHOW_BARS
        else:
            return
        self.update_agent_text()

    def adjust_xy_to_map(self, x: float, y: float) -> Tuple[float, float]:
        x -= SCREEN_WIDTH / 2
        y -= SCREEN_HEIGHT / 2
        x *= self.map_camera.scale
        y *= self.map_camera.scale
        return (x + SCREEN_WIDTH / 2, y + SCREEN_HEIGHT / 2)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        mx, my = self.adjust_xy_to_map(x, y)
        if button == arcade.MOUSE_BUTTON_LEFT and self.map.collides_with_point(
            (mx, my)
        ):
            if self.map.create_agent(mx - 25, my + 25, self.cur_agent):
                self.graph.add_vertical_mark()
                self.time_no_modif = 0
                self.score = max(0, self.score - 10)
                last_log = self.logs.last_log()
                name = self.cur_agent.__name__
                if (
                    last_log is not None
                    and last_log.time_elapsed(self.logs.cur_time) < 30
                    and last_log.raw_text.startswith("Created")
                    and last_log.raw_text.endswith(name)
                ):
                    num = int(last_log.raw_text.split(" ", 3)[1])
                    last_log.raw_text = f"Created {num + 1} {name}"
                    last_log.time_log = self.logs.cur_time
                else:
                    self.logs.log(f"Created 1 {name}")
        elif button == arcade.MOUSE_BUTTON_RIGHT and self.map.collides_with_point(
            (mx, my)
        ):
            to_kill = self.map.find_at_point(mx, my)
            for agent in to_kill:
                agent.kill()
                self.logs.log(f"Manually killed {agent.__class__.__name__}")
                self.score = max(0, self.score - 10)
            if len(to_kill) > 0:
                self.graph.add_vertical_mark()
                self.time_no_modif = 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--herbivores-only", action="store_true")
    parser.add_argument("--carnivores-only", action="store_true")
    parser.add_argument("--start-paused", action="store_true")
    args = parser.parse_args()
    if args.start_paused:
        global SPEED_MULTIPLIER
        SPEED_MULTIPLIER = 0
    game = Game(args)
    arcade.run()


if __name__ == "__main__":
    main()
