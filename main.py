import platform

# This is the main entry point for the Snake game.
# It initializes the game based on the platform (desktop or mobile).
if platform.system() in ["Linux", "Windows", "Darwin"]:
    import pygame
    from src.game import Game

    # Desktop version
    def main_desktop():
        """
        Initializes and runs the desktop version of the Snake game using Pygame.
        """
        print("Running on Desktop")
        pygame.init()
        game = Game()
        game.run()

elif platform.system() not in ["Linux", "Windows", "Darwin"]:
    from kivy.app import App
    from kivy.uix.widget import Widget
    from kivy.graphics import Rectangle, Color
    from kivy.clock import Clock
    from kivy.core.window import Window
    from src.snake import Snake
    from src.food import Food

    # Mobile version
    class SnakeGame(Widget):
        """
        Represents the mobile version of the Snake game using Kivy.
        """

        def __init__(self, **kwargs):
            """
            Initializes the SnakeGame widget for mobile devices.

            Args:
                **kwargs: Additional keyword arguments for the Kivy Widget.
            """
            super().__init__(**kwargs)
            self.cell_size = 20
            self.screen_width = Window.width
            self.screen_height = Window.height
            self.snake = Snake(self.screen_width, self.screen_height, self.cell_size)
            self.food = Food(self.screen_width, self.screen_height, self.cell_size)
            self.speed = 10
            self.boundary_mode = "wrap"  # Boundary mode: "wrap" or "stay"
            self.running = True

            # Schedule the game loop to update at regular intervals
            Clock.schedule_interval(self.update, 1.0 / self.speed)

        def on_touch_down(self, touch):
            """
            Handles touch input to control the snake's direction.

            Args:
                touch: The touch event containing the position of the touch.
            """
            x, y = touch.pos
            head_x, head_y = self.snake.get_head_position()

            # Determine the direction based on the touch position relative to the snake's head
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

            Args:
                dt: The time elapsed since the last update.
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

            # Handle boundary modes
            if self.boundary_mode == "wrap":
                # Wrap around the screen
                head_x %= self.screen_width
                head_y %= self.screen_height
                self.snake.positions[0] = (head_x, head_y)
            elif self.boundary_mode == "stay":
                # End the game if the snake hits the boundary
                if head_x < 0 or head_x >= self.screen_width or head_y < 0 or head_y >= self.screen_height:
                    self.running = False

            # Check collision with itself
            if self.snake.get_head_position() in self.snake.get_positions()[1:]:
                self.running = False

            # Check collision with food
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
                    Color(0, 1, 0)  # Green color for the snake
                    Rectangle(pos=segment, size=(self.cell_size, self.cell_size))

                # Draw the food
                Color(1, 0, 0)  # Red color for the food
                Rectangle(pos=self.food.position, size=(self.cell_size, self.cell_size))

    class SnakeApp(App):
        """
        Represents the Kivy application for the Snake game on mobile devices.
        """

        def build(self):
            """
            Builds and returns the SnakeGame widget.

            Returns:
                SnakeGame: The main game widget.
            """
            print("Running on Android")
            return SnakeGame()


if __name__ == "__main__":
    if platform.system() in ["Linux", "Windows", "Darwin"]:
        # Run the desktop version
        main_desktop()
    else:
        # Run the mobile version
        SnakeApp().run()
