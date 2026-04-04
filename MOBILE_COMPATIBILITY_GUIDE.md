# Mobile Compatibility Guide

## Current Status

### ✅ Working on Mobile
- **Wake Word Detection** - Works on iPad and Samsung mobile (Chrome)
- **Sliders** - Work on all mobile devices
- **UI Layout** - Responsive design implemented
- **Touch Interactions** - Touch-friendly sizing (44px minimum)

### ⚠️ Requires Backend Deployment
- **Chat Completion** - Requires deployed backend
- **TTS (Text-to-Speech)** - Requires deployed backend
- **Console Settings Dropdowns** - Now fixed with CSS improvements

## Issue: "Sorry, I encountered an error"

### Root Cause
The frontend is trying to connect to a backend that isn't deployed or accessible from the internet. When you deploy to Vercel, the frontend needs a publicly accessible backend URL.

### Solution Steps

1. **Deploy the Backend**
   - Use Railway, Render, or similar service
   - Follow DEPLOYMENT_GUIDE.md for instructions

2. **Configure Vercel Environment Variables**
   - Go to Vercel → Project → Settings → Environment Variables
   - Add `NEXT_PUBLIC_BACKEND_URL` = `https://your-backend-url.com`
   - Redeploy the frontend

3. **Verify Backend Accessibility**
   - Test your backend URL from a browser
   - Ensure CORS allows your Vercel domain

## Browser Compatibility

### Voice Features
| Browser | Speech Recognition | Speech Synthesis | Wake Word |
|---------|-------------------|------------------|-----------|
| Chrome (Desktop) | ✅ | ✅ | ✅ |
| Chrome (Android) | ✅ | ✅ | ✅ |
| Chrome (iOS) | ⚠️ Limited | ✅ | ⚠️ Limited |
| Safari (iOS) | ⚠️ Limited | ✅ | ⚠️ Limited |
| Samsung Internet | ✅ | ✅ | ✅ |

### Notes
- iOS browsers have limited SpeechRecognition support
- Wake word detection works best on Chrome/Edge desktop and Android
- TTS works on all modern browsers

## Mobile-Specific Fixes Applied

### 1. Dropdown Text Visibility
```css
select option {
  background-color: #272D3D !important;
  color: #EDEDF5 !important;
}
```

### 2. Touch-Friendly Sizing
```css
@media (max-width: 768px) {
  select, input[type="range"], button {
    min-height: 44px;
  }
}
```

### 3. iOS Safari Fixes
- Prevents zoom on input focus (font-size: 16px)
- Proper select styling for iOS

## Testing Checklist

### Before Deployment
- [ ] Test on Chrome Desktop
- [ ] Test on Chrome Android
- [ ] Test on Safari iOS
- [ ] Verify all buttons are tappable (44px minimum)
- [ ] Check text readability on small screens

### After Deployment
- [ ] Verify backend URL is accessible
- [ ] Test chat functionality
- [ ] Test TTS functionality
- [ ] Test voice recognition
- [ ] Test wake word detection

## Troubleshooting Mobile Issues

### Chat Not Working
1. Check if backend is deployed and accessible
2. Verify `NEXT_PUBLIC_BACKEND_URL` is set in Vercel
3. Check browser console for error messages
4. Ensure CORS allows your Vercel domain

### Voice Not Working
1. Grant microphone permission
2. Use HTTPS (required for microphone access)
3. Try Chrome on Android for best support
4. Check if SpeechRecognition is supported

### Dropdown Text Invisible
1. Clear browser cache
2. Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
3. Update to latest version

## Recommended Setup for Production

1. **Backend**: Deploy to Railway with proper environment variables
2. **Frontend**: Deploy to Vercel with `NEXT_PUBLIC_BACKEND_URL`
3. **Database**: Use Supabase for production data
4. **Error Tracking**: Configure Sentry for monitoring
5. **CDN**: Use Vercel's built-in CDN for static assets

## Quick Test Command

To test if your backend is accessible from the internet:
```bash
curl https://your-backend-url.com/health
```

If you get a JSON response, the backend is accessible. If not, check:
- Backend is running
- Port is open
- Firewall allows traffic
- CORS is configured correctly