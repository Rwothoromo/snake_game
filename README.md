# Snake Game in Python

This is a classic Snake game implemented in Python using the Pygame and Kivy libraries. GitHub Copilot was also used. The objective of the game is to control the snake to eat food and grow in length while avoiding collisions with the walls and itself.

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
├── .gitignore          # Specifies files and directories to ignore in Git
├── best_score.txt      # Stores the best score
└── README.md           # Documentation for the project
```

## Requirements

To run this game, you need to have Python installed.

## How to Run the Game (For Python - Desktop)

1. Clone the repository or download the project files.
2. Navigate to the project directory.
3. Install Python 3.8 ([steps](https://askubuntu.com/questions/1493434/how-to-install-python3-8-on-ubuntu-23-04)).
    ```bash
    sudo apt-get update

    sudo apt-get install -y build-essential libssl-dev \
    zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
    wget curl llvm libncurses5-dev libncursesw5-dev xz-utils \
    tk-dev libffi-dev liblzma-dev python3-openssl git libcairo2-dev \
    libcups2-dev libdbus-1-dev

    export LDFLAGS="-lm"

    mkdir ~/python38
    cd ~/python38
    wget https://www.python.org/ftp/python/3.8.16/Python-3.8.16.tgz
    tar -xf Python-3.8.16.tgz

    cd Python-3.8.16

    ./configure --enable-optimizations
    make -j$(nproc)
    sudo make install
    python3.8 --version
    ```
4. Create and activate a virtual environment:
    ```bash
    python3.8 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate     # On Windows
    ```
5. Install the required dependencies:
    ```bash
    pip install --no-cache-dir -r requirements.txt
    ```
6. Reset the best score (optional) - Open `best_score.txt` and set its content to `0`. Or run:
    ```bash
    echo 0 > best_score.txt
    ```
7. Run the game using the following command:
    ```bash
    python3.8 main.py
    # python3.8 -m main # as a module or standalone project
    ```

## How to Build and Run the Game on Android

Follow these steps to package the game for Android using Buildozer:

### Prerequisites

1. Install pip.
2. Install Buildozer and its dependencies:
    ```bash
    pip install buildozer

    sudo apt install -y python3-pip python3-setuptools \
    python3-virtualenv openjdk-17-jdk unzip libstdc++6 libgtk2.0-0 \
    libpangoxft-1.0-0 libjaxb-java cmake
    ```
3. Initialize Buildozer (if not already done):
    ```bash
    buildozer init
    ```
4. Edit the `buildozer.spec` file to configure your app. Refer to the [Buildozer documentation](https://buildozer.readthedocs.io/en/latest/specifications.html#specifications) and [Android-for-Python documentation](https://github.com/Android-for-Python/Android-for-Python-Users#changing-buildozerspec) for details.
5. Download the [Android Native Development Kit (NDK)](https://developer.android.com/ndk/downloads/) and [Android SDK Platform-Tools](https://developer.android.com/tools/releases/platform-tools). Set the NDK and SDK paths in `buildozer.spec`:
    ```plaintext
    android.sdk_path = /home/<username>/Desktop/code/copilot/snake_game/.buildozer/android/platform/android-sdk
    android.ndk_path = /home/<username>/android-ndk-r25b
    ```
6. (Optional) After changing `buildozer.spec`, you can do a complete appclean:
    ```bash
    buildozer appclean
    ```
7. (In a separate terminal) Install Android Command-Line Tools: Download and install the Android SDK command-line tools:
    ```bash
    mkdir -p .buildozer/android/platform/android-sdk/cmdline-tools/latest/
    cd .buildozer/android/platform/android-sdk/cmdline-tools/latest/
    wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip -O cmdline-tools.zip
    unzip cmdline-tools.zip
    mv cmdline-tools/* .
    rmdir cmdline-tools
    ```
8. Set the relevant paths in your terminal and check them in your environment:
    ```bash
    export ANDROIDSDK=$(pwd)/.buildozer/android/platform/android-sdk
    export ANDROIDNDK=$HOME/android-ndk-r25b
    export ANDROID_HOME=$(pwd)/.buildozer/android/platform/android-sdk
    export ANDROID_SDK_ROOT=$(pwd)/.buildozer/android/platform/android-sdk

    echo $ANDROIDSDK
    echo $ANDROIDNDK
    echo $ANDROID_HOME
    echo $ANDROID_SDK_ROOT
    ```
9. Persist the environment variables:
    ```bash
    echo 'export ANDROIDSDK=$(pwd)/.buildozer/android/platform/android-sdk' >> ~/.bashrc
    echo 'export ANDROIDNDK=$HOME/android-ndk-r25b' >> ~/.bashrc
    echo 'export ANDROID_HOME=$(pwd)/.buildozer/android/platform/android-sdk' >> ~/.bashrc
    echo 'export ANDROID_SDK_ROOT=$(pwd)/.buildozer/android/platform/android-sdk' >> ~/.bashrc
    source ~/.bashrc
    ```
10. (In a new terminal) Verify the Installation: Ensure the `sdkmanager` tool is available:
    ```bash
    ls -l .buildozer/android/platform/android-sdk/cmdline-tools/latest/bin/sdkmanager
    .buildozer/android/platform/android-sdk/cmdline-tools/latest/bin/sdkmanager --list
    ```
11. Accept SDK Licenses: Accept the Android SDK licenses to avoid further issues:
    ```bash
    .buildozer/android/platform/android-sdk/cmdline-tools/latest/bin/sdkmanager --licenses -y
    ```
    This should resolve the issue with the missing `sdkmanager`.
12. Automatically fix missing libs:
    ```bash
    chmod +x fix_buildozer_jdk17.sh
    ./fix_buildozer_jdk17.sh
    ```
    Make sure buildozer android has already initialized your .buildozer folder before running this script.
13. Or manually create a `jaxb-libs` directory:
    ```bash
    mkdir .buildozer/jaxb-libs/
    ```
14. Then download these JARs into it:
    | Library                | Suggested Version |
    | ---------------------- | ----------------- |
    | [jakarta.xml.bind-api](https://mvnrepository.com/artifact/jakarta.xml.bind/jakarta.xml.bind-api/2.3.3) | `2.3.3` or later |
    | [jaxb-runtime](https://mvnrepository.com/artifact/org.glassfish.jaxb/jaxb-runtime/2.3.3)         | `2.3.3` or later   |
    | [javax.activation-api](https://mvnrepository.com/artifact/jakarta.activation/jakarta.activation-api/1.2.2) | `1.2.0`  |
    | [jaxb-core](https://mvnrepository.com/artifact/com.sun.xml.bind/jaxb-core/2.3.0) (optional) | `2.3.0` or later    |
    This will ensure that `javax.xml.bind` module is resolved for JDK 17.
15. Override the wrong/old sdkmanager path with a symbolic link:
    ```bash
    rm -f .buildozer/android/platform/android-sdk/tools/bin/sdkmanager
    mkdir -p .buildozer/android/platform/android-sdk/tools/bin
    ln -s .buildozer/android/platform/android-sdk/cmdline-tools/latest/bin/ .buildozer/android/platform/android-sdk/tools/bin/sdkmanager

    .buildozer/android/platform/android-sdk/tools/bin/sdkmanager --list
    ```
16. Build the APK. This will generate an APK file in the `bin/` directory:
    ```bash
    buildozer android clean
    buildozer -v android debug --log-level 2 --debug > logs/buildozer.log
    cp logs/buildozer.log logs/buildozer_log.txt
    ```
17. Or deploy and run the debug app directly on a plugged-in phone:
    ```bash
    buildozer android debug deploy run logcat > logs/buildozer.log
    cp logs/buildozer.log logs/buildozer_log.txt
    ```
18. To check logs when running the app:
    ```bash
    adb logcat | grep "com.rwothoromo.game.snakegame" | grep -A 10 -B 10 "ANR" > logs/android_apk.log
    cp logs/android_apk.log logs/android_apk_log.txt
    ```
    This captures 10 lines before and after each Application Not Responding (ANR) error.

### Using JDK 17 for Buildozer

Buildozer works well with JDK 17. Follow these steps to configure JDK 17:

1. Set JDK 17 as the default Java version:
    ```bash
    sudo update-alternatives --config java
    sudo update-alternatives --config javac
    ```
2. Select the option corresponding to JDK 17 (e.g., `/usr/lib/jvm/java-17-openjdk-amd64/bin/java`).
3. Persist JDK 17 in your environment:
    ```bash
    export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
    echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
    echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc
    source ~/.bashrc
    ```
4. Verify the change:
    ```bash
    java -version
    ```
   It should display Java 17.


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
- Score tracking based on the number of food items eaten.
- Best score saved between sessions.

Enjoy playing the classic Snake game!

apktool d your_app.apk