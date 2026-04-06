# Deployment Fix Summary

## Issues Fixed

### 1. **Frontend Environment Configuration**
- **Problem**: `frontend/.env` was missing `NEXT_PUBLIC_BACKEND_URL`
- **Fix**: Added `NEXT_PUBLIC_BACKEND_URL=http://localhost:8000` for local development
- **Production**: This needs to be set in Vercel environment variables

### 2. **Backend CORS Configuration**
- **Problem**: CORS was only allowing a specific Vercel preview URL
- **Fix**: Updated `backend/app/main.py` to allow:
  - `http://localhost:3000` (local development)
  - `http://localhost:3001` (alternative dev port)
  - `https://donut-ai-eosin.vercel.app` (production)
  - `*.vercel.app` (all Vercel preview deployments)

### 3. **Frontend URL Configuration**
- **Problem**: Root `.env` had an incorrect Vercel preview URL
- **Fix**: Changed `FRONTEND_URL=http://localhost:3000` for local testing

### 4. **Next.js Configuration**
- **Problem**: `next.config.js` only proxied API requests in production
- **Fix**: Updated to proxy API requests in both development and production using `NEXT_PUBLIC_BACKEND_URL`

## Deployment Instructions

### For Railway (Backend)

1. **Environment Variables** (set in Railway dashboard):
   ```
   GROQ_API_KEY=your_actual_groq_api_key
   SUPABASE_URL=https://bqwcahpypjatdbjfdkri.supabase.co
   SUPABASE_KEY=sb_publishable_7fVCsy26DpiBa8nrPqKazQ_P8YAupMj
   FRONTEND_URL=https://donut-ai-eosin.vercel.app
   ```

2. **Deployment**:
   - Railway will automatically detect `railway.json`
   - Uses `backend/Dockerfile` for building
   - Starts with `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### For Vercel (Frontend)

1. **Environment Variables** (set in Vercel dashboard):
   ```
   NEXT_PUBLIC_BACKEND_URL=https://donutai-production.up.railway.app
   ```

2. **Build Settings**:
   - Framework: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

3. **Deployment**:
   - Vercel will automatically deploy from GitHub
   - The `NEXT_PUBLIC_BACKEND_URL` will be baked into the build

## Testing Locally

### Option 1: Using start.bat (Windows)
```bash
cd donutAI
start.bat
```

### Option 2: Manual startup
1. **Terminal 1 - Backend**:
   ```bash
   cd donutAI
   # Activate virtual environment if needed
   # On Windows: .venv\Scripts\activate
   # On Mac/Linux: source .venv/bin/activate
   
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Terminal 2 - Frontend**:
   ```bash
   cd donutAI/frontend
   npm run dev
   ```

3. **Access**:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Verification Steps

After deploying to production:

1. **Check Backend Health**:
   - Visit: `https://donutai-production.up.railway.app/health`
   - Should return: `{"status": "healthy", ...}`

2. **Check Frontend**:
   - Visit: `https://donut-ai-eosin.vercel.app`
   - Should load the UI

3. **Test API Connection**:
   - Open browser console on the frontend
   - Look for any CORS errors
   - Try sending a chat message

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'app'"
**Solution**: Make sure you're in the correct directory and using the virtual environment:
```bash
cd donutAI/backend
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Mac/Linux
python -m uvicorn app.main:app --reload
```

### Issue: CORS errors in browser console
**Solution**: 
1. Verify `NEXT_PUBLIC_BACKEND_URL` is set correctly in Vercel
2. Check that backend CORS allows your Vercel domain
3. Clear browser cache and redeploy

### Issue: Frontend can't connect to backend
**Solution**:
1. Verify backend is running and accessible
2. Check that `NEXT_PUBLIC_BACKEND_URL` matches your backend URL
3. Test backend health endpoint directly

## Files Modified

1. `donutAI/frontend/.env` - Added `NEXT_PUBLIC_BACKEND_URL`
2. `donutAI/.env` - Fixed `FRONTEND_URL` for local testing
3. `donutAI/backend/app/main.py` - Updated CORS configuration
4. `donutAI/frontend/next.config.js` - Improved API routing

## Next Steps

1. Commit these changes to GitHub:
   ```bash
   git add .
   git commit -m "Fix deployment configuration for Railway and Vercel"
   git push origin main
   ```

2. Railway and Vercel will automatically redeploy

3. Set environment variables in both platforms as described above

4. Test the live deployment