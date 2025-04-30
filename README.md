# Snake Game in Python

This is a classic Snake game implemented in Python using the Pygame library. The objective of the game is to control the snake to eat food and grow in length while avoiding collisions with the walls and itself.

## Project Structure

```
snake_game
├── src
│   ├── main.py       # Entry point of the game
│   ├── snake.py      # Contains the Snake class
│   ├── food.py       # Contains the Food class
│   └── game.py       # Contains the Game class
├── requirements.txt   # Lists the dependencies
└── README.md          # Documentation for the project
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
4. Run the game using the following command:

```bash
python src/main.py
# Alt way to run it as a module or standalone project
# python3 -m src.main
```

## Features

- Control the snake using arrow keys.
- Eat food to grow the snake.
- The game ends if the snake collides with the walls or itself.
- Score tracking based on the number of food items eaten.

Enjoy playing the classic Snake game!