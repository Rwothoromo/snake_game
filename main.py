from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.core.window import Window
from src.snake import Snake
from src.food import Food

Window.size = (Window.width, Window.height)

class SnakeGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Window.bind(on_keyboard = self.keyboard)
        
        self.cell_size = 20
        self.screen_width = Window.width
        self.screen_height = Window.height
        self.snake = Snake(self.screen_width, self.screen_height, self.cell_size)
        self.food = Food(self.screen_width, self.screen_height, self.cell_size)
        self.speed = 10
        self.boundary_mode = "wrap"
        self.running = True

        # Schedule the game loop
        Clock.schedule_interval(self.update, 1.0 / self.speed)

    # def keyboard(self, window, key, *args):
    #     if key == 27 and self.sm.current != "main":
    #         self.current = some_previous_screen
    #         return True   # key event consumed by app
    #     else:           
    #         return False  # key event passed to Android
    
    def on_touch_down(self, touch):
        """
        Handles touch input to control the snake's direction.
        """
        x, y = touch.pos
        head_x, head_y = self.snake.get_head_position()

        if x > head_x and abs(x - head_x) > abs(y - head_y):  # Move right
            self.snake.set_direction((self.cell_size, 0))
        elif x < head_x and abs(x - head_x) > abs(y - head_y):  # Move left
            self.snake.set_direction((-self.cell_size, 0))
        elif y > head_y:  # Move up
            self.snake.set_direction((0, self.cell_size))
        elif y < head_y:  # Move down
            self.snake.set_direction((0, -self.cell_size))

    def update(self, dt):
        """
        Updates the game state on each frame.
        """
        if not self.running:
            return

        self.snake.move()
        self.check_collisions()
        self.render()

    def check_collisions(self):
        """
        Checks for collisions between the snake and the walls, itself, or the food.
        """
        head_x, head_y = self.snake.get_head_position()

        if self.boundary_mode == "wrap":
            head_x %= self.screen_width
            head_y %= self.screen_height
            self.snake.positions[0] = (head_x, head_y)
        elif self.boundary_mode == "stay":
            if head_x < 0 or head_x >= self.screen_width or head_y < 0 or head_y >= self.screen_height:
                self.running = False

        if self.snake.get_head_position() in self.snake.get_positions()[1:]:
            self.running = False

        if self.snake.get_head_position() == self.food.position:
            self.snake.grow()
            self.food.randomize_position(self.snake.get_positions())

    def render(self):
        """
        Renders the snake and food on the screen.
        """
        self.canvas.clear()
        with self.canvas:
            # Draw the snake
            for segment in self.snake.get_positions():
                Color(0, 1, 0)
                Rectangle(pos=segment, size=(self.cell_size, self.cell_size))

            # Draw the food
            Color(1, 0, 0)
            Rectangle(pos=self.food.position, size=(self.cell_size, self.cell_size))


# Desktop version
import pygame
import sys
from src.game import Game
import platform

def main_desktop():
    pygame.init()
    game = Game()
    game.run()

class SnakeApp(App):
    def build(self):
        return SnakeGame()

if __name__ == "__main__":
    if platform.system() == "Linux" or platform.system() == "Windows" or platform.system() == "Darwin":
        main_desktop()
    else:
        SnakeApp().run()
