import random
from .constants import UI_TOP_TEXT_HEIGHT

class Food:
    """
    Represents the food in the Snake game.
    """

    def __init__(self, screen_width, screen_height, cell_size, play_area_top=UI_TOP_TEXT_HEIGHT):
        """
        Initializes the food with a random position.

        Args:
            screen_width (int): Width of the game screen.
            screen_height (int): Height of the game screen.
            cell_size (int): Size of each grid cell.
            play_area_top (int): The top boundary of the play area.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = cell_size
        self.play_area_top = play_area_top  # Ensure food stays below this boundary
        self.position = (0, 0)
        self.randomize_position([])

    def randomize_position(self, snake_positions):
        """
        Randomizes the food's position, ensuring it does not overlap with the snake
        and stays within the playable area.

        Args:
            snake_positions (list of tuple): List of the snake's body positions.
        """
        valid_positions = []

        # Generate all valid positions within the grid
        for x in range(0, self.screen_width, self.cell_size):
            for y in range(self.play_area_top, self.screen_height, self.cell_size):
                if (x, y) not in snake_positions:
                    valid_positions.append((x, y))

        # Randomly select a position from the valid ones
        if valid_positions:
            self.position = random.choice(valid_positions)

    def get_position(self):
        """
        Returns the current position of the food.

        Returns:
            tuple: (x, y) coordinates of the food.
        """
        return self.position

    def respawn(self, snake_positions):
        """
        Respawns the food at a new random position.

        Args:
            snake_positions (list of tuple): List of the snake's body positions.
        """
        self.randomize_position(snake_positions)