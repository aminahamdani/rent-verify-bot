# Azure Deployment Troubleshooting

## Error: "ModuleNotFoundError: No module named 'app'"

This error means Azure can't find your `app.py` file. This usually happens when:
1. Code hasn't been deployed from GitHub yet
2. GitHub connection isn't configured
3. Deployment hasn't completed

## Solution: Complete GitHub Deployment

### Step 1: Configure GitHub Connection
1. Go to **Deployment Center** in Azure Portal
2. Make sure **GitHub** is selected as source
3. Click **"Authorize"** button if not already authorized
4. Select:
   - **Organization**: Your GitHub username
   - **Repository**: `aminahamdani/rent-verify-bot`
   - **Branch**: `main`
5. Click **"Save"**

### Step 2: Trigger Deployment
After saving, Azure will:
- Create a GitHub Actions workflow file
- Automatically trigger first deployment
- Deploy your code to Azure

### Step 3: Wait for Deployment
1. Go to **Deployment Center** → **Logs** tab
2. You should see deployment progress
3. Wait 2-5 minutes for deployment to complete

### Step 4: Restart App
Once deployment shows "Success":
1. Go to **Overview**
2. Click **"Restart"**
3. Wait 1-2 minutes
4. Check **Log stream** - should see app starting correctly

## Alternative: Check GitHub Actions

1. Go to your GitHub repository: https://github.com/aminahamdani/rent-verify-bot
2. Click **"Actions"** tab
3. You should see an Azure deployment workflow
4. Click on it to see deployment status
5. Wait for it to complete (green checkmark)

## Quick Fix Checklist

- [ ] GitHub connected in Deployment Center
- [ ] Repository selected correctly
- [ ] Branch set to `main`
- [ ] Deployment triggered (check Logs tab)
- [ ] GitHub Actions workflow running (check GitHub)
- [ ] Deployment completed successfully
- [ ] App restarted after deployment

## Still Not Working?

1. **Manual Sync**: In Deployment Center, click **"Sync"** button
2. **Check Logs**: Go to Deployment Center → Logs tab
3. **GitHub Actions**: Check your GitHub repo → Actions tab
4. **Restart**: Always restart app after deployment
