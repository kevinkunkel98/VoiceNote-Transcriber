#!/bin/bash

echo "========================================"
echo "  VoiceNote Transcriber - Quick Start"
echo "========================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "Starting VoiceNote Transcriber..."
echo ""

# Start services
docker-compose up -d

echo ""
echo "Services starting..."
echo ""
echo "This may take a few minutes on first run:"
echo "  1. Downloading Ollama and Llama 3.2 model (~5-10 min)"
echo "  2. Building backend with Whisper (~2-3 min)"
echo "  3. Building frontend (~1-2 min)"
echo ""
echo "Monitor progress with:"
echo "  docker-compose logs -f"
echo ""
echo "Once ready, access the app at:"
echo "  Frontend: http://localhost:3000"
echo "  API:      http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "To stop the application:"
echo "  docker-compose down"
echo ""
