#!/bin/bash
# CV Tailor Setup Script
# This script helps you set up the CV Tailor application

echo "🚀 CV Tailor Setup Script"
echo "=========================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama is not installed."
    echo "Please install Ollama from: https://ollama.ai"
    echo ""
    read -p "Do you want to continue without Ollama? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Ollama found: $(ollama --version)"
    echo ""

    # Check if Ollama is running
    if curl -s http://localhost:11434 > /dev/null 2>&1; then
        echo "✅ Ollama is running"
    else
        echo "⚠️  Ollama is not running. Starting Ollama..."
        ollama serve &
        sleep 3
    fi

    # Check for models
    echo ""
    echo "📦 Checking for LLM models..."
    if ollama list | grep -q "llama3"; then
        echo "✅ llama3 model found"
    else
        echo "⚠️  llama3 model not found"
        read -p "Do you want to download llama3? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "⬇️  Downloading llama3 (this may take a while)..."
            ollama pull llama3
        fi
    fi
fi

echo ""
echo "📦 Setting up Python environment..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎉 You can now run the application with:"
echo "   streamlit run app.py"
echo ""
