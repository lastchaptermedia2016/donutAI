# Client Deployment & Usage Guide

## Part 1: Developer Deployment Steps (You)

### Step 1: Prepare Client Branding
Decide on client's branding:
- App Name (e.g., "Acme Assistant")
- Tagline (e.g., "Your AI Business Partner")
- Logo Emoji (e.g., "🏢")
- Primary Color (e.g., "#1E40AF")
- Secondary Color (e.g., "#EFF6FF")
- Business Name (e.g., "Acme Corp Reception")

### Step 2: Deploy Backend to Railway
1. Go to [Railway](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Go to Project → Variables
5. Add these environment variables:

```env
# Required API Keys
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=https://client-project.supabase.co
SUPABASE_KEY=client_supabase_anon_key

# Client Branding
APP_NAME="Acme Assistant"
APP_DESCRIPTION="Your AI Business Partner"
APP_LOGO_EMOJI="🏢"
BRAND_PRIMARY_COLOR="#1E40AF"
BRAND_SECONDARY_COLOR="#EFF6FF"
BUSINESS_NAME="Acme Corp Reception"

# Optional
JWT_SECRET=random_secret_string
ADMIN_PASSPHRASE=client_secure_passphrase
```

6. Railway automatically deploys
7. Copy the generated Railway URL (e.g., `https://acme-assistant-production.up.railway.app`)

### Step 3: Deploy Frontend to Vercel
1. Go to [Vercel](https://vercel.com)
2. Click "Add New Project" → Import your GitHub repository
3. In "Root Directory" select `frontend`
4. Add environment variable:
   - `NEXT_PUBLIC_BACKEND_URL` = `https://acme-assistant-production.up.railway.app`
5. Click "Deploy"
6. Copy the Vercel URL (e.g., `https://acme-assistant.vercel.app`)

### Step 4: Configure Custom Domain (Optional)
1. In Vercel: Project → Settings → Domains → Add client's domain
2. In Railway: Project → Settings → Domains → Add backend domain
3. Update DNS records as instructed

### Step 5: Enterprise Integration (Optional - Google Workspace / Microsoft 365)

#### Google Workspace (Gmail + Calendar)
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Gmail API and Google Calendar API
4. Create OAuth 2.0 credentials (Web application type)
5. Add authorized redirect URI: `https://your-backend.railway.app/api/auth/callback`
6. Add these environment variables to Railway:

```env
# Google Workspace Integration
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_CALENDAR_ID=primary
```

#### Microsoft 365 (Outlook Email + Calendar)
1. Go to [Azure Portal](https://portal.azure.com)
2. Register a new application in Azure AD
3. Add permissions: Mail.ReadWrite, Mail.Send, Calendars.ReadWrite
4. Create a client secret
5. Add redirect URI: `https://your-backend.railway.app/api/auth/callback`
6. Add these environment variables to Railway:

```env
# Microsoft 365 Integration
OUTLOOK_CLIENT_ID=your_application_client_id
OUTLOOK_CLIENT_SECRET=your_client_secret
OUTLOOK_TENANT_ID=your_directory_tenant_id
```

7. Redeploy on Railway (changes take effect automatically)

#### Twilio Phone Answering (Optional - AI Receptionist)
1. Go to [Twilio Console](https://console.twilio.com)
2. Buy a phone number (supports voice calls)
3. Get your Account SID and Auth Token from Dashboard
4. Add these environment variables to Railway:

```env
# Twilio Phone Answering
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

5. Configure the phone number webhook:
   - Go to Phone Numbers → Manage → Active Numbers
   - Click your number
   - Under "Voice & Fax" → "A CALL COMES IN"
   - Select "Webhook" and enter: `https://your-backend.railway.app/api/twilio/voice`
   - Set method to "HTTP POST"
   - Click "Save"

6. Redeploy on Railway (changes take effect automatically)

**Features when enabled:**
- AI answers calls automatically
- Natural voice conversation
- Can schedule appointments, take messages, answer FAQs
- Transcribes calls and stores in system
- 24/7 availability

### Step 6: Handoff to Client
Send client:
- Frontend URL: `https://acme-assistant.vercel.app`
- Admin passphrase (set in `ADMIN_PASSPHRASE`)
- Brief usage instructions (see Part 2 below)
- Enterprise integration status (if configured)

---

## Part 2: Client Usage Steps

### On Laptop/Desktop

#### Option A: Web Browser (Easiest)
1. Open browser (Chrome, Firefox, Edge, or Safari)
2. Go to the provided URL (e.g., `https://acme-assistant.vercel.app`)
3. Enter the admin passphrase to log in
4. Start using the assistant via:
   - **Text**: Type in the chat box
   - **Voice**: Click the microphone icon and speak

#### Option B: Install as PWA (Recommended)
1. Open the app URL in Chrome or Edge
2. Click the install icon (⊕) in the address bar
3. Click "Install"
4. The app appears on desktop/start menu
5. Launch like any native app

### On Phone/Tablet

#### iPhone/iPad (iOS)
1. Open Safari
2. Go to the app URL
3. Tap the Share button (square with arrow)
4. Scroll down and tap "Add to Home Screen"
5. Name it (e.g., "Acme Assistant") and tap "Add"
6. App icon appears on home screen
7. Tap to open and use

#### Android
1. Open Chrome
2. Go to the app URL
3. Tap the menu (three dots)
4. Tap "Install app" or "Add to Home screen"
5. Tap "Install" or "Add"
6. App icon appears on home screen
7. Tap to open and use

### Voice Commands
The assistant responds to natural voice commands:
- "Add a task to call John tomorrow"
- "Write in my diary about today's meeting"
- "What's on my calendar for this week?"
- "Search for AI news"
- "Switch to business mode"

### Features Available
- **Chat**: Text or voice conversation
- **Tasks**: Create, view, complete tasks
- **Diary**: Write and read journal entries
- **Memory**: Store and recall information
- **Search**: Web search via DuckDuckGo
- **Calendar**: View and manage events
- **Email**: Send and read emails (with Gmail/Outlook integration)
- **Phone**: AI receptionist via Twilio (optional)
- **Slack/Teams**: Chat integration (optional)
- **Multi-language**: Support for multiple languages (optional)
- **Analytics**: Usage metrics and insights (optional)
- **Console**: Admin dashboard for monitoring

---

## Part 3: Ongoing Management

### For You (Developer)
- Monitor Railway logs for errors
- Update environment variables as needed
- Redeploy when making code changes

### For Client
- Use the admin passphrase to access console
- Monitor usage via the dashboard
- Contact you for technical support

---

## Quick Reference

| Action | Steps |
|--------|-------|
| **Deploy Backend** | Railway → New Project → GitHub → Set env vars → Auto-deploy |
| **Deploy Frontend** | Vercel → New Project → Select `frontend` folder → Set `NEXT_PUBLIC_BACKEND_URL` → Deploy |
| **Rebrand** | Change `APP_NAME`, `BRAND_PRIMARY_COLOR`, etc. in Railway env vars → Redeploy |
| **Client Login** | Web browser → Enter admin passphrase |
| **Install on Phone** | Browser → Share → Add to Home Screen |
| **Use Voice** | Click microphone → Speak naturally |