FROM python:3.8-slim-bookworm

# Set environment variables for SDK/NDK if you're managing them manually
# Otherwise, Buildozer will download them to ~/.buildozer/android/platform/
ENV HOME=/home/builduser
ENV APP_DIR=${HOME}/app
ENV GLOBAL_ANDROID_PLAT=${HOME}/.buildozer/android/platform
ENV ANDROID_PLAT=${APP_DIR}/.buildozer/android/platform
ENV GLOBAL_ANDROID_SDK_ROOT=${GLOBAL_ANDROID_PLAT}/android-sdk
ENV ANDROID_SDK_ROOT=${ANDROID_PLAT}/android-sdk
ENV ANDROID_NDK_HOME=${ANDROID_PLAT}/android-ndk-r25b

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    autoconf \
    autoconf-archive \
    automake \
    build-essential \
    cmake \
    curl \
    git \
    libcairo2-dev \
    libcups2-dev \
    libbz2-dev \
    libffi-dev \
    libgdbm-dev \
    liblzma-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libnss3-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    libtinfo5 \
    libtool \
    libtool-bin \
    locales \
    m4 \
    nano \
    openjdk-17-jdk \
    patch \
    pkg-config \
    python3-dev \
    python3-pip \
    python3-setuptools \
    sudo \
    unzip \
    wget \
    zip \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set locale
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && locale-gen

# Set environment variables
ENV LANG=en_US.UTF-8  
ENV LANGUAGE=en_US:en  
ENV LC_ALL=en_US.UTF-8

# Upgrade pip and install Python dependencies
RUN --mount=type=cache,target=/root/.cache/pip pip install --upgrade pip setuptools wheel python-for-android appdirs buildozer colorama cython pyjnius

# Test internet connectivity
RUN curl -sS https://www.google.com > /dev/null || exit 1

# Download and install Android SDK command-line tools
RUN mkdir -p "$ANDROID_SDK_ROOT/cmdline-tools" && \
    cd "$ANDROID_SDK_ROOT/cmdline-tools" && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O tools.zip && \
    unzip -q tools.zip && rm tools.zip && \
    mv cmdline-tools latest && \
    cd $APP_DIR

# Make sdkmanager available at the legacy path, satisfying python-for-android
RUN mkdir -p ${ANDROID_SDK_ROOT}/tools/bin && \
    ln -sf ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager ${ANDROID_SDK_ROOT}/tools/bin/sdkmanager

# Add SDK tools to PATH
ENV PATH="${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin:${ANDROID_SDK_ROOT}/platform-tools:${PATH}"

# Accept Android SDK licenses (essential for automated builds)
RUN yes | ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager --sdk_root=${ANDROID_SDK_ROOT} --licenses || true

# Install platform-tools and build-tools for both API 30 and 33
RUN yes | $ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_SDK_ROOT \
    "platform-tools" \
    "platforms;android-30" \
    "platforms;android-33" \
    "build-tools;30.0.3" \
    "build-tools;33.0.2" && \
    ls -la $ANDROID_SDK_ROOT/build-tools

# Create symbolic links to ensure build-tools are found in both paths
RUN mkdir -p $GLOBAL_ANDROID_SDK_ROOT && \
    ln -sf ${ANDROID_SDK_ROOT}/build-tools $GLOBAL_ANDROID_SDK_ROOT/build-tools && \
    ln -sf ${ANDROID_SDK_ROOT}/platforms $GLOBAL_ANDROID_SDK_ROOT/platforms

# Download and extract Android NDK
RUN wget -q https://dl.google.com/android/repository/android-ndk-r25b-linux.zip -O /tmp/ndk.zip && \
    unzip -q /tmp/ndk.zip -d /opt && \
    mv /opt/android-ndk-r25b ${ANDROID_NDK_HOME} && \
    rm /tmp/ndk.zip

## 1) Create a non-root user
RUN useradd -m builduser

# Add builduser to sudoers with passwordless sudo (MOVE THIS HERE)
RUN apt-get update && apt-get install -y sudo && \
    echo "builduser ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/builduser && \
    chmod 0440 /etc/sudoers.d/builduser

## 2) Copy app files & pre-create logs (as root)
WORKDIR ${APP_DIR}
COPY . ${APP_DIR}

## 3) Create necessary directories and set permissions
#   chown ensures the non-root user actually owns the files and directories.
RUN mkdir -p ${HOME}/.local \
    && mkdir -p ${HOME}/.android \
    && mkdir -p ${APP_DIR}/.buildozer/cache \
    && mkdir -p ${APP_DIR}/logs \
    && chown -R builduser:builduser ${HOME} \
    && chown -R builduser:builduser ${APP_DIR}/.buildozer \
    && chown -R builduser:builduser ${APP_DIR}/logs \
    && chown -R builduser:builduser ${APP_DIR} # Ensure builduser owns the app directory content copied as root

## 4) Switch to the non-root user for the rest
USER builduser
WORKDIR ${APP_DIR}

ENV PATH="${HOME}/.local/bin:${PATH}"

# Install dependencies in requirements
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# Create logs directory (buildozer needs this)
RUN mkdir -p logs
