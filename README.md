# Snake Game in Python

This is a classic Snake game implemented in Python using the Pygame library. GitHub Copilot was also used. The objective of the game is to control the snake to eat food and grow in length while avoiding collisions with the walls and itself.

## Project Structure

```
snake_game
├── src
│   ├── snake.py        # Contains the Snake class
│   ├── food.py         # Contains the Food class
│   └── game.py         # Contains the Game class
├── requirements.txt    # Lists the dependencies
├── main.py             # Entry point of the game
├── best_score.txt      # Stores the best score
└── README.md           # Documentation for the project
```

## Requirements

To run this game, you need to have Python installed.

## How to Run the Game

1. Clone the repository or download the project files.
2. Navigate to the project directory.
3. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/macOS
   venv\Scripts\activate     # On Windows
   pip install -r requirements.txt
   ```
4. Reset the best score (optional):
   - Open the `best_score.txt` file in the root directory and set its content to `0`. Or run:
   ```bash
   echo 0 > best_score.txt
   ```

5. Run the game using the following command:
   ```bash
   python main.py
   ```

## Features

- Control the snake using arrow keys.
- Eat food to grow the snake.
- The game ends if the snake collides with the walls or itself.
- Score tracking based on the number of food items eaten.
- Best score saved between sessions.

Enjoy playing the classic Snake game!