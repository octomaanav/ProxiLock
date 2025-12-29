#!/bin/bash
# Build script for Proxi-Lock macOS app

echo "Building Proxi-Lock.app..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build the app
echo "Building app bundle"
python3 setup.py py2app

# Check if build was successful
if [ -d "dist/Proxi-Lock.app" ]; then
    echo "Build successful!"
    echo "App location: $(pwd)/dist/Proxi-Lock.app"
else
    echo "Build failed. Check the output above for errors."
    exit 1
fi

