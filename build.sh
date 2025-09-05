#!/bin/bash
# Build script for Render deployment

echo "🚀 Starting build process..."

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Verify scikit-learn installation
echo "🔍 Verifying scikit-learn installation..."
python -c "import sklearn; print(f'scikit-learn version: {sklearn.__version__}')"

echo "✅ Build completed successfully!"
