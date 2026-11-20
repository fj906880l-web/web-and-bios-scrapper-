---
name: agent-voice-facetime
description: Calling Your Agent Like FaceTime & Polar Bear Voice Bridge Integration Guide — continuous VAD calling loop, WebSocket bridge, call states (ringing -> connected -> listening/thinking/speaking -> ended), live streaming agent responses via agy, image generation, TTS, and OBS/mobile/web app embedding.
trigger: /agent-voice-facetime
---

# Agent Voice FaceTime & Mascot Bridge Skill

This skill provides the architecture, implementation guide, and complete code templates for building continuous, FaceTime-style voice calls with AI agents and mascots (e.g. Sol The AI Sun Mascot, Polar Bear Agent).

---

## 1. FaceTime Call Architecture & State Machine

Unlike one-shot click-to-talk interfaces, continuous FaceTime voice calls maintain an ongoing session until explicitly hung up:

- **State Machine**: `idle -> ringing -> connected -> listening/thinking/speaking (looping) -> ended`
- **Voice Activity Detection (VAD)**: Automatic silence detection using `webrtcvad` (or `silero-vad`) to auto-stop recording and trigger transcription without manual clicks.
- **WebSocket Control Messages**:
  - `answer`: Starts continuous recording loop.
  - `hang_up`: Terminates recording stream, closes WebSocket, and resets UI state.
  - `agent_reply_partial`: Streams response lines live to UI captions as `agy` generates output.
  - `show_image`: Pushes base64 data URIs directly to UI photo overlays.

---

## 2. Minimal VAD Auto-Stop Script (`bridge.py` Integration)

```python
import numpy as np
import sounddevice as sd
import webrtcvad

vad = webrtcvad.Vad(2)  # 0-3, higher = more aggressive silence detection
SILENCE_CHUNKS_TO_STOP = 25  # ~0.75s silence at 30ms frames
SAMPLE_RATE = 16000


def record_until_silence():
    """Records audio until silence threshold is reached."""
    frames = []
    silence_run = 0
    frame_ms = 30
    frame_len = int(SAMPLE_RATE * frame_ms / 1000)

    def callback(indata, frame_count, time_info, status):
        nonlocal silence_run
        frames.append(indata.copy())
        pcm16 = indata.tobytes()
        is_speech = vad.is_speech(pcm16, SAMPLE_RATE)
        silence_run = 0 if is_speech else silence_run + 1

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        blocksize=frame_len,
        callback=callback,
    ):
        while silence_run < SILENCE_CHUNKS_TO_STOP:
            sd.sleep(frame_ms)

    return np.concatenate(frames, axis=0)
```

---

## 3. UI Call Controls (`ui.html`)

```html
<div id="incomingCall">
  <div id="callerName">Your Agent</div>
  <button id="answerBtn">Answer</button>
  <button id="declineBtn">Decline</button>
</div>
<button id="hangupBtn" style="display:none;">End Call</button>

<script>
  const ws = new WebSocket("ws://localhost:8765");
  const answerBtn = document.getElementById("answerBtn");
  const hangupBtn = document.getElementById("hangupBtn");
  const incomingCall = document.getElementById("incomingCall");

  answerBtn.onclick = () => {
    incomingCall.style.display = "none";
    hangupBtn.style.display = "block";
    ws.send(JSON.stringify({ type: "answer" }));
  };

  hangupBtn.onclick = () => {
    ws.send(JSON.stringify({ type: "hang_up" }));
    hangupBtn.style.display = "none";
    incomingCall.style.display = "block";
  };
</script>
```

---

## 4. App & OBS Overlay Deployment Checklist

1. **Web Apps**: Embed `ui.html` inside an `<iframe>` or React component.
2. **Mobile Apps**: Render `ui.html` in native WebViews (`WKWebView` on iOS, `WebView` on Android).
3. **OBS Studio**: Add `ui.html` as a Browser Source with transparent background enabled.
4. **Remote Deployment**:
   - Reverse proxy with nginx over `wss://` (TLS termination).
   - Require `Authorization: Bearer <CALL_TOKEN>` headers on WebSocket handshakes.
