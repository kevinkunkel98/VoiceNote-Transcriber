# VoiceNote Transcriber

Transform your voice notes into beautifully structured markdown documents using AI.

## Features

- **Audio Transcription**: Upload audio files and get accurate transcriptions using OpenAI's Whisper model
- **AI-Powered Structuring**: Automatically organize transcriptions into well-formatted markdown with titles, headings, and bullet points using Ollama
- **Beautiful UI**: Modern, responsive React interface with drag-and-drop support
- **Multiple Formats**: Supports MP3, WAV, M4A, OGG, FLAC, and AAC audio files
- **Download**: Export your structured notes as markdown files
- **Dockerized**: Everything runs in Docker containers - single command to start

## Architecture

- **Frontend**: React 18 + Vite with a beautiful gradient UI
- **Backend**: FastAPI with OpenAI Whisper for transcription
- **AI Structuring**: Ollama with Llama 3.2 for intelligent text formatting
- **Deployment**: Docker Compose for easy orchestration

## Prerequisites

- Docker Desktop installed and running
- At least 8GB of RAM available for Docker
- 10GB of free disk space (for models and images)

## Quick Start

1. **Clone or navigate to the repository**:
   ```bash
   cd VoiceNote-Transcriber
   ```

2. **Start the application**:
   ```bash
   docker-compose up -d
   ```

   This single command will:
   - Pull and start Ollama
   - Download the Llama 3.2 model
   - Build and start the FastAPI backend with Whisper
   - Build and start the React frontend
   - Set up all networking between services

3. **Wait for initialization** (first time only):
   - The Llama 3.2 model download takes 5-10 minutes
   - Monitor progress with: `docker-compose logs -f ollama-init`
   - Backend initialization takes 2-3 minutes (downloads Whisper model)

4. **Access the application**:
   - Open your browser to: http://localhost:3000
   - The API is available at: http://localhost:8000
   - API docs: http://localhost:8000/docs

## Usage

1. **Upload Audio**:
   - Drag and drop an audio file onto the upload area, or
   - Click to browse and select an audio file
   - Supported formats: MP3, WAV, M4A, OGG, FLAC, AAC

2. **Wait for Processing**:
   - Whisper transcribes your audio (usually takes 10-30 seconds per minute of audio)
   - Ollama structures the transcription into markdown (5-15 seconds)
   - Progress is shown with a loading indicator

3. **View Results**:
   - See your beautifully formatted markdown document
   - Expand "View Raw Transcription" to see the original text
   - Click "Download Markdown" to save the file
   - Click "New Transcription" to process another file

## Project Structure

```
VoiceNote-Transcriber/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile          # Backend container
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── App.css         # Styling
│   │   ├── main.jsx        # Entry point
│   │   └── index.css       # Global styles
│   ├── index.html          # HTML template
│   ├── package.json        # Node dependencies
│   ├── vite.config.js      # Vite configuration
│   ├── nginx.conf          # Nginx configuration
│   └── Dockerfile          # Frontend container
├── docker-compose.yml      # Orchestration
└── README.md              # This file
```

## API Endpoints

### `GET /`
Health check endpoint
```bash
curl http://localhost:8000/
```

### `GET /health`
Detailed health check with service status
```bash
curl http://localhost:8000/health
```

### `POST /transcribe`
Transcribe and structure an audio file
```bash
curl -X POST http://localhost:8000/transcribe \
  -F "file=@your-audio.mp3"
```

Response:
```json
{
  "success": true,
  "filename": "your-audio.mp3",
  "transcription": "Raw transcription text...",
  "title": "Meeting Notes - Project Update",
  "markdown": "# Meeting Notes - Project Update\n\n## Key Points..."
}
```

## Configuration

### Environment Variables

Backend (`docker-compose.yml`):
- `OLLAMA_URL`: URL to Ollama service (default: `http://ollama:11434`)

### Resource Limits

The backend container is configured with:
- 4 CPU cores
- 4GB RAM

Adjust in `docker-compose.yml` if needed:
```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 4G
```

### Whisper Model

The backend uses the `base` Whisper model by default (balanced speed/accuracy).

To change models, edit `backend/main.py`:
```python
model = whisper.load_model("medium")  # Options: tiny, base, small, medium, large
```

Model comparison:
- `tiny`: Fastest, least accurate (~1GB RAM)
- `base`: Good balance (default, ~1GB RAM)
- `small`: Better accuracy (~2GB RAM)
- `medium`: High accuracy (~5GB RAM)
- `large`: Best accuracy (~10GB RAM)

## Troubleshooting

### Services not starting

Check service status:
```bash
docker-compose ps
```

View logs:
```bash
docker-compose logs -f
```

### Ollama model not downloading

Check Ollama init logs:
```bash
docker-compose logs ollama-init
```

Manually pull the model:
```bash
docker-compose exec ollama ollama pull llama3.2
```

### Backend fails to start

Ensure you have enough RAM (at least 4GB for backend + 2GB for Ollama):
```bash
docker stats
```

### Transcription fails

1. Check file format is supported
2. Ensure file is not corrupted
3. Check backend logs: `docker-compose logs backend`
4. Verify Ollama is healthy: `curl http://localhost:11434/api/tags`

### Frontend can't connect to backend

1. Check backend health: `curl http://localhost:8000/health`
2. Verify all services are running: `docker-compose ps`
3. Check frontend logs: `docker-compose logs frontend`

## Development

### Running locally without Docker

**Backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
export OLLAMA_URL=http://localhost:11434
python main.py
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

**Ollama**:
Install from https://ollama.ai and run:
```bash
ollama serve
ollama pull llama3.2
```

### Building images manually

```bash
# Backend
docker build -t voicenote-backend ./backend

# Frontend
docker build -t voicenote-frontend ./frontend
```

## Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (including downloaded models)
docker-compose down -v
```

## Performance Tips

1. **Use smaller audio files**: Break long recordings into chunks for faster processing
2. **Compress audio**: MP3 or M4A files upload faster than WAV
3. **Adjust Whisper model**: Use `tiny` or `small` for faster transcription
4. **Increase resources**: Allocate more CPU/RAM to Docker if available

## License

This project uses:
- [OpenAI Whisper](https://github.com/openai/whisper) (MIT License)
- [Ollama](https://ollama.ai) (MIT License)
- [FastAPI](https://fastapi.tiangolo.com) (MIT License)
- [React](https://react.dev) (MIT License)

## Contributing

Feel free to open issues or submit pull requests for improvements!

## Acknowledgments

- OpenAI for the amazing Whisper model
- Ollama team for making LLMs accessible
- FastAPI and React communities
