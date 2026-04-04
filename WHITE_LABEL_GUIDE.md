# White-Label Configuration Guide

This project is fully white-label enabled, allowing you to rebrand the entire application for your clients with simple environment variable changes.

## Quick Start - Rebrand in 5 Steps

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Update branding variables in `.env`:**
   ```env
   # Change the app name
   APP_NAME="Your Brand Name"
   
   # Change the tagline
   APP_DESCRIPTION="Your Tagline Here"
   
   # Change the logo emoji (or use a custom image)
   APP_LOGO_EMOJI="🤖"
   
   # Change brand colors
   BRAND_PRIMARY_COLOR="#YourPrimaryHex"
   BRAND_SECONDARY_COLOR="#YourSecondaryHex"
   
   # Change business name for receptionist
   BUSINESS_NAME="Your Company Receptionist"
   ```

3. **Deploy to Railway/Vercel** - Environment variables will be picked up automatically

4. **Test the branding** - Visit your app and verify the new branding

5. **For each new client** - Just change the environment variables and redeploy!

## Available Branding Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `APP_NAME` | Main application name | `Donut` | `AssistantAI` |
| `APP_DESCRIPTION` | App tagline/description | `Executive Function Co-Pilot` | `Your AI Business Assistant` |
| `APP_LOGO_EMOJI` | Emoji used as logo | `🍩` | `🤖`, `💼`, `🧠` |
| `BRAND_PRIMARY_COLOR` | Primary brand color (hex) | `#FFBF00` | `#3B82F6` |
| `BRAND_SECONDARY_COLOR` | Secondary/background color (hex) | `#FFF8DC` | `#F0F9FF` |
| `BUSINESS_NAME` | Receptionist business name | `Donut Receptionist` | `Acme Corp Reception` |

## API Endpoint

The branding configuration is exposed via the `/api/branding` endpoint:

```json
GET /api/branding

{
  "app_name": "Your Brand Name",
  "app_description": "Your Tagline Here",
  "app_logo_emoji": "🤖",
  "brand_primary_color": "#3B82F6",
  "brand_secondary_color": "#F0F9FF",
  "business_name": "Acme Corp Reception"
}
```

Your frontend can fetch this endpoint to dynamically apply branding.

## Example Configurations

### Corporate Business
```env
APP_NAME="CorpAssist"
APP_DESCRIPTION="Enterprise AI Assistant"
APP_LOGO_EMOJI="💼"
BRAND_PRIMARY_COLOR="#1E40AF"
BRAND_SECONDARY_COLOR="#EFF6FF"
BUSINESS_NAME="CorpAssist Reception"
```

### Healthcare
```env
APP_NAME="MedAssist"
APP_DESCRIPTION="Healthcare AI Companion"
APP_LOGO_EMOJI="🏥"
BRAND_PRIMARY_COLOR="#059669"
BRAND_SECONDARY_COLOR="#ECFDF5"
BUSINESS_NAME="MedAssist Patient Services"
```

### Education
```env
APP_NAME="EduPal"
APP_DESCRIPTION="Student Success Assistant"
APP_LOGO_EMOJI="📚"
BRAND_PRIMARY_COLOR="#7C3AED"
BRAND_SECONDARY_COLOR="#F5F3FF"
BUSINESS_NAME="EduPal Student Services"
```

### Personal Brand
```env
APP_NAME="MyAI"
APP_DESCRIPTION="Your Personal AI Sidekick"
APP_LOGO_EMOJI="⚡"
BRAND_PRIMARY_COLOR="#F59E0B"
BRAND_SECONDARY_COLOR="#FFFBEB"
BUSINESS_NAME="MyAI Assistant"
```

## Frontend Integration

To make your frontend fully dynamic, fetch branding from the API:

```typescript
// Example: Fetch branding on app load
const response = await fetch('/api/branding');
const branding = await response.json();

// Apply to document
document.title = branding.app_name;
document.documentElement.style.setProperty('--primary-color', branding.brand_primary_color);
document.documentElement.style.setProperty('--secondary-color', branding.brand_secondary_color);

// Update logo
document.querySelector('.logo').textContent = branding.app_logo_emoji;
```

## Multi-Tenant Deployment

For SaaS deployments with multiple clients:

1. **Single codebase** - Deploy the same code for all clients
2. **Environment-based branding** - Each deployment has unique environment variables
3. **Subdomain routing** - Use subdomains like `client1.yourapp.com`, `client2.yourapp.com`
4. **Database isolation** - Each client can have their own Supabase project

## Railway Deployment

1. Create a new Railway project for each client
2. Connect to your GitHub repository
3. Set the branding environment variables
4. Deploy!

## Vercel Frontend

1. Set `NEXT_PUBLIC_BACKEND_URL` to your Railway backend URL
2. Optionally fetch branding from `/api/branding` on app load
3. Deploy to Vercel

## Tips for Resellers

- **Keep a template**: Save different `.env` templates for different industries
- **Use a deployment script**: Automate environment variable setup
- **Test thoroughly**: Verify branding on both frontend and backend
- **Document for clients**: Provide a simple form for clients to choose their branding
- **Version control**: Tag releases for each client customization

## Support

For questions about white-label configuration, refer to:
- `backend/app/config.py` - Backend configuration
- `.env.example` - All available environment variables
- `DEPLOYMENT_GUIDE.md` - Deployment instructions