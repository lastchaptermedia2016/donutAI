# Troubleshooting Guide

## Quick Reference

### Common Issues and Solutions

#### 1. Voice Recognition Not Working
**Symptoms:** Microphone icon doesn't respond, no speech-to-text

**Solutions:**
- Use Chrome or Edge browser (Firefox not supported)
- Check microphone permissions in browser settings
- Ensure HTTPS in production (required for Web Speech API)
- Test at `/mic-test` page for isolated testing
- Check browser console for error messages

#### 2. Wake Word Detection Not Activating
**Symptoms:** Saying "Donut" doesn't trigger voice input

**Solutions:**
- Click the bell icon in the header to enable wake word detection
- Grant microphone permission when prompted
- Ensure browser supports SpeechRecognition API
- Check that no other app is using the microphone

#### 3. TTS (Text-to-Speech) Not Working
**Symptoms:** AI responses are silent

**Solutions:**
- Check that `GROQ_API_KEY` is set correctly
- Toggle TTS button (speaker icon) to enable/disable
- Check browser volume settings
- Verify TTS provider in environment variables

#### 4. API Connection Errors
**Symptoms:** "Failed to connect" or network errors

**Solutions:**
- Ensure backend is running on port 8000
- Check `NEXT_PUBLIC_BACKEND_URL` in frontend `.env`
- Verify CORS settings in backend
- Check firewall/antivirus blocking connections

#### 5. Database Errors
**Symptoms:** "Database connection failed" or data not saving

**Solutions:**
- Ensure `data` directory exists: `mkdir -p data`
- Check file permissions: `chmod 755 data`
- Verify SQLite database file isn't corrupted
- Check disk space

#### 6. Build Errors
**Symptoms:** TypeScript/ESLint errors during build

**Solutions:**
- Run `npm run lint` to check for issues
- Fix any TypeScript errors
- Ensure all dependencies are installed: `npm install`
- Clear cache: `rm -rf node_modules .next && npm install`

#### 7. Rate Limit Errors (429)
**Symptoms:** "Too many requests" errors

**Solutions:**
- Wait a moment and retry
- Rate limit is 200 requests/minute
- AI settings endpoints are exempt from rate limiting
- Consider increasing rate limit in backend if needed

#### 8. WebSocket Connection Failed
**Symptoms:** Chat not working, connection errors

**Solutions:**
- Ensure backend is running on port 8000
- Check WebSocket URL in frontend
- Verify `ws://` protocol is supported
- Check proxy/firewall settings

## Debugging Tools

### Browser Console
Open browser developer tools (F12) and check:
- Console for errors
- Network tab for failed requests
- Application tab for storage issues

### Backend Logs
```bash
# View logs
docker compose logs -f backend

# Or if running locally
tail -f backend/logs/*.log
```

### Health Check
Visit `/health` endpoint to check system status:
```bash
curl http://localhost:8000/health
```

### API Documentation
Visit `/docs` endpoint for interactive API testing:
```
http://localhost:8000/docs
```

## Performance Issues

### Slow Response Times
- Check Groq API status
- Verify network connectivity
- Consider caching frequently used data
- Check database query performance

### High Memory Usage
- Check for memory leaks in browser
- Limit conversation history size
- Clear browser cache regularly
- Monitor backend memory usage

## Error Tracking

### Sentry Integration
If configured, errors are automatically tracked in Sentry:
1. Go to your Sentry dashboard
2. Check "Issues" for error details
3. View stack traces and user context
4. Monitor error frequency

### Local Debugging
Enable debug logging:
```bash
# Backend
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload

# Frontend
npm run dev
```

## Getting Help

### Resources
- [API Documentation](http://localhost:8000/docs)
- [GitHub Issues](https://github.com/your-repo/issues)
- [Community Discord](link-to-discord)

### Reporting Issues
When reporting issues, include:
1. Browser and version
2. Operating system
3. Steps to reproduce
4. Console errors (if any)
5. Network tab screenshots (if relevant)

## Maintenance

### Regular Tasks
- Clear old conversation data monthly
- Update dependencies quarterly
- Review Sentry errors weekly
- Monitor performance metrics

### Backup & Recovery
```bash
# Backup database
cp data/donut.sqlite backup/donut-$(date +%Y%m%d).sqlite

# Restore from backup
cp backup/donut-YYYYMMDD.sqlite data/donut.sqlite
```

## Security Considerations

### API Keys
- Never commit `.env` files
- Rotate keys regularly
- Use environment-specific keys
- Monitor key usage in dashboards

### Rate Limiting
- Default: 200 requests/minute
- Adjust based on usage patterns
- Monitor for abuse
- Consider per-user limits for production

---

**Last Updated:** April 4, 2026
**Version:** 0.1.0