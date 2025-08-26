# Deployment Checklist

## Phase 1: GitHub Setup ✅
- [ ] Create GitHub account
- [ ] Install GitHub Desktop
- [ ] Upload project to GitHub
- [ ] Push code to main branch

## Phase 2: Backend Deployment (Render) ✅
- [ ] Create Render account
- [ ] Connect GitHub repository
- [ ] Configure Python service
- [ ] Wait for deployment
- [ ] Copy backend URL
- [ ] Test backend (add /docs to URL)

## Phase 3: Frontend Configuration ✅
- [ ] Copy env-template.txt to .env
- [ ] Update REACT_APP_API_URL with backend URL
- [ ] Run npm run build
- [ ] Verify build folder created

## Phase 4: Frontend Deployment (Netlify) ✅
- [ ] Create Netlify account
- [ ] Deploy build folder
- [ ] Set environment variable REACT_APP_API_URL
- [ ] Redeploy with new environment variable

## Phase 5: Testing ✅
- [ ] Test backend API endpoints
- [ ] Test frontend navigation
- [ ] Verify data loads from backend
- [ ] Test all app sections

## Final Result
Your trading signals app should be live at:
- **Frontend**: Your Netlify URL
- **Backend**: Your Render URL

## Notes
- Backend sleeps after 15 min inactivity (Render free tier)
- First request after sleep takes 30-60 seconds
- All hosting is completely free

