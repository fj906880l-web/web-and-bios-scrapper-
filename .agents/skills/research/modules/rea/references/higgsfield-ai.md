# Higgsfield AI Reverse-Engineering Dossier

**Target**: Higgsfield AI Foundation Video Generation Platform (`api.higgsfield.ai` / `open.higgsfield.ai`)  
**Method**: REA Protocol (Network & OpenAPI Protocol Reconstruction)  
**Standard**: EGE-2 Quantum Epistemic Level 1 (Direct Telemetry & Contract Verification)

---

## 1. Executive Summary & Architectural Overview

Higgsfield AI is a high-fidelity cinematic video generation service known for its proprietary **Soul Cinema** foundational model family (v1, v2), **DoP (Director of Photography)** steering controls, and **Soul ID** character consistency engines.

Unlike synchronous image-generation APIs, Higgsfield's backend architecture is an **asynchronous job queue pipeline** with distributed worker nodes running diffusion transformer backends.

---

## 2. API Contract & Routing Specifications

### 2.1 Host & Authentication
* **Base URL**: `https://api.higgsfield.ai` *(Note: OpenAPI endpoints do not use a `/v1` prefix)*
* **Authentication Header**:
  ```http
  Authorization: Key <HF_API_KEY>
  Content-Type: application/json
  ```
  *Alternative dual-header auth (for custom enterprise integrations):*
  ```http
  hf-api-key: <HF_API_KEY>
  hf-secret: <HF_SECRET>
  ```
* **Idempotency**: Supports `Idempotency-Key: <UUID>` on mutation requests for safe automated retries.

### 2.2 Endpoint Dispatch Matrix
Higgsfield routes generation jobs dynamically via model-family and task-type path segments:

| Path | Method | Purpose | Key Inputs |
| :--- | :--- | :--- | :--- |
| `/{provider}/{model}/{version}/{task}` | `POST` | Job Dispatch | `prompt`, `aspect_ratio`, `duration`, `motion_intensity` |
| `/higgsfield/soul-cinema-v2/text-to-video` | `POST` | Primary Cinematic T2V | Text prompt, camera motion, negative prompt |
| `/higgsfield/genjutsu/motion-transfer/v1.0` | `POST` | Motion/Pose Transfer | Source video, target character reference |
| `/requests/{request_id}/status` | `GET` | Asynchronous Status | `request_id` URL parameter |
| `/v1/custom-references` | `POST` | Soul ID Character Registration | Multi-angle reference portrait URLs |
| `/v1/custom-references/{reference_id}` | `GET` | Soul ID Reference Status | `reference_id` |

---

## 3. Payload Schemas & Telemetry

### 3.1 Text-to-Video Job Submission (`POST`)
```json
{
  "prompt": "string (512 to 10,000 characters)",
  "negative_prompt": "string",
  "aspect_ratio": "9:16 | 16:9 | 1:1",
  "duration": 5,
  "fps": 24,
  "motion_intensity": 65,
  "guidance_scale": 7.5,
  "sound": "off"
}
```

### 3.2 Submission Response Schema
```json
{
  "request_id": "d7e6c0f3-6699-4f6c-9a11-b0e2569e5d41",
  "status": "queued",
  "created_at": "2026-10-13T21:18:00Z"
}
```

### 3.3 Polling Telemetry (`GET /requests/{request_id}/status`)
```json
{
  "request_id": "d7e6c0f3-6699-4f6c-9a11-b0e2569e5d41",
  "status": "completed",
  "progress": 100,
  "video": {
    "url": "https://api.higgsfield.ai/outputs/d7e6c0f3_output.mp4",
    "width": 1080,
    "height": 1920,
    "duration": 5.0
  },
  "error": null
}
```

State transitions follow the deterministic state machine:  
`queued` $\longrightarrow$ `processing` $\longrightarrow$ `completed` | `failed`.

---

## 4. Reverse-Engineered Discrepancies in Legacy Code

An audit of the previous codebase ([higgsfield_adapter.py](file:///Users/malcolm/trading-bot-/scripts/generative_media_studio/higgsfield_adapter.py)) revealed 4 structural discrepancies against the live API:

1. **Path Prefix**: Legacy used `https://api.higgsfield.ai/v1/video/generate`. The actual API routes to model paths directly (`/higgsfield/soul-cinema-v2/text-to-video`).
2. **Auth Token Header**: Legacy passed `Authorization: Bearer <token>`. Higgsfield requires `Authorization: Key <token>`.
3. **Response Key Mismatch**: Legacy expected `id` or `job_id`. Live API returns `request_id`.
4. **Omitted Lifecycle**: Legacy lacked status polling on `/requests/{request_id}/status`.

---

## 5. REA Reconstruction Directives

1. Update `HiggsfieldAIClient` to support `Key <token>` auth with automatic fallback.
2. Route text-to-video jobs through `/higgsfield/soul-cinema-v2/text-to-video`.
3. Map `request_id` to `job_id` aliasing to maintain 100% backward compatibility for existing callers.
4. Implement `check_job_status(request_id)` and `poll_video_completion(request_id, timeout_sec=120)`.
5. Retain local deterministic fallback (PIL + FFmpeg) when running offline or without credentials.
