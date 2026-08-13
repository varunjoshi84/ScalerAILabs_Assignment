# Fireflies.ai Clone — SDE Fullstack Assignment

A functional clone of the **Fireflies.ai** meeting-assistant web application replicating its design, user experience, and core post-meeting workflows. Built with a Next.js (TypeScript) frontend and a Python FastAPI backend powered by an SQLite database.

---

## 🌟 Key Features

- **Meetings Library / Dashboard**:
  - Home dashboard with recency sorting (`date_desc`), participant & date range filtering, and search across titles and transcripts.
  - Collapsible Fireflies sidebar navigation with official emblem branding.

- **Meeting & Interactive Transcript Detail View**:
  - Interactive transcript with speaker avatars, labels, and timestamps.
  - **Bi-Directional Media Player Sync**: Clicking transcript lines seeks the media player; audio playback automatically highlights active segments and smooth auto-scrolls into view.
  - Variable speed playback controls (`1x`, `1.25x`, `1.5x`, `2x`) and quick `-5s / +5s` skip buttons.
  - Live transcript search with highlighted term matches.

- **AI Summaries & Task Checklist**:
  - AI Overview, key topics (`#SlowQueries`, `#TursoRedirects`), and task checklist with interactive completion toggles.
  - Summary Style Presets (**General Summary**, **Executive Brief**, **Technical Breakdown**, **Action-Item Centric**) and custom prompt AI refinement modal.

- **Meeting Management (CRUD)**:
  - Create meetings via file upload (`.txt`, `.vtt`, `.json`, `.mp4`), raw transcript text paste, or form metadata.
  - Edit title/participants and delete meetings with confirmation modals.

- **Global AskFred AI Assistant**:
  - Dedicated standalone AskFred workspace with scope switching (`# All Workspace Meetings`, `# My Meetings`, `Specific Notebook`), preset prompts, and clickable source citations.

- **Export & Highlights**:
  - Markdown transcript export (`GET /meetings/{id}/export/markdown`).
  - Highlight segments (`is_highlighted`) and add persistent comments (`comment`).

---

## 🛠️ Technical Stack

- **Frontend**: Next.js 16 (App Router), TypeScript, Vanilla CSS & Tailwind CSS, Lucide Icons.
- **Backend**: Python 3.12, FastAPI, SQLAlchemy ORM, Pydantic v2, Uvicorn.
- **Database**: SQLite (`backend/meetings.db`).

---

## 🚀 Setup & Run Instructions

### 1. Prerequisites
- Node.js v18+ and npm
- Python 3.10+

### 2. Backend Setup (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed sample database
python app/seed.py

# Run FastAPI dev server (port 8000)
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The API will be live at `http://127.0.0.1:8000`. Access interactive Swagger docs at `http://127.0.0.1:8000/docs`.

### 3. Frontend Setup (Next.js)

```bash
# Navigate to frontend directory
cd frontend

# Install npm packages
npm install

# Start Next.js dev server (port 3000)
npm run dev
```

Open `http://localhost:3000` in your browser. Demo login credentials are pre-filled on the login screen (`demo@fireflies.local` / `demo123`).

---

## 🗄️ Database Schema

Managed via SQLAlchemy ORM with foreign key cascades:

```sql
-- Meetings Table
CREATE TABLE meetings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    meeting_date DATETIME NOT NULL,
    duration_minutes INTEGER NOT NULL,
    audio_url VARCHAR(500),
    video_url VARCHAR(500),
    summary TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Transcripts Table
CREATE TABLE transcripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_id INTEGER NOT NULL,
    speaker VARCHAR(100) NOT NULL,
    start_time VARCHAR(20) NOT NULL,
    end_time VARCHAR(20) NOT NULL,
    text TEXT NOT NULL,
    is_highlighted BOOLEAN DEFAULT 0,
    comment TEXT,
    FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
);

-- Action Items Table
CREATE TABLE action_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_id INTEGER NOT NULL,
    task TEXT NOT NULL,
    assignee VARCHAR(100),
    due_date VARCHAR(50),
    completed BOOLEAN DEFAULT 0,
    FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
);
```

---

## 🌐 API Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/meetings` | List meetings with search, participant filter, date range & sorting |
| `POST` | `/meetings` | Create meeting & parse transcript text or uploaded segments |
| `GET` | `/meetings/{id}` | Retrieve meeting detail payload |
| `PUT` | `/meetings/{id}` | Update meeting title, date, duration & participants |
| `DELETE` | `/meetings/{id}` | Delete meeting & cascade remove child records |
| `POST` | `/meetings/{id}/regenerate-summary` | Dynamically regenerate AI summary by style preset or custom prompt |
| `GET` | `/meetings/{id}/export/markdown` | Export meeting notes & transcript to Markdown |
| `GET` | `/meetings/{id}/transcript/search` | Live search matching transcript segments |
| `PUT` | `/transcript-segments/{id}` | Toggle transcript line highlight or edit comment |
| `POST` | `/meetings/{id}/action-items` | Create new action item task |
| `PUT` | `/action-items/{id}` | Toggle task completion or edit text |
| `DELETE` | `/action-items/{id}` | Delete action item |

---

## 💡 Assumptions & Implementation Notes

1. **Audio/Video Playback**: Real audio transcription is out of scope per assignment guidelines. Sample meeting audio/video sources and parsed transcript files (`.txt`, `.vtt`, `.json`) are used to demonstrate real-time player synchronization.
2. **Authentication**: Uses a pre-filled demo session (`fireflies_session = authenticated`) with full persistence in `localStorage`.
3. **State Persistence**: Active views and meeting selections are synced with URL query parameters (`?view=meetings`, `?view=detail&id=1`) and `localStorage` to preserve state on page refreshes.
