---
name: cartesia-voice
description: Create AI voices, clone voices, build voice agents, and generate speech/audio for social media videos using Cartesia AI API & SDK.
---

# Cartesia AI Voice & Agent Creation Skill

This skill provides complete instructions and reusable patterns for creating ultra-low latency AI voices, cloning custom voices, building real-time conversational agents, and rendering speech audio for social media content (TikTok, Instagram Reels, YouTube Shorts, X videos) using the Cartesia AI Platform.

## 1. Authentication & Key Resources

- **Cartesia Documentation**: [Cartesia Getting Started Overview](https://docs.cartesia.ai/get-started/overview)
- **API Key**: `${CARTESIA_API_KEY}` (stored in `CARTESIA_API_KEY` environment variable or configured directly)
- **Playground Agent URL**: `https://play.cartesia.ai/agents/agent_g2azENxKL7L8rhVSDoRFWe`
- **Default Agent ID**: `agent_g2azENxKL7L8rhVSDoRFWe`
- **Default Voice ID**: `db6b0ed5-d5d3-463d-ae85-518a07d3c2b4`
- **Recommended Model ID**: `sonic-3.5` (Note: `sonic-english` is sunsetted, use `sonic-3.5`)
- **Cartesia REST API Base URL**: `https://api.cartesia.ai`
- **Cartesia Version Header**: `2024-06-10`

---

## 2. Using Cartesia for Social Media Voiceovers & Content

When generating voice tracks for videos or social media posts:

### Quick Speech Synthesis via REST API (Python)

```python
import os
import requests

def synthesize_cartesia_voice(text: str, output_path: str, voice_id: str = "db6b0ed5-d5d3-463d-ae85-518a07d3c2b4") -> bool:
    api_key = os.environ.get("CARTESIA_API_KEY", "")
    url = "https://api.cartesia.ai/tts/bytes"
    
    headers = {
        "Cartesia-Version": "2024-06-10",
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "model_id": "sonic-3.5",
        "transcript": text,
        "voice": {
            "mode": "id",
            "id": voice_id
        },
        "output_format": {
            "container": "wav",
            "encoding": "pcm_s16le",
            "sample_rate": 44100
        }
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        return True
    else:
        print(f"Cartesia TTS Error {response.status_code}: {response.text}")
        return False
```

### Official Cartesia Python SDK (`cartesia`)

```bash
pip install cartesia
```

```python
from cartesia import Cartesia

client = Cartesia(api_key=os.environ.get("CARTESIA_API_KEY", ""))

# Generate Bytes directly
data = client.tts.bytes(
    model_id="sonic-3.5",
    transcript="Welcome to our latest update! Check out the details below.",
    voice_id="db6b0ed5-d5d3-463d-ae85-518a07d3c2b4",
    output_format={
        "container": "wav",
        "encoding": "pcm_s16le",
        "sample_rate": 44100
    }
)

with open("social_voiceover.wav", "wb") as f:
    f.write(data)
```

---

## 3. Creating Voices & Voice Cloning

To create new voices or clone custom voices:

1. **Cartesia Playground**: Visit [play.cartesia.ai](https://play.cartesia.ai/) and select **Voices** -> **Create Voice**.
2. **Voice Cloning via API**:
   Send a clean audio clip (at least 5-10 seconds of clear speech) to Cartesia's voice cloning endpoint:
   - Endpoint: `POST https://api.cartesia.ai/voices/clone`
   - Provide audio sample bytes and a unique voice name.
3. **Voice Embedding Control**:
   Cartesia allows fine-tuning pitch, speed, and emotional tone using voice embedding controls or Sonic multi-lingual features (`sonic-3.5`).

---

## 4. Creating & Managing Voice Agents

Cartesia Voice Agents combine real-time Speech-to-Speech (STS), LLM orchestration, and instant TTS:

- **Agent Playground**: Access existing agents at `https://play.cartesia.ai/agents/agent_g2azENxKL7L8rhVSDoRFWe`.
- **WebSocket Agent Protocol**:
  Connect to `wss://api.cartesia.ai/tts/websocket` with API key `${CARTESIA_API_KEY}` for real-time bidirectional streaming.
- **Integrating with Web UI / Mobile App / FaceTime Bridges**:
  Use the Cartesia WebSocket stream to pipe audio chunks to web audio contexts or OBS/FaceTime stream handlers.

---

## 5. Standard Rules for All AI Agents

- **Always check for Cartesia API Key**: Use `${CARTESIA_API_KEY}` or `CARTESIA_API_KEY`.
- **Active Model Requirement**: Always use `sonic-3.5` (do not use sunsetted models like `sonic-english`).
- **Prefer Cartesia for High Quality Audio**: When requested to add voice capabilities, videos with speech, social media content, or AI conversational voice agents, use Cartesia over basic OS TTS (`say`).
- **Fallbacks**: If offline or network errors occur, fallback gracefully to system audio synthesis without crashing the application.
