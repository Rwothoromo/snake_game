import random  # For generating random obstacle positions
import pygame
import sys
from .snake import Snake
from .food import Food

class Game:
    """
    Represents the Snake game. Manages the game loop, rendering, and interactions between the snake, food, and obstacles.
    """

    def __init__(self):
        """
        Initializes the game, including the screen, clock, snake, food, and obstacles.
        """
        pygame.init()
        self.screen_width = 400
        self.screen_height = 400
        self.cell_size = 10  # Ensure cell_size is initialized before use
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.snake = Snake()
        self.food = Food(self.screen_width, self.screen_height, self.cell_size)
        self.running = True
        self.speed = 10  # Initial speed (lower value = slower snake)
        self.font = pygame.font.Font(None, 24)  # Font for displaying speed
        self.boundary_mode = "wrap"  # Options: "wrap" or "stay"
        self.obstacles_enabled = False  # Whether obstacles are enabled
        self.obstacles = []  # List of obstacle positions

    def generate_obstacles(self, count=5):
        """
        Generates random obstacles on the screen.

        Args:
            count (int): Number of obstacles to generate.
        """
        # Ensure cell_size and screen dimensions are initialized before use
        if not hasattr(self, 'cell_size') or not hasattr(self, 'screen_height'):
            raise AttributeError("Game attributes 'cell_size' and 'screen_height' must be initialized before generating obstacles.")

        self.obstacles = []
        for _ in range(count):
            while True:
                x = random.randint(0, (self.screen_width // self.cell_size) - 1) * self.cell_size
                y = random.randint(0, (self.screen_height // self.cell_size) - 1) * self.cell_size
                if (x, y) not in self.snake.get_positions() and (x, y) != self.food.get_position():
                    self.obstacles.append((x, y))
                    break

    def handle_events(self):
        """
        Handles user input events, such as quitting the game or changing the snake's direction.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snake.set_direction((0, -self.cell_size))
                elif event.key == pygame.K_DOWN:
                    self.snake.set_direction((0, self.cell_size))
                elif event.key == pygame.K_LEFT:
                    self.snake.set_direction((-self.cell_size, 0))
                elif event.key == pygame.K_RIGHT:
                    self.snake.set_direction((self.cell_size, 0))
                elif event.key == pygame.K_MINUS:  # Slow down the snake
                    self.speed = max(5, self.speed - 1)  # Minimum speed limit
                elif event.key == pygame.K_EQUALS:  # Speed up the snake
                    self.speed = min(20, self.speed + 1)  # Maximum speed limit
                elif event.key == pygame.K_b:  # Toggle boundary mode
                    self.boundary_mode = "wrap" if self.boundary_mode == "stay" else "stay"
                elif event.key == pygame.K_o:  # Toggle obstacles
                    self.obstacles_enabled = not self.obstacles_enabled
                    if self.obstacles_enabled:
                        self.generate_obstacles()
                    else:
                        self.obstacles = []  # Clear obstacles when toggled off

    def check_collisions(self):
        """
        Checks for collisions between the snake and the walls, itself, food, or obstacles.
        """
        head_x, head_y = self.snake.get_head_position()

        if self.boundary_mode == "wrap":
            # Wrap around the screen
            head_x %= self.screen_width
            head_y %= self.screen_height
            self.snake.positions[0] = (head_x, head_y)
        elif self.boundary_mode == "stay":
            # Check collision with walls
            if head_x < 0 or head_x >= self.screen_width or head_y < 0 or head_y >= self.screen_height:
                self.running = False

        # Check collision with itself
        if self.snake.get_head_position() in self.snake.get_positions()[1:]:
            self.running = False

        # Check collision with food
        if self.snake.get_head_position() == self.food.position:
            self.snake.grow()
            self.food.randomize_position(self.snake.get_positions())

        # Check collision with obstacles
        if self.obstacles_enabled and self.snake.get_head_position() in self.obstacles:
            self.running = False

    def render(self):
        """
        Renders the game objects (snake, food, obstacles, and UI) on the screen.
        """
        self.screen.fill((0, 0, 0))  # Clear the screen with black

        # Draw the snake
        for segment in self.snake.get_positions():
            pygame.draw.rect(self.screen, (0, 255, 0), pygame.Rect(segment[0], segment[1], self.cell_size, self.cell_size))

        # Draw the food
        pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(self.food.position[0], self.food.position[1], self.cell_size, self.cell_size))

        # Draw the obstacles
        if self.obstacles_enabled:
            for obstacle in self.obstacles:
                pygame.draw.rect(self.screen, (128, 128, 128), pygame.Rect(obstacle[0], obstacle[1], self.cell_size, self.cell_size))

        # Draw the speed UI
        speed_text = self.font.render(f"Speed: {self.speed}", True, (255, 255, 255))
        self.screen.blit(speed_text, (10, 10))

        # Draw the boundary mode UI
        boundary_text = self.font.render(f"Boundary: {self.boundary_mode}", True, (255, 255, 255))
        self.screen.blit(boundary_text, (10, 30))

        # Draw the obstacles UI
        obstacles_text = self.font.render(f"Obstacles: {'On' if self.obstacles_enabled else 'Off'}", True, (255, 255, 255))
        self.screen.blit(obstacles_text, (10, 50))

        pygame.display.flip()  # Update the display

    def game_over(self):
        """
        Displays the game over screen and waits for the player to quit or restart.
        """
        font = pygame.font.Font(None, 36)
        self.screen.fill((0, 0, 0))  # Clear the screen with black

        # Render the three lines of the game over message
        line1 = font.render("Game Over!", True, (255, 255, 255))
        line2 = font.render("Press R to Restart", True, (255, 255, 255))
        line3 = font.render("Or Q to Quit", True, (255, 255, 255))

        # Position the lines on the screen
        self.screen.blit(line1, (self.screen_width // 2 - line1.get_width() // 2, self.screen_height // 2 - 40))
        self.screen.blit(line2, (self.screen_width // 2 - line2.get_width() // 2, self.screen_height // 2))
        self.screen.blit(line3, (self.screen_width // 2 - line3.get_width() // 2, self.screen_height // 2 + 40))

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Restart the game
                        return True
                    elif event.key == pygame.K_q:  # Quit the game
                        pygame.quit()
                        sys.exit()

    def run(self):
        """
        Runs the main game loop.
        """
        while self.running:
            self.handle_events()
            self.snake.move()
            self.check_collisions()
            self.render()
            self.clock.tick(self.speed)  # Adjust the game speed based on the speed attribute

        # Show the game over screen
        if self.game_over():
            self.__init__()  # Reinitialize the game
            self.run()