# Snake Game in Python

This is a classic Snake 🐍 Game 🎮 implemented in Python using the Pygame and Kivy libraries. GitHub Copilot was also used. The objective of the game is to control the snake to eat food and grow in length while avoiding collisions with the walls and itself.

## Project Structure

```
snake_game
├── src
│   ├── snake.py        # Contains the Snake class
│   ├── food.py         # Contains the Food class
│   └── game.py         # Contains the Pygame-based Game class (optional)
├── main.py             # Entry point of the game (Kivy-based implementation)
├── requirements.txt    # Lists the dependencies
├── buildozer.spec      # Config file for building the APK (Android Package Kit or Android Application Package)
├── Dockerfile          # Dockerfile for building Android APKs
├── docker-compose.yml  # Compose file for Docker workflow
├── .gitignore          # Specifies files and directories to ignore in Git
├── best_score.txt      # Stores the best score
└── README.md           # Documentation for the project
```

---

## How to Run the Game on Desktop (Python)

1. **Clone the repository or download the project files.**

2. **Navigate to the project directory.**

3. **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # venv\Scripts\activate   # On Windows
    ```

4. **Install dependencies:**
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install pygame appdirs
    pip install --upgrade python-for-android
    ```

5. **(Optional) Reset the best score:**
    ```bash
    echo 0 > best_score.txt
    ```

6. **Run the game:**
    ```bash
    python3 main.py
    ```

---

## How to Build and Run the Game on Android (via Docker)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed on your system.

### Steps

1. **Clone the repository and navigate to the project directory.**

2. **Build or Re-Build the Docker image:**
    ```bash
    docker-compose build
    ```
    Or, if you prefer not to use Compose:
    ```bash
    docker build -t kivy-buildozer .
    ```
    Or, without reusing cache:
    ```bash
    docker build --no-cache -t kivy-buildozer .
    ```

    **Tip:** To clean up any orphaned containers from previous runs, you can run:
    ```bash
    docker-compose down --remove-orphans
    ```

3. **Start a shell in the Docker container (as a non-root user):**
    ```bash
    docker-compose run buildozer bash
    ```
    Or, without Compose:
    ```bash
    docker run --rm -it -v "$PWD":/app kivy-buildozer bash
    ```

4. **Inside the Docker container, build the APK:**

    First, add the local bin directory to your PATH (to avoid missing script warnings):
    ```bash
    export PATH="$PATH:/home/builduser/.local/bin"
    ```

    You can do a buildozer clean up if need be:
    ```bash
    buildozer android clean
    ```

    The generated APK will be in the `bin/` directory on your host machine.

5. **(Optional) Deploy and run the debug app directly on a plugged-in phone:**
    ```bash
    buildozer android debug deploy run logcat > logs/buildozer.log
    cp logs/buildozer.log logs/buildozer_log.txt
    ```

6. **Transfer the APK to your Android device and install it.**

---

## Notes

- **You do not need to install Buildozer or Android SDK/NDK on your host machine.** The Docker image handles all dependencies.
- **The Docker image runs as a non-root user (`builduser`) to avoid permission issues.**
- **If you want to customize the build, edit `buildozer.spec` before building.**
- **For advanced Android SDK/NDK configuration, see the Buildozer documentation.**

---

## Features

- Control the snake using touch gestures (on Android) or arrow keys (on desktop).
- Eat food to grow the snake.
- The game ends if the snake collides with the walls or itself.
- Adjustable speed and boundary modes (wrap or stay within boundaries).
- Playable on both desktop and Android devices.
- Score tracking based on the number of food items eaten.
- Best score saved between sessions.

Enjoy playing the classic Snake game!
