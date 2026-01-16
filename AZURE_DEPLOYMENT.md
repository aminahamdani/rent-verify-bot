# 🚀 RentVerify - Azure App Service Deployment Guide

## 📋 Prerequisites

Before deploying to Azure, ensure you have:
- ✅ Azure account (Free tier available)
- ✅ Azure App Service created
- ✅ GitHub repository ready
- ✅ Environment variables prepared
- ✅ PostgreSQL database (Azure Database or external like Neon)

---

## 🎯 Quick Deployment Steps

### **Step 1: Create Azure App Service**

1. **Go to Azure Portal**
   - Visit: https://portal.azure.com/
   - Sign in or create a free account

2. **Create App Service**
   - Click **"Create a resource"**
   - Search for **"Web App"**
   - Click **"Create"**

3. **Configure Basic Settings**
   ```
   Subscription: Your subscription
   Resource Group: Create new (e.g., "rentverify-rg")
   Name: rentverify-app (or your unique name)
   Publish: Code
   Runtime stack: Python 3.11
   Operating System: Linux
   Region: Choose closest to you (e.g., East US)
   App Service Plan: Create new (Free F1 tier for testing)
   ```

4. **Review and Create**
   - Review settings
   - Click **"Create"**
   - Wait 2-3 minutes for deployment

---

### **Step 2: Configure Deployment from GitHub**

1. **In Azure Portal**
   - Navigate to your App Service
   - Go to **"Deployment"** → **"Deployment Center"**

2. **Connect to GitHub**
   - Source: **GitHub**
   - Sign in with GitHub
   - Organization: Your GitHub username
   - Repository: `aminahamdani/rent-verify-bot`
   - Branch: `main`

3. **Configure Build**
   - Build provider: **GitHub Actions** (recommended)
   - Or use **Local Git** or **Zip deploy**

4. **Save Configuration**
   - Azure will automatically create deployment workflow
   - First deployment will start automatically

---

### **Step 3: Configure Environment Variables**

1. **In Azure Portal**
   - Go to your App Service
   - Navigate to **"Configuration"** → **"Application settings"**

2. **Add Environment Variables**
   Click **"+ New application setting"** and add each:

   ```env
   SECRET_KEY=8ecf4b0387239d9941b8871a4374dde452bd77fb62bf78053a62cf3e18bae2b8
   FLASK_ENV=production
   ADMIN_USERNAME=amina
   ADMIN_PASSWORD=0000
   TWILIO_ACCOUNT_SID=AC17efd4d5f4a68b402abba142a1258343
   TWILIO_AUTH_TOKEN=0aa93cf55621f111b0c7aa0fdb970d02
   TWILIO_PHONE_NUMBER=+16802082305
   DATABASE_URL=postgresql://neondb_owner:npg_VCl41aLdkqJN@ep-divine-smoke-ahao7irw-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
   PORT=8000
   ```

3. **Save Settings**
   - Click **"Save"**
   - Wait for settings to apply

---

### **Step 4: Configure Startup Command**

1. **In Azure Portal**
   - Go to **"Configuration"** → **"General settings"**

2. **Set Startup Command**
   ```
   gunicorn app:app --bind 0.0.0.0:8000 --workers 2 --timeout 60 --log-level info
   ```
   
   **OR** use the startup script:
   ```
   startup.sh
   ```

3. **Save Configuration**
   - Click **"Save"**
   - Restart the app if needed

---

### **Step 5: Enable Always On (Optional but Recommended)**

1. **In Azure Portal**
   - Go to **"Configuration"** → **"General settings"**

2. **Enable "Always On"**
   - Toggle **"Always On"** to **ON**
   - This prevents the app from sleeping on free tier

3. **Save Settings**

---

## 🔧 Alternative: Manual Deployment Methods

### **Method 1: GitHub Actions (Recommended)**

Azure automatically creates a GitHub Actions workflow when you connect to GitHub.

**Check GitHub Actions:**
1. Go to your GitHub repository
2. Click **"Actions"** tab
3. You'll see Azure deployment workflow running

---

### **Method 2: Azure CLI**

1. **Install Azure CLI**
   ```bash
   # Windows (PowerShell)
   Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi
   Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'
   ```

2. **Login to Azure**
   ```bash
   az login
   ```

3. **Deploy from GitHub**
   ```bash
   az webapp deployment source config --name rentverify-app \
     --resource-group rentverify-rg \
     --repo-url https://github.com/aminahamdani/rent-verify-bot \
     --branch main \
     --manual-integration
   ```

---

### **Method 3: Zip Deploy**

1. **Create ZIP file**
   ```bash
   # Exclude unnecessary files
   zip -r deploy.zip . -x "*.git*" -x "*venv*" -x "*.env*" -x "*__pycache__*"
   ```

2. **Deploy via Azure CLI**
   ```bash
   az webapp deploy --resource-group rentverify-rg \
     --name rentverify-app \
     --src-path deploy.zip \
     --type zip
   ```

---

## 🗄️ Database Options

### **Option 1: Use Existing Neon PostgreSQL (Recommended)**
- Your current `DATABASE_URL` from Neon will work
- Just add it to Azure App Settings

### **Option 2: Azure Database for PostgreSQL**

1. **Create Azure Database**
   - In Azure Portal, create **"Azure Database for PostgreSQL"**
   - Choose **"Flexible Server"** (cheaper)
   - Configure:
     ```
     Server name: rentverify-db
     Region: Same as App Service
     PostgreSQL version: 14 or 15
     Compute: Burstable B1ms (Free tier available)
     Storage: 32 GB
     ```

2. **Get Connection String**
   - Go to **"Connection strings"**
   - Copy the connection string
   - Format: `postgresql://user:password@host:5432/database`

3. **Update Environment Variable**
   - Replace `DATABASE_URL` in App Service with Azure DB connection string

---

## 🔍 Verify Deployment

### **1. Check App Status**
- Go to Azure Portal → Your App Service
- Check **"Overview"** → Status should be **"Running"**

### **2. View Logs**
- Go to **"Log stream"** to see real-time logs
- Or check **"App Service logs"**

### **3. Test Your App**
- Visit: `https://rentverify-app.azurewebsites.net`
- Should redirect to login page
- Login with your credentials

### **4. Test SMS Webhook**
- Update Twilio webhook to: `https://rentverify-app.azurewebsites.net/sms`
- Send test SMS
- Check dashboard for new record

---

## 📱 Configure Twilio Webhook

1. **Get Your Azure URL**
   - Format: `https://your-app-name.azurewebsites.net`

2. **Update Twilio Webhook**
   - Go to: https://console.twilio.com/
   - Navigate to **Phone Numbers** → **Active Numbers**
   - Click your phone number
   - Under **"Messaging Configuration"**
   - Set **"A MESSAGE COMES IN"**:
     ```
     URL: https://your-app-name.azurewebsites.net/sms
     HTTP Method: POST
     ```
   - Click **"Save"**

---

## 🔒 Security Best Practices

### **1. Enable HTTPS**
- Azure automatically provides HTTPS
- Free SSL certificate included
- Force HTTPS in App Service settings

### **2. Restrict Access (Optional)**
- Go to **"Networking"** → **"Access restrictions"**
- Add IP allowlist if needed

### **3. Application Insights (Optional)**
- Enable **Application Insights** for monitoring
- Go to **"Application Insights"** → **"Turn on Application Insights"**

---

## 🐛 Troubleshooting

### **Issue: App won't start**
**Solution:**
1. Check **"Log stream"** for errors
2. Verify startup command is correct
3. Check environment variables are set
4. Review **"Deployment Center"** for build errors

### **Issue: 502 Bad Gateway**
**Solution:**
1. Check if app is running (Status = Running)
2. Verify startup command format
3. Check application logs
4. Restart the app service

### **Issue: Database connection fails**
**Solution:**
1. Verify `DATABASE_URL` is correct
2. Check database firewall rules (if using Azure DB)
3. Test connection from App Service console

### **Issue: Environment variables not working**
**Solution:**
1. Ensure variables are in **"Application settings"** (not connection strings)
2. Restart app after adding variables
3. Check variable names match exactly (case-sensitive)

---

## 💰 Azure Pricing

### **Free Tier (F1)**
- ✅ 1 GB storage
- ✅ 60 minutes compute/day
- ✅ Limited to 1 app per subscription
- ✅ Custom domain not included

### **Basic Tier (B1) - $13/month**
- ✅ Always On included
- ✅ Custom domains
- ✅ No daily compute limits
- ✅ 3.5 GB storage

### **Recommended for Production**
- **App Service Plan**: B1 or higher
- **Database**: Azure Database for PostgreSQL Flexible Server (B1ms - ~$12/month)
- **Total**: ~$25/month

---

## 📊 Monitoring

### **Application Insights**
1. Enable in **"Application Insights"**
2. View:
   - Request rates
   - Response times
   - Error rates
   - Dependencies

### **Log Stream**
- Real-time application logs
- Go to **"Log stream"** in Azure Portal

### **Metrics**
- Go to **"Metrics"** to view:
  - CPU usage
  - Memory usage
  - HTTP requests
  - Response times

---

## 🔄 Continuous Deployment

Once configured, Azure will:
- ✅ Automatically deploy on every push to `main` branch
- ✅ Run build process
- ✅ Update application
- ✅ Keep app running

**To trigger manual deployment:**
1. Go to **"Deployment Center"**
2. Click **"Sync"** or **"Redeploy"**

---

## ✅ Post-Deployment Checklist

- [ ] App is running (Status = Running)
- [ ] Can access login page
- [ ] Can login with admin credentials
- [ ] Database connection working
- [ ] Twilio webhook configured
- [ ] Test SMS received and stored
- [ ] Dashboard displays records
- [ ] CSV export works
- [ ] Environment variables set correctly
- [ ] HTTPS enabled
- [ ] Logs are being captured

---

## 📚 Additional Resources

- **Azure App Service Docs**: https://docs.microsoft.com/azure/app-service/
- **Python on Azure**: https://docs.microsoft.com/azure/app-service/quickstart-python
- **Azure CLI Reference**: https://docs.microsoft.com/cli/azure/webapp
- **Troubleshooting Guide**: https://docs.microsoft.com/azure/app-service/troubleshoot-diagnostic-logs

---

## 🎉 Success!

Your RentVerify app is now deployed on Azure! 

**Your app URL:** `https://your-app-name.azurewebsites.net`

**Next Steps:**
1. Test all features
2. Monitor performance
3. Set up custom domain (optional)
4. Configure backups
5. Set up alerts

---

**Last Updated:** January 16, 2026
**Repository:** https://github.com/aminahamdani/rent-verify-bot
