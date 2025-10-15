#!/bin/bash

# Quick Start Script for AI Diwali Wish Maker with Ollama
# This script sets up and runs the app with Ollama support

set -e

echo "🪔 AI Diwali Wish Maker - Quick Start with Ollama 🪔"
echo "=================================================="
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if Ollama is running
check_ollama() {
    if curl -s http://localhost:11434/api/version >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Step 1: Check for Ollama
echo "📦 Step 1: Checking for Ollama..."
if ! command_exists ollama; then
    echo "❌ Ollama not found!"
    echo ""
    echo "Please install Ollama first:"
    echo "  macOS/Linux: curl https://ollama.ai/install.sh | sh"
    echo "  Or visit: https://ollama.ai/download"
    echo ""
    exit 1
fi
echo "✅ Ollama is installed"
echo ""

# Step 2: Start Ollama if not running
echo "🚀 Step 2: Checking Ollama server..."
if check_ollama; then
    echo "✅ Ollama is already running"
else
    echo "⚙️  Starting Ollama server..."
    ollama serve &
    OLLAMA_PID=$!
    echo "   Ollama started with PID: $OLLAMA_PID"
    
    # Wait for Ollama to be ready
    echo "   Waiting for Ollama to be ready..."
    for i in {1..30}; do
        if check_ollama; then
            echo "✅ Ollama is ready!"
            break
        fi
        sleep 1
        if [ $i -eq 30 ]; then
            echo "❌ Ollama failed to start in time"
            exit 1
        fi
    done
fi
echo ""

# Step 3: Check for model
echo "🤖 Step 3: Checking for llama3.2 model..."
if ollama list | grep -q "llama3.2"; then
    echo "✅ Model llama3.2 is available"
else
    echo "📥 Downloading llama3.2 model (this may take a few minutes)..."
    ollama pull llama3.2
    echo "✅ Model downloaded successfully!"
fi
echo ""

# Step 4: Check Python dependencies
echo "🐍 Step 4: Checking Python dependencies..."
if ! command_exists streamlit; then
    echo "❌ Streamlit not found!"
    echo ""
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed!"
else
    echo "✅ Python dependencies are installed"
fi
echo ""

# Step 5: Start the app
echo "🎉 Step 5: Starting the AI Diwali Wish Maker app..."
echo ""
echo "=================================================="
echo "🌟 Your app is starting..."
echo "📍 Local URL: http://localhost:8501"
echo ""
echo "💡 The app is configured to use:"
echo "   - Ollama Host: http://localhost:11434"
echo "   - Model: llama3.2"
echo ""
echo "⚙️  You can customize by setting environment variables:"
echo "   export OLLAMA_HOST=http://your-server:11434"
echo "   export OLLAMA_MODEL=llama3.1:8b"
echo "   export OPENAI_API_KEY=sk-... (optional fallback)"
echo ""
echo "Press Ctrl+C to stop the app"
echo "=================================================="
echo ""

# Start Streamlit
streamlit run app.py

