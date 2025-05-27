FROM python:3.11-slim-bookworm

# Set environment variables for SDK/NDK if you're managing them manually
# Otherwise, Buildozer will download them to ~/.buildozer/android/platform/
ENV HOME=/home/builduser
ENV ANDROID_SDK_ROOT=${HOME}/.buildozer/android/platform/android-sdk
ENV ANDROID_NDK_HOME=${HOME}/.buildozer/android/platform/android-ndk-r25b

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
RUN mkdir -p ${ANDROID_SDK_ROOT}/cmdline-tools/latest && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip -O /tmp/cmdline-tools.zip && \
    unzip -q /tmp/cmdline-tools.zip -d /tmp/cmdline-tools && \
    mv /tmp/cmdline-tools/cmdline-tools/* ${ANDROID_SDK_ROOT}/cmdline-tools/latest/ && \
    rm /tmp/cmdline-tools.zip

# Make sdkmanager available at the legacy path, satisfying python-for-android
RUN mkdir -p ${ANDROID_SDK_ROOT}/tools/bin && \
    ln -s ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager ${ANDROID_SDK_ROOT}/tools/bin/sdkmanager

# Add SDK tools to PATH
ENV PATH="${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin:${ANDROID_SDK_ROOT}/platform-tools:${PATH}"

# Accept Android SDK licenses (essential for automated builds)
RUN yes | ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager --sdk_root=${ANDROID_SDK_ROOT} --licenses || true

# Install Android API 33 (and potentially other necessary platforms/build-tools)
RUN ${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin/sdkmanager --sdk_root=${ANDROID_SDK_ROOT} "platforms;android-33" "build-tools;33.0.2" "platform-tools"

# Download and extract Android NDK
RUN wget -q https://dl.google.com/android/repository/android-ndk-r25b-linux.zip -O /tmp/ndk.zip && \
    unzip -q /tmp/ndk.zip -d /opt && \
    mv /opt/android-ndk-r25b ${ANDROID_NDK_HOME} && \
    rm /tmp/ndk.zip

## 1) Create a non-root user
RUN useradd -m builduser

## 2) Copy app files & pre-create logs (as root)
WORKDIR ${HOME}/app
COPY . ${HOME}/app
RUN mkdir -p logs \
 && chown -R builduser:builduser ${HOME}/app

## 3) Switch to the non-root user for the rest
USER builduser
WORKDIR ${HOME}/app

RUN mkdir -p ${HOME}/.local && chown -R builduser:builduser ${HOME}/.local

# install requirements…
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# bring in your patch
COPY --chown=builduser:builduser patch_py2to3.sh .

# initial build / patch / rebuild
RUN chmod +x patch_py2to3.sh \
 && buildozer android debug || true \
 && ./patch_py2to3.sh \
 && buildozer -v android debug --log‐level 2 --debug 2>&1 \
      | tee logs/buildozer.log