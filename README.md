# 🎙️ VoiceMemo AI

A full-stack voice memo transcription app. Upload an audio file, and a local
[Whisper](https://github.com/openai/whisper) model transcribes it in the
background — no external API calls, no API keys.

## Stack

- **Backend**: FastAPI, SQLAlchemy (async, SQLite), JWT auth (PyJWT + passlib)
- **Transcription**: `openai-whisper` running locally (CPU/GPU)
- **Frontend**: Streamlit

## Features

- User registration & login (OAuth2 password flow + JWT)
- Async audio upload, processed via FastAPI `BackgroundTasks`
- Local Whisper transcription with optional language selection (auto / English / Arabic)
- Per-user history with live status (`processing` / `completed` / `failed`)
- Admin panel: view all users and all memos system-wide
- Auto-seeded admin account on first run

## Project Structure

```
backend/
  app/
    main.py          # FastAPI app, middleware, lifespan (DB init + admin seed)
    config.py         # Settings (.env)
    database.py        # Async SQLAlchemy engine/session
    auth/              # Register, login, JWT, current-user dependencies
    memos/             # Upload, history, Whisper background task
    admin/             # Admin-only endpoints
  storage/             # Uploaded audio files (gitignored)
  database.db          # SQLite DB (gitignored)

frontend/
  app.py               # Entry point, sidebar nav, session handling
  session.py           # JWT persistence via encrypted cookie
  components/          # Auth forms, upload/history UI
  pages/admin.py        # Admin dashboard
```

## Setup

### Prerequisites

- Python 3.11+
- [ffmpeg](https://ffmpeg.org/download.html) installed and on your `PATH` (required by Whisper)

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env            # then edit secrets
uvicorn app.main:app --reload
```

`.env` variables:

| Variable             | Description                              |
| -------------------- | ----------------------------------------- |
| `JWT_SECRET`          | Secret key for signing JWTs                |
| `JWT_ALGORITHM`       | Default: `HS256`                           |
| `JWT_EXPIRE_MINUTES`  | Token lifetime, default `60`               |
| `DATABASE_URL`        | Default: `sqlite+aiosqlite:///./database.db` |
| `ADMIN_EMAIL`         | Auto-seeded admin account email            |
| `ADMIN_USERNAME`      | Auto-seeded admin username                 |
| `ADMIN_PASSWORD`      | Auto-seeded admin password                 |
| `STORAGE_DIR`         | Where uploaded audio is saved              |

### Frontend

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

Backend runs on `http://localhost:8000`, frontend on `http://localhost:8501`.

## API Overview

| Method | Endpoint          | Description                       |
| ------ | ----------------- | ---------------------------------- |
| POST   | `/auth/register`   | Create a new user                  |
| POST   | `/auth/token`      | Log in, returns JWT                |
| GET    | `/auth/me`         | Current user profile               |
| POST   | `/memos/upload`    | Upload audio, queues transcription |
| GET    | `/memos/history`   | Current user's memos               |
| GET    | `/admin/users`     | All users (admin only)             |
| GET    | `/admin/memos`     | All memos (admin only)             |

Interactive docs available at `http://localhost:8000/docs`.

## Notes

- The local Whisper model (`base`) loads on first transcription request and is cached in memory afterward.
- The first transcription will be slower as the model weights are downloaded.
