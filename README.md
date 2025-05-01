# Snake Game in Python

This is a classic Snake game implemented in Python using the Kivy library. GitHub Copilot was also used. The objective of the game is to control the snake to eat food and grow in length while avoiding collisions with the walls and itself.

## Project Structure

```
snake_game
├── src
│   ├── snake.py        # Contains the Snake class
│   ├── food.py         # Contains the Food class
│   └── game.py         # Contains the Pygame-based Game class (optional)
├── main.py             # Entry point of the game (Kivy-based implementation)
├── requirements.txt    # Lists the dependencies
├── buildozer.spec      # Configuration file for building the APK (Android Package Kit or Android Application Package)
├── .gitignore          # Specifies files and directories to ignore in Git
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
4. Run the game using the following command:
    ```bash
    python main.py
    # python3 -m main # as a module or standalone project
    ```

## How to Build and Run the Game on Android

Follow these steps to package the game for Android using Buildozer:

### Prerequisites

1. Install Python and pip.
2. Install Buildozer and its dependencies:
    ```bash
    pip install buildozer
    sudo apt install -y python3-pip python3-setuptools python3-virtualenv
    sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
    sudo apt install -y libsqlite3-dev
    sudo apt install -y openjdk-17-jdk unzip zlib1g-dev libncurses5 libstdc++6 libgtk2.0-0 libpangox-1.0-0 libpangoxft-1.0-0
    sudo apt install -y cmake
    ```
3. Install Cython (required by Buildozer):
    ```bash
    pip install cython
    ```
4. Initialize Buildozer (if not already done):
    ```bash
    buildozer init
    ```
5. Edit the `buildozer.spec` file to configure your app. Refer to the [Buildozer documentation](https://buildozer.readthedocs.io/en/latest/specifications.html#specifications) and (Android-for-Python documentation)[https://github.com/Android-for-Python/Android-for-Python-Users#changing-buildozerspec] for details.
6. Download the [Android Native Development Kit (NDK)](https://developer.android.com/ndk/downloads/) and [Android SDK Platform-Tools](https://developer.android.com/tools/releases/platform-tools). Set the NDK and SDK paths in `buildozer.spec`:
    ```plaintext
    android.sdk_path = /usr/lib/android-sdk
    android.ndk_path = /home/<username>/android-ndk-r25b
    ```
7. After changing the `buildozer.spec` file (or any of the dependencies), users must do an appclean:
    ```bash
    buildozer appclean
    ```
8. Set the paths in your terminal and check `ANDROIDSDK` and `ANDROIDNDK` paths in your environment:
    ```bash
    export ANDROIDSDK=/usr/lib/android-sdk
    export ANDROIDNDK=/home/<username>/android-ndk-r25b
    echo $ANDROIDSDK
    echo $ANDROIDNDK
    ```
9. Build the APK. This will generate an APK file in the `bin/` directory:
    ```bash
    buildozer android clean
    buildozer -v android debug --log-level 2 > buildozer.log
    ```
10. Run the debug app on a plugged-in phone:
    ```bash
    buildozer android debug deploy run logcat
    ```

### Using JDK 17 for Buildozer

Buildozer works well with JDK 17. Follow these steps to configure JDK 17:

1. Install JDK 17:
    ```bash
    sudo apt install openjdk-17-jdk
    ```

2. Set JDK 17 as the default Java version:
    ```bash
    sudo update-alternatives --config java
    sudo update-alternatives --config javac
    ```

3. Select the option corresponding to JDK 17 (e.g., `/usr/lib/jvm/java-17-openjdk-amd64/bin/java`).

4. Persist JDK 17 in your environment:
    ```bash
    export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
    echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
    echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc
    source ~/.bashrc
    ```

5. Verify the change:
    ```bash
    java -version
    ```
   It should display Java 17.

6. Retry the Buildozer commands:
    ```bash
    buildozer android clean
    buildozer -v android debug --log-level 2 --debug > buildozer.log
    ```

### Install and Run the APK on Android
1. Transfer the APK file to your Android device.
2. Install the APK on your device.
3. Launch the game and enjoy!

## Features

- Control the snake using touch gestures (on Android) or arrow keys (on desktop).
- Eat food to grow the snake.
- The game ends if the snake collides with the walls or itself.
- Adjustable speed and boundary modes (wrap or stay within boundaries).
- Playable on both desktop and Android devices.

Enjoy playing the classic Snake game!