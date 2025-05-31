#!/bin/bash
# Comprehensive Python 2 to 3 compatibility fixes for 'long' type

echo "Patching Python 2 'long' type references to make compatible with Python 3..."

# Fix pyjnius files
echo "1/6 Fix pyjnius files"
find ${APP_DIR}/.buildozer -path "*/pyjnius*" -name "*.pyx" -o -name "*.pxi" | xargs -I{} sed -i 's/isinstance(\([^,]*\), *(int, *long))/isinstance(\1, int)/g' {}
find ${APP_DIR}/.buildozer -path "*/pyjnius*" -name "*.pyx" -o -name "*.pxi" | xargs -I{} sed -i 's/isinstance(obj, (int, long))/isinstance(obj, int)/g' {}
find ${APP_DIR}/.buildozer -path "*/pyjnius*" -name "*.pyx" -o -name "*.pxi" | xargs -I{} sed -i 's/isinstance(arg, long)/isinstance(arg, int)/g' {}

# Fix kivy files
echo "2/6 Fix kivy files"
find ${APP_DIR}/.buildozer -path "*/kivy*" -name "*.pyx" -o -name "*.pxi" | xargs -I{} sed -i 's/isinstance(indices, (long, int))/isinstance(indices, int)/g' {}
find ${APP_DIR}/.buildozer -path "*/kivy*" -name "*.pyx" -o -name "*.pxi" | xargs -I{} sed -i 's/isinstance(data, (long, int))/isinstance(data, int)/g' {}
find ${APP_DIR}/.buildozer -path "*/kivy*" -name "*.pyx" -o -name "*.pxi" | xargs -I{} sed -i 's/isinstance(\([^,]*\), *(long, *int))/isinstance(\1, int)/g' {}
find ${APP_DIR}/.buildozer -path "*/kivy*" -name "*.pyx" -o -name "*.pxi" | xargs -I{} sed -i 's/isinstance(\([^,]*\), *(int, *long))/isinstance(\1, int)/g' {}

# Replace long() function calls
echo "3/6 Replace long() function calls"
find ${APP_DIR}/.buildozer -name "*.py" -o -name "*.pyx" -o -name "*.pxi" | xargs -I{} sed -i 's/long(/int(/g' {}

# Fix weakproxy.pyx __long__ method
echo "4/6 Fix weakproxy.pyx __long__ method"
find ${APP_DIR}/.buildozer -path "*/kivy*" -name "weakproxy.pyx" | xargs -I{} sed -i 's/def __long__(self):/def __index__(self):/g' {}
find ${APP_DIR}/.buildozer -path "*/kivy*" -name "weakproxy.pyx" | xargs -I{} sed -i 's/return long(self.__ref__())/return int(self.__ref__())/g' {}

# Fix the libffi LT_SYS_SYMBOL_USCORE issue
echo "5/6 Fix the libffi LT_SYS_SYMBOL_USCORE issue"
find ${APP_DIR}/.buildozer -name "configure.ac" -path "*libffi*" -exec sed -i '1s/^/m4_pattern_allow([LT_SYS_SYMBOL_USCORE])\n/' {} \;

# Create m4 directory where needed
echo "6/6 Create m4 directory where needed ...wait"
find ${APP_DIR}/.buildozer -path "*libffi*" -type d ! -name m4 | while read dir; do
    echo "Creating $dir/m4"
    mkdir -p "$dir/m4" 2>/dev/null || true
done

echo "Patching complete!"
