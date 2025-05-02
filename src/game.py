import random  # For generating random obstacle positions
import pygame
import sys
import os  # For file operations
from .snake import Snake
from .food import Food
from .constants import UI_TOP_TEXT_HEIGHT, BEST_SCORE_FILE

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
        self.play_area_top = UI_TOP_TEXT_HEIGHT  # Adjust the play area to start below the UI
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.snake = Snake(self.screen_width, self.screen_height, self.cell_size)
        self.food = Food(self.screen_width, self.screen_height - UI_TOP_TEXT_HEIGHT, self.cell_size)
        self.running = True
        self.speed = 10  # Initial speed (lower value = slower snake)
        self.font = pygame.font.Font(None, 24)  # Font for displaying UI
        self.boundary_mode = "Wrap"  # Options: "Wrap" or "Stay"
        self.obstacles_enabled = False  # Whether obstacles are enabled
        self.obstacles = []  # List of obstacle positions
        self.score = 0  # Current score
        self.best_score = self.load_best_score()  # Load the best score from file

    def load_best_score(self):
        """
        Loads the best score from a file. If the file does not exist, returns 0.

        Returns:
            int: The best score.
        """
        if os.path.exists(BEST_SCORE_FILE):
            with open(BEST_SCORE_FILE, "r") as file:
                try:
                    return int(file.read().strip())
                except ValueError:
                    return 0  # Default to 0 if the file is corrupted
        return 0

    def save_best_score(self):
        """
        Saves the best score to a file.
        """
        try:
            with open(BEST_SCORE_FILE, "w") as file:
                file.write(str(self.best_score))
        except (IOError, OSError) as e:
            print(f"Error saving best score: {e}")

    def generate_obstacles(self, count=5):
        """
        Generates random obstacles on the screen.

        Args:
            count (int): Number of obstacles to generate.
        """
        self.obstacles = []
        # Calculate all possible positions on the grid
        all_positions = [
            (x * self.cell_size, y * self.cell_size)
            for x in range(self.screen_width // self.cell_size)
            for y in range((self.play_area_top // self.cell_size) + 1, self.screen_height // self.cell_size)
        ]
        # Filter out positions occupied by the snake or food
        available_positions = [
            pos for pos in all_positions
            if pos not in self.snake.get_positions() and pos != self.food.get_position()
        ]
        # Check if there are enough available positions
        if len(available_positions) < count:
            print(f"Warning: Not enough space for {count} obstacles. Generating {len(available_positions)} obstacles instead.")
            count = len(available_positions)
        # Generate obstacles
        for _ in range(count):
            attempts = 0
            while attempts < 100:  # Limit the number of attempts to prevent infinite loop
                x, y = random.choice(available_positions)
                if (x, y) not in self.obstacles:  # Ensure no duplicate obstacles
                    self.obstacles.append((x, y))
                    break
                attempts += 1
            else:
                print("Warning: Could not place all obstacles due to space constraints.")

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
                    self.boundary_mode = "Wrap" if self.boundary_mode == "Stay" else "Stay"
                elif event.key == pygame.K_o:  # Toggle obstacles
                    self.obstacles_enabled = not self.obstacles_enabled
                    if self.obstacles_enabled:
                        self.generate_obstacles()
                    else:
                        self.obstacles = []  # Clear obstacles when toggled off
                else:
                    # Ignore unrecognized key presses
                    print(f"Unrecognized key pressed: {event.key}")

    def check_collisions(self):
        """
        Checks for collisions between the snake and the walls, itself, food, or obstacles.
        """
        head_x, head_y = self.snake.get_head_position()

        if self.boundary_mode == "Wrap":
            # Wrap around the screen, allowing the snake to pass through all edges
            head_x %= self.screen_width
            head_y = (head_y - self.play_area_top) % (self.screen_height - self.play_area_top) + self.play_area_top
            self.snake.positions[0] = (head_x, head_y)
        elif self.boundary_mode == "Stay":
            # Check collision with walls, including the top boundary (text area)
            if (
                head_x < 0 or head_x >= self.screen_width or
                head_y < self.play_area_top or head_y >= self.screen_height
            ):
                self.running = False

        # Check collision with itself
        if self.snake.get_head_position() in self.snake.get_positions()[1:]:
            self.running = False

        # Check collision with food
        if self.snake.get_head_position() == self.food.position:
            self.snake.grow()
            self.food.randomize_position(self.snake.get_positions())
            self.score += 1  # Increment score when food is eaten

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

        # Draw the score UI
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

        # Draw the best score UI
        best_score_text = self.font.render(f"Best: {self.best_score}", True, (255, 255, 255))
        self.screen.blit(best_score_text, (10, 30))

        # Draw the boundary mode UI with toggle key
        boundary_text = self.font.render(f"Boundary: {self.boundary_mode} - Press 'B'", True, (255, 255, 255))
        self.screen.blit(boundary_text, (10, 50))

        # Draw the obstacles UI with toggle key
        obstacles_text = self.font.render(f"Obstacles: {'On' if self.obstacles_enabled else 'Off'} - Press 'O'", True, (255, 255, 255))
        self.screen.blit(obstacles_text, (10, 70))

        # Draw the speed controls
        speed_text = self.font.render(f"Speed: {self.speed} - Press '=' or '-'", True, (255, 255, 255))
        self.screen.blit(speed_text, (10, 90))

        # Draw a white line below the text area
        pygame.draw.line(self.screen, (255, 255, 255), (0, self.play_area_top), (self.screen_width, self.play_area_top), 2)

        pygame.display.flip()  # Update the display

    def game_over(self):
        """
        Displays the game over screen and waits for the player to quit or restart.
        Updates the best score if the current score exceeds it.
        """
        if self.score > self.best_score:
            self.best_score = self.score  # Update best score
            self.save_best_score()  # Save the new best score to file

        font = pygame.font.Font(None, 36)
        self.screen.fill((0, 0, 0))  # Clear the screen with black

        # Render the game over message
        line1 = font.render("Game Over!", True, (255, 255, 255))
        line2 = font.render(f"Score: {self.score}", True, (255, 255, 255))
        line3 = font.render(f"Best: {self.best_score}", True, (255, 255, 255))
        line4 = font.render("Press R to Restart or Q to Quit", True, (255, 255, 255))

        # Position the lines on the screen
        self.screen.blit(line1, (self.screen_width // 2 - line1.get_width() // 2, self.screen_height // 2 - 60))
        self.screen.blit(line2, (self.screen_width // 2 - line2.get_width() // 2, self.screen_height // 2 - 30))
        self.screen.blit(line3, (self.screen_width // 2 - line3.get_width() // 2, self.screen_height // 2))
        self.screen.blit(line4, (self.screen_width // 2 - line4.get_width() // 2, self.screen_height // 2 + 30))

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

    def restart_game(self):
        """
        Reinitializes the game state for a restart.
        """
        self.snake = Snake(self.screen_width, self.screen_height, self.cell_size)
        self.food = Food(self.screen_width, self.screen_height, self.cell_size, self.play_area_top)  # Ensure food respects play_area_top
        self.running = True
        self.speed = 10
        self.score = 0
        self.obstacles = []
        if self.obstacles_enabled:
            self.generate_obstacles()

    def update(self):
        """
        Updates the game state, including moving the snake and checking for collisions.
        """
        self.snake.move()
        self.check_collisions()

    def run(self):
        """
        Runs the main game loop.
        """
        while self.running:
            self.handle_events()
            self.update()  # Update the game state
            self.render()  # Render the game objects
            self.clock.tick(self.speed)  # Adjust the game speed based on the speed attribute

        # Show the game over screen
        if self.game_over():
            self.__init__()  # Reinitialize the game
            self.run()