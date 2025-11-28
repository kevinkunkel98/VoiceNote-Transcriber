from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel
import os
import tempfile
import requests
import json
from pathlib import Path

app = FastAPI(title="VoiceNote Transcriber")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Whisper model on startup (using faster-whisper for better ARM support)
print("Loading Faster-Whisper model...")
model = WhisperModel("base", device="cpu", compute_type="int8")
print("Faster-Whisper model loaded successfully!")

# Ollama configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file using Faster-Whisper"""
    try:
        segments, info = model.transcribe(audio_path, beam_size=5)
        transcription = " ".join([segment.text for segment in segments])
        return transcription
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


def structure_with_ollama(transcription: str) -> dict:
    """Use Ollama to structure the transcription into markdown"""
    prompt = f"""You are a helpful assistant that converts voice note transcriptions into well-structured markdown documents.

Given the following transcription, please:
1. Create a clear, descriptive title for the content
2. Structure the content into a well-formatted markdown document with appropriate headings, bullet points, and sections
3. Fix any grammar or punctuation issues
4. Make it readable and professional

Transcription:
{transcription}

Please respond with a JSON object containing:
- "title": A concise, descriptive title (without markdown formatting)
- "content": The full formatted markdown content (including the title as # heading)

Example response format:
{{
  "title": "Meeting Notes - Project Update",
  "content": "# Meeting Notes - Project Update\\n\\n## Key Points\\n\\n- Point 1\\n- Point 2\\n\\n## Action Items\\n\\n1. Task 1\\n2. Task 2"
}}
"""

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": "qwen2.5:7b",
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=120
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Ollama request failed: {response.text}"
            )

        result = response.json()
        response_text = result.get("response", "")

        # Parse the JSON response from Ollama
        try:
            structured_data = json.loads(response_text)
            return {
                "title": structured_data.get("title", "Voice Note"),
                "content": structured_data.get("content", transcription)
            }
        except json.JSONDecodeError:
            # If Ollama doesn't return valid JSON, use the response as content
            return {
                "title": "Voice Note Transcription",
                "content": f"# Voice Note Transcription\n\n{response_text}"
            }

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Ollama service unavailable: {str(e)}"
        )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "VoiceNote Transcriber API"}


@app.get("/health")
async def health_check():
    """Detailed health check"""
    ollama_status = "unknown"
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        ollama_status = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        ollama_status = "unavailable"

    return {
        "api": "healthy",
        "whisper": "loaded",
        "ollama": ollama_status
    }


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """
    Transcribe an audio file and structure it into markdown

    Accepts: audio files (mp3, wav, m4a, etc.)
    Returns: JSON with title and markdown content
    """
    # Validate file type
    allowed_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac']
    file_ext = Path(file.filename).suffix.lower()

    print(f"Received file: {file.filename}, extension: {file_ext}")

    if file_ext not in allowed_extensions:
        print(f"File rejected: extension '{file_ext}' not in {allowed_extensions}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file_ext}'. Allowed: {', '.join(allowed_extensions)}"
        )

    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        try:
            # Save uploaded file
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            temp_path = temp_file.name

            # Step 1: Transcribe with Whisper
            print(f"Transcribing {file.filename}...")
            transcription = transcribe_audio(temp_path)
            print(f"Transcription complete: {len(transcription)} characters")

            # Step 2: Structure with Ollama
            print("Structuring with Ollama...")
            structured = structure_with_ollama(transcription)
            print(f"Structured markdown created: {structured['title']}")

            return JSONResponse(content={
                "success": True,
                "filename": file.filename,
                "transcription": transcription,
                "title": structured["title"],
                "markdown": structured["content"]
            })

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        finally:
            # Cleanup temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
