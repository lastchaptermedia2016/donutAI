# CI/CD Setup Guide

## Overview

This project now includes automated testing and preview deployments through GitHub Actions and Vercel.

## What's Configured

### 1. GitHub Actions (`.github/workflows/test.yml`)

**Triggers:**
- Every push to `main` or `master` branch
- Every pull request to `main` or `master` branch

**Jobs:**
1. **Backend Tests**
   - Sets up Python 3.11
   - Installs dependencies
   - Runs pytest on `backend/tests/`
   - Uses cached pip packages for speed

2. **Frontend Build**
   - Sets up Node.js 20
   - Installs dependencies
   - Runs `npm run build`
   - Runs linting (if available)
   - Uses cached npm packages for speed

### 2. Vercel Preview Deployments

**How It Works:**
1. Create a new branch: `git checkout -b feature-name`
2. Push to GitHub: `git push origin feature-name`
3. Create a Pull Request on GitHub
4. Vercel automatically:
   - Detects the PR
   - Builds the frontend
   - Deploys to a unique URL
   - Posts the URL as a comment on the PR

**Preview URL Format:**
```
https://donut-ai-git-[branch-name].vercel.app
```

## Setup Instructions

### 1. GitHub Secrets

Add these secrets to your GitHub repository:

1. Go to GitHub → Your Repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add:
   - `GROQ_API_KEY`: Your Groq API key (for backend tests)

### 2. Vercel Connection

If you haven't already:

1. Go to [Vercel](https://vercel.com)
2. Import your GitHub repository
3. Set the root directory to `frontend`
4. Add environment variable: `NEXT_PUBLIC_BACKEND_URL`
5. Deploy!

Vercel will automatically:
- Deploy to production on pushes to `main`
- Create preview deployments for every PR

## Workflow Example

### Developing a New Feature

```bash
# 1. Create a new branch
git checkout -b add-new-feature

# 2. Make changes and commit
git add .
git commit -m "Add new feature"

# 3. Push to GitHub
git push origin add-new-feature

# 4. Create a Pull Request on GitHub
# - GitHub Actions will automatically run tests
# - Vercel will automatically create a preview deployment
# - Check the PR for test results and preview URL

# 5. Test the preview at: https://donut-ai-git-add-new-feature.vercel.app

# 6. When ready, merge the PR
# - Vercel will automatically deploy to production
```

## Viewing Test Results

### GitHub Actions
1. Go to your GitHub repository
2. Click "Actions" tab
3. See all workflow runs
4. Click on a run to see detailed logs

### Vercel Previews
1. Create a Pull Request
2. Vercel bot will comment with the preview URL
3. Click the URL to test your changes
4. Preview is automatically deleted when PR is merged/closed

## Troubleshooting

### Tests Failing
- Check the "Actions" tab on GitHub
- Click on the failed job to see logs
- Common issues:
  - Missing environment variables
  - Test syntax errors
  - Dependency issues

### Build Failing
- Check Vercel deployment logs
- Common issues:
  - TypeScript errors
  - Missing environment variables
  - Build script errors

### Preview Not Deploying
- Ensure Vercel is connected to your GitHub repo
- Check Vercel project settings
- Verify `frontend/vercel.json` exists

## Benefits

### For Solo Developers
- **Catch bugs early** - Tests run automatically
- **Test before merging** - Preview deployments let you verify changes
- **Professional workflow** - Same as big companies use
- **Zero maintenance** - Set up once, runs forever

### For Teams (Future)
- **Code review** - See live previews of changes
- **Quality assurance** - Tests must pass before merging
- **Collaboration** - Share preview URLs with team members
- **Confidence** - Deploy with certainty

## Cost

- **GitHub Actions**: Free (included with GitHub)
- **Vercel Previews**: Free (included with Vercel Hobby plan)
- **Total**: $0/month

## Next Steps

1. Add your `GROQ_API_KEY` to GitHub Secrets
2. Connect your repository to Vercel (if not already)
3. Create a test branch to verify everything works
4. Start enjoying automated testing and previews!

## Support

If you encounter issues:
1. Check GitHub Actions logs
2. Check Vercel deployment logs
3. Review this guide
4. Ask your AI assistant! 🤖