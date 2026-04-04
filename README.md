# 🍩 Donut - Executive Function Co-Pilot

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![Version](https://img.shields.io/badge/version-0.1.0-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![Node](https://img.shields.io/badge/node-20+-green)]()

A multi-modal agentic voice assistant that acts as your Executive Function Co-Pilot. Donut maintains state, manages dual-contexts (Business vs Personal), and executes actions via voice or text.

## Features

- **Voice-First Interface**: Speak naturally using Web Speech API (STT) with multi-provider TTS fallback (Groq → ElevenLabs → xAI → Browser)
- **Dual Context Management**: Seamlessly switch between Business, Personal, and Neutral modes
- **Memory System**: Long-term semantic memory via LanceDB vector store + short-term rolling buffer
- **Task Management**: Create, list, complete, and delete to-do items across contexts with priority levels
- **Diary/Journal**: Write and review personal or business diary entries with mood tracking
- **Web Search**: Search the web via DuckDuckGo
- **Email Management**: Send/read emails via Gmail API (requires Google OAuth)
- **AI Receptionist**: Automated phone answering with Twilio integration, appointment booking, and reminder system
- **AI Customization**: Customize personality, voice, tone, and model parameters through the console
- **White-Label Ready**: Full rebranding support via environment variables (colors, logo, business name)
- **AI-Powered**: Uses Groq's ultra-fast LLM inference (Llama 3.3 70B)
- **PWA Support**: Installable on desktop and mobile with offline capabilities
- **Management Console**: Full dashboard for monitoring conversations, tasks, memories, AI settings, and system health
- **Luxury UI/UX**: Premium interface with holographic effects, magnetic buttons, gradient mesh backgrounds, particle effects, deep blue accents, multi-layer glassmorphism, and shimmer loading effects

## Architecture

```
┌─────────────────────────────────────────────────┐
│              Frontend (Next.js PWA)             │
│  React 18 + Tailwind + Web Speech API (STT)     │
│  ┌──────────┐ ┌───────────┐ ┌───────────────┐  │
│  │ Chat UI  │ │ Console   │ │ Context Switch│  │
│  │ + Voice  │ │ Dashboard │ │ (B/P/N)       │  │
│  └────┬─────┘ └───────────┘ └───────────────┘  │
│       │ HTTP / WebSocket                        │
└───────┼─────────────────────────────────────────┘
        │
┌───────▼─────────────────────────────────────────┐
│              Backend (FastAPI)                   │
│  ┌─────────────────────────────────────────┐    │
│  │  Agent Orchestrator (LangGraph)          │    │
│  │  Intent → Context Router → Tool Executor │    │
│  └─────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────┐    │
│  │  Groq API (Llama 3.3 70B)               │    │
│  └─────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────┐    │
│  │  Memory: Ring Buffer + LanceDB + SQLite │    │
│  └─────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────┐    │
│  │  Tools: Diary, Tasks, Search, Memory    │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

## Tech Stack ($0 Tier Strategy)

| Component | Technology | Free Tier |
|-----------|------------|-----------|
| **LLM** | Groq (Llama 3.3 70B + Llama 3.1 8B) | Free tier |
| **Database** | Supabase Postgres + pgvector | 500MB free |
| **Auth** | Supabase Auth | Free tier |
| **STT** | Groq Whisper → Browser | Free tier |
| **TTS** | ElevenLabs (briefings) → Browser | 10k chars/month |
| **Search** | xAI Grok | $25-175 credits |
| **Frontend** | Next.js 14, React 18, Tailwind CSS | Free |
| **Deployment** | Docker + Vercel/Railway | Free tier |

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Groq API key ([get one here](https://console.groq.com))

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional
OPENAI_API_KEY=your_openai_key_here
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/callback
JWT_SECRET=your_jwt_secret_here
ADMIN_PASSPHRASE=your_admin_passphrase
TTS_PROVIDER=coqui
ELEVENLABS_API_KEY=your_elevenlabs_key

# Server Settings
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000

# Database
SQLITE_DB_PATH=./data/donut.sqlite
LANCEDB_PATH=./data/lancedb

# Receptionist Settings
BUSINESS_NAME=Donut Receptionist
WORKING_HOURS_START=9
WORKING_HOURS_END=17
APPOINTMENT_SLOT_DURATION=30
```

See `.env.example` for a complete list of available variables.

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .[dev]

# Copy environment file
cp ../.env.example ../.env
# Edit .env with your GROQ_API_KEY

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to access Donut.

### Docker

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your GROQ_API_KEY

# Build and run
docker compose up --build
```

## Project Structure

```
donut-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry + all routes
│   │   ├── config.py             # Settings management
│   │   ├── schemas.py            # Pydantic models
│   │   ├── llm.py                # Groq client
│   │   ├── agents/
│   │   │   └── orchestrator.py   # LangGraph agent
│   │   ├── memory/
│   │   │   ├── ring_buffer.py    # Short-term conversation memory
│   │   │   ├── vector_store.py   # LanceDB semantic memory
│   │   │   └── structured_db.py  # SQLite for tasks/diary
│   │   └── tools/
│   │       ├── task_tool.py      # Task management
│   │       ├── diary_tool.py     # Diary management
│   │       ├── memory_tool.py    # Memory store/recall
│   │       └── search_tool.py    # Web search
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx        # Root layout
│   │   │   ├── page.tsx          # Chat interface
│   │   │   └── console/
│   │   │       ├── layout.tsx
│   │   │       └── page.tsx      # Management console
│   │   ├── components/
│   │   │   └── providers.tsx     # App state context
│   │   ├── hooks/
│   │   │   └── useVoice.ts       # Speech recognition hook
│   │   └── lib/
│   │       └── utils.ts          # Utilities + API client
│   ├── public/
│   │   └── manifest.json         # PWA manifest
│   ├── package.json
│   ├── tailwind.config.ts
│   └── Dockerfile
├── .env.example
├── .env
├── docker-compose.yml
└── README.md
```

## API Reference

### Chat
- `POST /api/chat` - Send a message to Donut
- `WS /ws/chat` - WebSocket for streaming chat

### Memory
- `POST /api/memory/store` - Store a memory
- `POST /api/memory/recall` - Search memories
- `GET /api/memory/all` - Get all memories

### Tasks
- `GET /api/tasks` - List tasks
- `POST /api/tasks` - Create a task
- `PUT /api/tasks/{id}` - Update a task
- `DELETE /api/tasks/{id}` - Delete a task

### Diary
- `GET /api/diary` - Get diary entries
- `POST /api/diary` - Create diary entry
- `DELETE /api/diary/{id}` - Delete entry

### Search
- `GET /api/search?query=...` - Search the web

### Console
- `GET /api/console/dashboard` - Dashboard stats
- `GET /api/console/conversations` - Conversation history
- `GET /api/console/system/health` - System health

### AI Settings
- `GET /api/ai-settings` - Get current AI personality and voice settings
- `PUT /api/ai-settings` - Update AI settings (personality, voice, model parameters)
- `POST /api/ai-settings/reset` - Reset AI settings to defaults
- `GET /api/ai-settings/options` - Get available customization options

### Branding
- `GET /api/branding` - Get current white-label branding configuration

## Usage Examples

### Voice Commands
- "Hey Donut, add a task to review the quarterly report by Friday"
- "Write in my diary about today's team meeting"
- "Remember that my boss prefers concise emails"
- "What did I say about the project timeline?"
- "Search for latest AI news"
- "Switch to business mode"

### Context Management
Use the sidebar to switch between:
- **Business** 🏢 - Work-focused interactions
- **Personal** 🏠 - Life-focused interactions
- **Neutral** ⚡ - Adaptive mode

## Deployment

### Vercel (Frontend) + Railway (Backend)

1. Push to GitHub
2. Connect backend repo to Railway
3. Connect frontend repo to Vercel
4. Set environment variables
5. Deploy!

### Docker

```bash
docker compose up -d
```

### Railway Deployment (Recommended for Production)

For production deployment, use Railway with the included `railway.json` configuration:

1. Push your code to GitHub
2. Connect your repository to Railway
3. Railway will automatically use `backend/Dockerfile` and start with uvicorn
4. Configure environment variables in Railway dashboard

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

## Voice Services

Donut includes a robust multi-provider voice system with automatic fallback:

### Wake Word Detection
- **Wake Words**: "Donut", "Hey Donut", "OK Donut", or "Hello Donut"
- **Background Listening**: Continuously listens for wake word when enabled
- **Auto-Activation**: Automatically starts voice input when wake word is detected
- **Browser Support**: Chrome, Edge, Safari (requires microphone permission)

### Text-to-Speech (TTS)
- **Primary**: Groq TTS using `canopylabs/orpheus-v1-english` model
- **Fallback Chain**: Groq → ElevenLabs → xAI → Browser SpeechSynthesis
- **Customization**: Choose voices (Autumn, Echo, Onyx, Nova) and adjust speed (0.5x - 2.0x)

### Speech-to-Text (STT)
- **Primary**: Groq Whisper using `whisper-large-v3` model
- **Fallback**: Browser Web Speech API

### Browser Compatibility

| Browser | Speech Recognition | Speech Synthesis |
|---------|-------------------|------------------|
| Chrome  | ✅ Full support   | ✅ Full support  |
| Edge    | ✅ Full support   | ✅ Full support  |
| Safari  | ⚠️ Limited        | ✅ Full support  |
| Firefox | ❌ No support     | ✅ Full support  |

## White-Label Configuration

Donut is fully white-label enabled. Rebrand the entire application by setting environment variables:

```env
# Branding Variables
APP_NAME="Your Brand Name"
APP_DESCRIPTION="Your Tagline Here"
APP_LOGO_EMOJI="🤖"
BRAND_PRIMARY_COLOR="#3B82F6"
BRAND_SECONDARY_COLOR="#F0F9FF"
BUSINESS_NAME="Your Company Reception"
```

See [WHITE_LABEL_GUIDE.md](WHITE_LABEL_GUIDE.md) for complete customization options and examples for different industries.

## AI Customization

Customize Donut's personality and behavior through the Console Settings:

- **Personality Tone**: Warm, Professional, Casual, Formal, Humorous, Empathetic
- **Emotional Tone**: Neutral, Cheerful, Calm, Energetic
- **Response Length**: Concise, Balanced, Detailed
- **Formality Level**: 1-10 scale
- **Voice Settings**: Choose TTS voice and adjust speed
- **Model Parameters**: Temperature (0.1-1.0) and Max Tokens (256-4096)

## Additional Documentation

- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Detailed Railway and Vercel deployment instructions
- **[CLIENT_DEPLOYMENT_GUIDE.md](CLIENT_DEPLOYMENT_GUIDE.md)** - Client handoff and usage guide
- **[WHITE_LABEL_GUIDE.md](WHITE_LABEL_GUIDE.md)** - Complete white-label customization guide
- **[BUILD_AND_TEST_REPORT.md](BUILD_AND_TEST_REPORT.md)** - Production readiness report
- **[LUXURY_UI_ENHANCEMENTS.md](LUXURY_UI_ENHANCEMENTS.md)** - Documentation for premium UI/UX features including holographic effects, magnetic buttons, gradient mesh backgrounds, particle effects, and more
- **[CI_CD_SETUP.md](CI_CD_SETUP.md)** - GitHub Actions and Vercel preview deployments setup guide
- **[TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md)** - Comprehensive troubleshooting guide for common issues
- **[STABILITY_REVIEW_REPORT.md](STABILITY_REVIEW_REPORT.md)** - Code stability analysis and production readiness assessment
- **[MOBILE_COMPATIBILITY_GUIDE.md](MOBILE_COMPATIBILITY_GUIDE.md)** - Mobile device compatibility guide and browser support matrix

## Troubleshooting

### Common Issues

#### 1. Groq API Key Error
**Error:** `GROQ_API_KEY is required`
**Solution:** 
- Get your API key from [console.groq.com](https://console.groq.com)
- Add it to your `.env` file: `GROQ_API_KEY=your_key_here`

#### 2. Python Version Error
**Error:** `Python 3.11+ is required`
**Solution:**
- Install Python 3.11 or higher from [python.org](https://python.org)
- Verify: `python --version`

#### 3. Node.js Version Error
**Error:** `Node.js 20+ is required`
**Solution:**
- Install Node.js 20 or higher from [nodejs.org](https://nodejs.org)
- Verify: `node --version`

#### 4. Port Already in Use
**Error:** `Address already in use: 8000`
**Solution:**
- Kill the process: `lsof -i :8000 | kill -9`
- Or use a different port: `uvicorn app.main:app --port 8001`

#### 5. Database Errors
**Error:** `Database connection failed`
**Solution:**
- Ensure the `data` directory exists: `mkdir -p data`
- Check file permissions: `chmod 755 data`

#### 6. WebSocket Connection Failed
**Error:** `WebSocket connection failed`
**Solution:**
- Ensure backend is running on port 8000
- Check CORS configuration in `backend/app/main.py`
- Verify `NEXT_PUBLIC_BACKEND_URL` in frontend `.env`

#### 7. Voice Recognition Not Working
**Error:** `SpeechRecognition API not supported`
**Solution:**
- Use Chrome or Edge browser (Firefox not supported)
- Enable microphone permissions in browser settings
- Ensure HTTPS in production (required for Web Speech API)
- Check browser console for detailed error messages
- Try the mic-test page at `/mic-test` for isolated testing

#### 8. Microphone Permission Denied
**Error:** `Permission denied` or `NotAllowedError`
**Solution:**
- Reset browser permissions: Go to browser settings → Site permissions → Microphone
- Remove the site from blocked list and try again
- Ensure no other application is using the microphone

#### 9. TTS (Text-to-Speech) Not Working
**Error:** No audio output from TTS
**Solution:**
- Check that `GROQ_API_KEY` is set correctly (Groq TTS requires API key)
- Verify TTS provider priority in environment variables
- Browser SpeechSynthesis is always available as final fallback
- Use the TTS toggle button in the UI to enable/disable speech output

#### 10. Build Errors
**Error:** `TypeScript/ESLint errors`
**Solution:**
- Run `npm run lint` to check for issues
- Fix any TypeScript errors
- Ensure all dependencies are installed: `npm install`

### Getting Help

- Check the [API Documentation](http://localhost:8000/docs)
- Review the [Console Dashboard](http://localhost:3000/console)
- Check the logs: `docker compose logs -f`

## License

MIT

## Roadmap

- [ ] Google Calendar integration
- [ ] Reminder scheduling with APScheduler
- [ ] Porcupine wake word for always-listening desktop
- [ ] ElevenLabs TTS for better voice quality
- [ ] Multi-user authentication
- [ ] Export data (Markdown, JSON)
- [ ] iOS/Android native apps