# Donut AI - Deployment Guide

## Railway Deployment

### Prerequisites
1. GitHub repository connected to Railway
2. Groq API key from https://console.groq.com
3. Supabase project (for database)

### Step-by-Step Deployment

#### 1. Connect to Railway
- Go to https://railway.app
- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose your repository

#### 2. Configure Environment Variables
In Railway dashboard → Variables, add these **required** variables:

```bash
# REQUIRED - Groq API
GROQ_API_KEY=your_actual_groq_api_key_here

# REQUIRED - Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# LLM Models (optional - defaults are set)
LLM_MODEL=llama-3.3-70b-versatile
INTENT_MODEL=llama-3.1-8b-instant

# Server Settings (optional - defaults are set)
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_URL=https://your-frontend.vercel.app

# Authentication (optional - defaults are set)
JWT_SECRET=change_me_to_random_string
ADMIN_PASSPHRASE=your_secure_passphrase

# Optional - ElevenLabs (for premium TTS)
ELEVENLABS_API_KEY=

# Optional - xAI (for web search)
XAI_API_KEY=
```

#### 3. Deploy
Railway will automatically:
- Detect the `railway.json` configuration
- Use `backend/Dockerfile` for building
- Start with `uvicorn` (not gunicorn)

### Troubleshooting

#### Issue: "gunicorn could not be found"
**Cause:** Railway is not using the correct Dockerfile or start command.

**Solution:**
1. Make sure `railway.json` exists in the root directory
2. In Railway dashboard → Settings → Build, ensure Dockerfile is set to `backend/Dockerfile`
3. Redeploy

#### Issue: Groq TTS falls back to browser immediately
**Cause:** `GROQ_API_KEY` environment variable is not set or incorrect.

**Solution:**
1. Go to Railway dashboard → Variables
2. Ensure `GROQ_API_KEY` is set to your actual Groq API key
3. Redeploy

#### Issue: App crashes on startup
**Cause:** Missing required environment variables.

**Solution:**
1. Check Railway logs for specific error
2. Ensure all REQUIRED variables are set:
   - `GROQ_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

## Local Development

### Prerequisites
```bash
pip install -r requirements.txt
```

### Run Backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Setup
1. Copy `.env.example` to `.env`
2. Fill in your API keys:
   - `GROQ_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

## Voice Services Configuration

### TTS (Text-to-Speech)
Default fallback order: `groq,elevenlabs,xai,browser`

- **Groq TTS**: Uses `canopylabs/orpheus-v1-english` model
- **ElevenLabs**: Premium quality (10k chars/month free)
- **xAI**: Alternative cloud provider
- **Browser**: Frontend SpeechSynthesis API (always available)

### STT (Speech-to-Text)
Default fallback order: `groq,elevenlabs,xai,browser`

- **Groq STT**: Uses `whisper-large-v3` model
- **Browser**: Web Speech API (always available)

### Changing TTS/STT Priority
Update environment variables:
```bash
TTS_PROVIDER_PRIORITY=groq,elevenlabs,browser
STT_PROVIDER_PRIORITY=groq,browser
```

## Frontend Deployment (Vercel)

1. Connect your GitHub repository to Vercel
2. Set root directory to `frontend`
3. Deploy

### Environment Variables (Vercel)
```bash
NEXT_PUBLIC_BACKEND_URL=https://your-backend.railway.app
```

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐
│   Frontend      │     │    Railway      │
│  (Next.js)      │────▶│   (Backend)     │
│   on Vercel     │     │   (FastAPI)     │
└─────────────────┘     └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    Supabase     │
                         │   (Database)    │
                         └─────────────────┘
```

### External APIs Used
- **Groq**: LLM chat completions + TTS/STT
- **Supabase**: Database + Auth
- **ElevenLabs** (optional): Premium TTS
- **xAI** (optional): Web search