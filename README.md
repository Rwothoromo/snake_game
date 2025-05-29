# Snake Game in Python

A classic Snake 🐍 Game 🎮 implemented in Python using Pygame and Kivy. GitHub Copilot assisted in development. Guide the snake to eat food, grow longer, and avoid collisions with walls or itself.

## Project Structure

```
snake_game
├── src
│   ├── snake.py        # Snake class
│   ├── food.py         # Food class
│   └── game.py         # Pygame-based Game class (optional)
├── main.py             # Entry point (Kivy-based)
├── requirements.txt    # Python dependencies
├── buildozer.spec      # Buildozer config for APK builds
├── Dockerfile          # Dockerfile for Android APK builds
├── docker-compose.yml  # Docker Compose workflow
├── .gitignore          # Git ignore rules
├── best_score.txt      # Stores best score
└── README.md           # Project documentation
```

---

## Running the Game on Desktop

1. **Clone the repository:**
    ```bash
    git clone <repo-url>
    cd snake_game
    ```

2. **Set up a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/macOS
    # venv\Scripts\activate   # Windows
    ```

3. **Install dependencies:**
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install pygame appdirs
    pip install --upgrade python-for-android
    ```

4. **(Optional) Reset best score:**
    ```bash
    echo 0 > best_score.txt
    ```

5. **Run the game:**
    ```bash
    python3 main.py
    ```

---

## Building and Running on Android (with Docker)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed

### Steps

1. **Clone the repository, enter the directory and remove orphan containers.**  
    This ensures a clean environment by deleting unused Docker resources that might interfere with the build process.
    ```bash
    docker-compose down --remove-orphans
    ```

2. **Build and start the Docker container:**
    ```bash
    docker-compose build
    docker-compose run buildozer bash
    ```
    
    Or, without Compose:
    ```bash
    docker build -t kivy-buildozer .
    docker run --dns 8.8.8.8 --rm -it -v "$PWD":/home/builduser/app kivy-buildozer bash
    ```
    
    **Tip:** To avoid cache, add `--no-cache`.

    **Tip:** To clean Buildozer state: `buildozer android clean`.

3. **Build your APK inside the container:**
    ```bash
    # First create all needed directories and fix permissions
    sudo mkdir -p ${APP_DIR}/.buildozer # For project-specific files
    sudo mkdir -p ${HOME}/.buildozer  # Global for shared config
    sudo mkdir -p ${HOME}/.android
    sudo chown -R builduser:builduser ${APP_DIR}/.buildozer
    sudo chown -R builduser:builduser ${HOME}/.buildozer
    sudo chown -R builduser:builduser ${HOME}/.android  

    # Set Google DNS (needs sudo)
    echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf > /dev/null
   
    # First build attempt (will fail but creates directories)
    buildozer android debug || true
   
    # Apply patches
    chmod +x patch_py2to3.sh
    ./patch_py2to3.sh

    # Final build with logging. This captures all output (stdout and stderr use '2>&1'), shows it live (use '| tee' instead of '>'), and saves it to 'logs/buildozer.log'. With '--log-level' (0 - minimal, 1 - normal, 2 - verbose).
    buildozer -v android debug --log-level 2 --debug 2>&1 | tee logs/buildozer.log
    ```
   
    The APK will be generated in the `bin/` directory.

4. **(Optional) Deploy and run on a connected Android device:**
    ```bash
    buildozer android debug deploy run logcat > logs/buildozer.log
    cp logs/buildozer.log logs/buildozer_log.txt
    ```

5. **In case you need to manually download the Android platform-tools:**
    ```bash
    # Manually download and install platform-tools instead of relying on sdkmanager. Create platform-tools directory
    mkdir -p ${ANDROID_SDK_ROOT}/platform-tools

    # Download and install platform-tools directly
    cd ${ANDROID_SDK_ROOT}
    wget -q https://dl.google.com/android/repository/platform-tools_r33.0.3-linux.zip -O platform-tools.zip
    unzip -q platform-tools.zip
    rm platform-tools.zip

    # Return to the app directory
    cd ~/app
    ```

---

## Notes

- **No need to install Buildozer or Android SDK/NDK on your host.** Docker handles all dependencies.
- **Docker runs as a non-root user (`builduser`) to avoid permission issues.**
- **Customize builds by editing `buildozer.spec`.**
- **For advanced Android configuration, see Buildozer docs.**

---

## Features

- Touch controls (Android) and arrow keys (desktop)
- Eat food to grow the snake
- Game over on collision with walls or self
- Adjustable speed and boundary modes (wrap or bounded)
- Playable on desktop and Android
- Score and best score tracking (saved between sessions)

Enjoy playing the classic Snake game!
