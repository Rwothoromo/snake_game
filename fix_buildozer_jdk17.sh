#!/bin/bash

set -e

# Get the original user's home directory
ORIGINAL_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
if [ -z "$ORIGINAL_HOME" ]; then
    ORIGINAL_HOME="$HOME"
fi

# Step 1: Create lib dir and download JAXB jars if not already there
LIB_DIR="$ORIGINAL_HOME/.buildozer/jaxb-libs"
mkdir -p "$LIB_DIR"

download_if_missing() {
    local url="$1"
    local file="$2"
    if [ ! -f "$LIB_DIR/$file" ]; then
        echo "Downloading $file..."
        curl -L -o "$LIB_DIR/$file" "$url"
    fi
}

echo "Ensuring JAXB jars are in $LIB_DIR..."
download_if_missing "https://repo1.maven.org/maven2/jakarta/xml/bind/jakarta.xml.bind-api/2.3.3/jakarta.xml.bind-api-2.3.3.jar" "jakarta.xml.bind-api-2.3.3.jar"
download_if_missing "https://repo1.maven.org/maven2/org/glassfish/jaxb/jaxb-runtime/2.3.3/jaxb-runtime-2.3.3.jar" "jaxb-runtime-2.3.3.jar"
download_if_missing "https://repo1.maven.org/maven2/com/sun/activation/javax.activation/1.2.0/javax.activation-1.2.0.jar" "javax.activation-1.2.0.jar"
# download_if_missing "https://mvnrepository.com/artifact/jakarta.xml.bind/jakarta.xml.bind-api/2.3.3"
# download_if_missing "https://mvnrepository.com/artifact/org.glassfish.jaxb/jaxb-runtime/2.3.3"
# download_if_missing "https://mvnrepository.com/artifact/jakarta.activation/jakarta.activation-api/1.2.2"
# download_if_missing "https://mvnrepository.com/artifact/com.sun.xml.bind/jaxb-core/2.3.0"

# Step 2: Find sdkmanager
echo "Searching for sdkmanager..."
SDKMANAGER_PATH="$ORIGINAL_HOME/.buildozer/android/platform/android-sdk/tools/bin/sdkmanager"

if [ -z "$SDKMANAGER_PATH" ]; then
    echo "❌ sdkmanager not found at $SDKMANAGER_PATH. Make sure you've run 'buildozer android' at least once."
    exit 1
fi

echo "Found sdkmanager at: $SDKMANAGER_PATH"

# Step 3: Back up original sdkmanager
if [ ! -f "$SDKMANAGER_PATH.original" ]; then
    echo "Backing up original sdkmanager..."
    cp "$SDKMANAGER_PATH" "$SDKMANAGER_PATH.original"
fi

# Step 4: Replace with wrapper script
echo "Injecting JAXB wrapper..."

chmod +x "$SDKMANAGER_PATH"  # Ensure execute permissions

cat > "$SDKMANAGER_PATH" <<EOF
#!/bin/bash
JAXB_JARS="$LIB_DIR/*"
exec java -cp "\$JAXB_JARS:\$CLASSPATH" -Dcom.android.sdklib.toolsdir="\$(dirname "\$0")" com.android.sdklib.tool.sdkmanager.SdkManagerCli "\$@"
EOF

chmod +x "$SDKMANAGER_PATH"

echo "✅ JAXB wrapper injected. You can now build with JDK 17!"
