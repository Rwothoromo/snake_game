import random

class Food:
    """
    Represents the food in the Snake game.
    """

    def __init__(self, screen_width, screen_height, cell_size):
        """
        Initializes the food with a random position.

        Args:
            screen_width (int): Width of the game screen.
            screen_height (int): Height of the game screen.
            cell_size (int): Size of each grid cell.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = cell_size
        self.position = (0, 0)
        self.randomize_position([])

    def randomize_position(self, snake_positions):
        """
        Randomizes the food's position, ensuring it does not overlap with the snake.

        Args:
            snake_positions (list of tuple): List of the snake's body positions.
        """
        while True:
            x = random.randint(0, (self.screen_width // self.cell_size) - 1) * self.cell_size
            y = random.randint(0, (self.screen_height // self.cell_size) - 1) * self.cell_size
            if (x, y) not in snake_positions:
                self.position = (x, y)
                break

    def get_position(self):
        return self.position

    def respawn(self):
        self.randomize_position([])