FROM python:3.8-slim-bookworm

LABEL maintainer="Elijah Rwothoromo <https://github.com/Rwothoromo/snake_game>"

ENV HOME=/home/builduser \
    APP_DIR=/home/builduser/app \
    GLOBAL_ANDROID_PLAT=/home/builduser/.buildozer/android/platform \
    ANDROID_PLAT=/home/builduser/app/.buildozer/android/platform \
    GLOBAL_ANDROID_SDK_ROOT=/home/builduser/.buildozer/android/platform/android-sdk \
    ANDROID_SDK_ROOT=/home/builduser/app/.buildozer/android/platform/android-sdk \
    ANDROID_NDK_HOME=/home/builduser/app/.buildozer/android/platform/android-ndk-r25b \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

# Install dependencies as well as i386 architecture and install 32-bit dependencies
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        autoconf autoconf-archive automake build-essential ccache cmake curl git \
        libcairo2-dev libcups2-dev libbz2-dev libffi-dev libgdbm-dev liblzma-dev \
        libncurses5-dev libncursesw5-dev libnss3-dev libreadline-dev libsqlite3-dev \
        libssl-dev libtinfo5 libtool libtool-bin locales m4 nano openjdk-17-jdk \
        libncurses5:i386 libstdc++6:i386 libgtk2.0-0:i386 \
        patch pkg-config python3-dev python3-pip python3-setuptools sudo unzip wget zip zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set locale
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && locale-gen

# Upgrade pip and install Python dependencies
RUN python -m pip install --upgrade pip setuptools wheel --no-cache-dir && \
    pip install "cython>=0.29,<3.0" "buildozer!=0.33" appdirs colorama pyjnius pyOpenssl python-for-android --no-cache-dir

# Upgrade Cython to 0.28.6 (as root, before switching to builduser)
RUN pip install --upgrade cython==0.28.6

# Create non-root user and directories
RUN useradd -m builduser && \
    mkdir -p $APP_DIR && \
    chown -R builduser:builduser $HOME

# Add builduser to sudoers
RUN echo "builduser ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/builduser && \
    chmod 0440 /etc/sudoers.d/builduser

USER builduser

WORKDIR $APP_DIR

# Copy app files (use --chown if supported)
COPY --chown=builduser:builduser . $APP_DIR

# Download and install Android SDK command-line tools
RUN mkdir -p "$ANDROID_SDK_ROOT/cmdline-tools" && \
    cd "$ANDROID_SDK_ROOT/cmdline-tools" && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O tools.zip && \
    unzip -q tools.zip && rm tools.zip && \
    mv cmdline-tools latest

# Make sdkmanager available at the legacy path
RUN mkdir -p ${ANDROID_SDK_ROOT}/tools/bin && \
    ln -sf ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager ${ANDROID_SDK_ROOT}/tools/bin/sdkmanager

ENV PATH="${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin:${ANDROID_SDK_ROOT}/platform-tools:${HOME}/.local/bin:${PATH}"

# Accept Android SDK licenses
RUN yes | ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager --sdk_root=${ANDROID_SDK_ROOT} --licenses || true

# Install platform-tools and build-tools
RUN yes | $ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_SDK_ROOT \
    "platform-tools" "platforms;android-30" "platforms;android-33" \
    "build-tools;30.0.3" "build-tools;33.0.2"

# Create symbolic links for build-tools and platforms
RUN mkdir -p $GLOBAL_ANDROID_SDK_ROOT && \
    ln -sf ${ANDROID_SDK_ROOT}/build-tools $GLOBAL_ANDROID_SDK_ROOT/build-tools && \
    ln -sf ${ANDROID_SDK_ROOT}/platforms $GLOBAL_ANDROID_SDK_ROOT/platforms

USER root
RUN mkdir -p $ANDROID_NDK_HOME
RUN wget -q https://dl.google.com/android/repository/android-ndk-r25b-linux.zip -O /tmp/ndk.zip \
 && unzip -q /tmp/ndk.zip -d /home/builduser/app/.buildozer/android/platform/ \
 && rm /tmp/ndk.zip
USER builduser

# Create necessary directories
RUN mkdir -p ${HOME}/.local ${HOME}/.android ${APP_DIR}/.buildozer/cache ${APP_DIR}/logs

# Install Python requirements
RUN pip install --no-cache-dir -r requirements.txt

VOLUME $APP_DIR
