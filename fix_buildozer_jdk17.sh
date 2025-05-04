#!/bin/bash

set -e

# Get the user's home directory
HOME=$(pwd)
echo "HOME: $HOME"

# Step 1: Create lib dir and download JAXB jars if not already there
LIB_DIR="$HOME/.buildozer/jaxb-libs"
if [ -d "$LIB_DIR" ]; then
    echo "✅ $LIB_DIR already exists. Skipping creation."
else
    echo "Creating $LIB_DIR..."
    mkdir -p "$LIB_DIR"
fi

download_if_missing() {
    local url="$1"
    local file="$2"
    if [ ! -f "$LIB_DIR/$file" ]; then
        echo "Downloading $file... into $LIB_DIR"
        curl -L -o "$LIB_DIR/$file" "$url" || { echo "❌ Failed to download $file from $url"; exit 1; }
    else
        echo "✅ $file already exists in $LIB_DIR. Skipping download."
    fi
}

echo "Ensuring JAXB jars are in $LIB_DIR..."
download_if_missing "https://repo1.maven.org/maven2/jakarta/xml/bind/jakarta.xml.bind-api/2.3.3/jakarta.xml.bind-api-2.3.3.jar" "jakarta.xml.bind-api-2.3.3.jar"
download_if_missing "https://repo1.maven.org/maven2/org/glassfish/jaxb/jaxb-runtime/2.3.3/jaxb-runtime-2.3.3.jar" "jaxb-runtime-2.3.3.jar"
download_if_missing "https://repo1.maven.org/maven2/com/sun/activation/javax.activation/1.2.0/javax.activation-1.2.0.jar" "javax.activation-1.2.0.jar"
download_if_missing "https://repo1.maven.org/maven2/jakarta/xml/bind/jakarta.xml.bind-api/2.3.3/jakarta.xml.bind-api-2.3.3.jar" "jakarta.xml.bind-api-2.3.3.jar"
download_if_missing "https://repo1.maven.org/maven2/org/glassfish/jaxb/jaxb-runtime/2.3.3/jaxb-runtime-2.3.3.jar" "jaxb-runtime-2.3.3.jar"
download_if_missing "https://repo1.maven.org/maven2/jakarta/activation/jakarta.activation-api/1.2.2/jakarta.activation-api-1.2.2.jar" "jakarta.activation-api-1.2.2.jar"
download_if_missing "https://repo1.maven.org/maven2/com/sun/xml/bind/jaxb-core/2.3.0/jaxb-core-2.3.0.jar" "jaxb-core-2.3.0.jar"

# Step 2: Find sdkmanager
echo "Searching for sdkmanager..."
SDKMANAGER_PATH="$HOME/.buildozer/android/platform/android-sdk/cmdline-tools/latest/bin/sdkmanager"

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
