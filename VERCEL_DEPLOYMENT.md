# Vercel Deployment Guide for AlphaForge Frontend

## Prerequisites
1. A Vercel account (sign up at [vercel.com](https://vercel.com))
2. Vercel CLI installed globally: `npm i -g vercel`
3. Git repository (GitHub, GitLab, or Bitbucket)

## Deployment Steps

### Method 1: Deploy via Vercel Dashboard (Recommended)

1. **Push your code to a Git repository**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your Git repository
   - Select the `frontend` folder as the root directory

3. **Configure Environment Variables**
   - In Vercel dashboard, go to your project settings
   - Navigate to "Environment Variables"
   - Add: `REACT_APP_API_BASE_URL` = `http://161.118.218.33:5000/api`

4. **Deploy**
   - Click "Deploy" and wait for the build to complete
   - Your app will be available at `https://your-project-name.vercel.app`

### Method 2: Deploy via Vercel CLI

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel
   ```
   - Follow the prompts to configure your project
   - Set the root directory as `.` (current directory)
   - Confirm the build settings

4. **Set Environment Variables**
   ```bash
   vercel env add REACT_APP_API_BASE_URL
   # Enter: http://161.118.218.33:5000/api
   ```

5. **Redeploy with environment variables**
   ```bash
   vercel --prod
   ```

## Configuration Files

### vercel.json
- Handles routing for React Router
- Sets build configuration
- Defines environment variables

### Environment Variables
- `REACT_APP_API_BASE_URL`: Backend API endpoint
- Can be overridden in Vercel dashboard for different environments

## Troubleshooting

### Common Issues

1. **Build Fails**
   - Check that all dependencies are in `package.json`
   - Ensure Node.js version is compatible (Vercel uses Node 18 by default)

2. **API Connection Issues**
   - Verify the backend API is accessible from the internet
   - Check CORS settings on your backend
   - Ensure the API URL is correct in environment variables

3. **Routing Issues**
   - The `vercel.json` file handles client-side routing
   - All routes should redirect to `index.html` for React Router

### CORS Configuration
If you encounter CORS issues, ensure your backend allows requests from your Vercel domain:
```python
# In your backend (example)
CORS(app, origins=[
    "http://localhost:3000",  # Local development
    "https://your-app.vercel.app"  # Vercel domain
])
```

## Custom Domain (Optional)

1. In Vercel dashboard, go to your project
2. Navigate to "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions

## Monitoring

- Check deployment logs in Vercel dashboard
- Monitor API calls in browser developer tools
- Use Vercel Analytics for performance insights

## Updates

To update your deployment:
1. Push changes to your Git repository
2. Vercel will automatically redeploy (if auto-deploy is enabled)
3. Or manually trigger deployment in Vercel dashboard

## Security Notes

- Never commit `.env` files with sensitive data
- Use Vercel's environment variables for configuration
- Consider using HTTPS for your backend API in production
