# 🚀 Complete AWS EC2 Deployment Guide with Ollama

This comprehensive guide walks you through deploying the AI Diwali Wish Maker on AWS EC2 with Ollama for dynamic AI content generation.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [EC2 Instance Setup](#ec2-instance-setup)
3. [Security Configuration](#security-configuration)
4. [Server Setup](#server-setup)
5. [Ollama Installation](#ollama-installation)
6. [Application Deployment](#application-deployment)
7. [Domain & SSL Setup (Optional)](#domain--ssl-setup)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Cost Optimization](#cost-optimization)
10. [Troubleshooting](#troubleshooting)

---

## 📦 Prerequisites

### What You'll Need:
- ✅ AWS Account ([Sign up here](https://aws.amazon.com/free/))
- ✅ Credit card for AWS billing
- ✅ Domain name (optional, for custom URL)
- ✅ Basic terminal/SSH knowledge
- ✅ 30-60 minutes of time

### Cost Estimate:
| Component | Monthly Cost | Notes |
|-----------|--------------|-------|
| EC2 t3.medium | ~$30-40 | CPU only, good for demos |
| EC2 g4dn.xlarge | ~$200-300 | With GPU, better performance |
| Storage (30GB) | ~$3 | EBS volume |
| Data Transfer | ~$0-10 | First 100GB free |
| **Total (CPU)** | **~$35-50/mo** | Budget option |
| **Total (GPU)** | **~$210-320/mo** | Performance option |

> 💡 **Tip:** Use t3.medium for testing, upgrade to GPU if you need faster responses.

---

## 🖥️ EC2 Instance Setup

### Step 1: Launch EC2 Instance

#### 1.1 Sign in to AWS Console
1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Sign in with your credentials
3. Select your preferred region (e.g., `us-east-1`)

#### 1.2 Navigate to EC2
1. Search for "EC2" in the services search bar
2. Click "Launch Instance"

#### 1.3 Configure Instance

**Name and Tags:**
```
Name: diwali-wish-maker-prod
Environment: production
```

**Application and OS Images (AMI):**
- Select: **Ubuntu Server 22.04 LTS**
- Architecture: **64-bit (x86)**
- Free tier eligible ✅

**Instance Type:**

Choose based on your needs:

| Instance Type | vCPUs | RAM | GPU | Best For | Cost/month |
|---------------|-------|-----|-----|----------|------------|
| **t3.small** | 2 | 2GB | No | Testing only | ~$15 |
| **t3.medium** | 2 | 4GB | No | Light production | ~$30 |
| **t3.large** | 2 | 8GB | No | Medium traffic | ~$60 |
| **g4dn.xlarge** | 4 | 16GB | Yes | Fast AI | ~$200 |
| **g4dn.2xlarge** | 8 | 32GB | Yes | High traffic | ~$400 |

**Recommendation:**
- **For Testing/Demo:** t3.medium (4GB RAM)
- **For Production:** t3.large or g4dn.xlarge (with GPU)

Select: **t3.medium** (good starting point)

**Key Pair:**
1. Click "Create new key pair"
2. Name: `diwali-wish-maker-key`
3. Type: RSA
4. Format: `.pem` (for Mac/Linux) or `.ppk` (for Windows PuTTY)
5. Click "Create key pair"
6. **IMPORTANT:** Save this file securely - you can't download it again!

**Network Settings:**
1. Click "Edit"
2. Auto-assign public IP: **Enable**
3. Firewall (security groups): **Create security group**
4. Security group name: `diwali-wish-maker-sg`
5. Description: `Security group for AI Diwali Wish Maker`

Add these rules:

| Type | Protocol | Port | Source | Description |
|------|----------|------|--------|-------------|
| SSH | TCP | 22 | My IP | SSH access |
| HTTP | TCP | 80 | Anywhere (0.0.0.0/0) | Web traffic |
| HTTPS | TCP | 443 | Anywhere (0.0.0.0/0) | Secure web |
| Custom TCP | TCP | 8501 | Anywhere (0.0.0.0/0) | Streamlit app |
| Custom TCP | TCP | 11434 | My IP | Ollama API (optional) |

> ⚠️ **Security Note:** For production, restrict SSH (port 22) to "My IP" only!

**Configure Storage:**
1. Size: **30 GB** (minimum recommended)
2. Volume type: **gp3** (newer, better performance)
3. Delete on termination: **Yes** (unless you want to keep data)

**Advanced Details** (expand this section):
1. Scroll down to "User data" (optional)
2. You can add startup script here (we'll do manual setup)

#### 1.4 Launch Instance

1. Review your configuration in the summary panel
2. Click **"Launch instance"**
3. Wait 1-2 minutes for instance to start
4. Click "View all instances"

#### 1.5 Note Your Instance Details

Once running, note these details:
```
Instance ID: i-0abc123def456789
Public IPv4 address: 54.123.45.67
Public IPv4 DNS: ec2-54-123-45-67.compute-1.amazonaws.com
```

---

## 🔒 Security Configuration

### Step 2: Set Up SSH Access

#### 2.1 Secure Your Key File (Mac/Linux)

```bash
# Move key to secure location
mkdir -p ~/.ssh
mv ~/Downloads/diwali-wish-maker-key.pem ~/.ssh/

# Set correct permissions
chmod 400 ~/.ssh/diwali-wish-maker-key.pem
```

#### 2.2 Connect to Your Instance

```bash
# Replace with your instance's public IP
ssh -i ~/.ssh/diwali-wish-maker-key.pem ubuntu@54.123.45.67
```

**First time connection:**
- You'll see a message about host authenticity
- Type `yes` and press Enter

**For Windows users (using PuTTY):**
1. Convert `.ppk` key using PuTTYgen
2. Use PuTTY with:
   - Host: `ubuntu@54.123.45.67`
   - Port: 22
   - Auth: Browse to your `.ppk` file

#### 2.3 Create SSH Config (Optional but Recommended)

On your local machine:

```bash
# Edit SSH config
nano ~/.ssh/config
```

Add:
```
Host diwali-prod
    HostName 54.123.45.67
    User ubuntu
    IdentityFile ~/.ssh/diwali-wish-maker-key.pem
    ServerAliveInterval 60
```

Now you can connect with just:
```bash
ssh diwali-prod
```

---

## 🛠️ Server Setup

### Step 3: Update and Install Dependencies

Once connected via SSH:

```bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install essential tools
sudo apt-get install -y \
    git \
    curl \
    wget \
    nano \
    htop \
    tmux \
    python3 \
    python3-pip \
    python3-venv \
    ffmpeg \
    nginx \
    certbot \
    python3-certbot-nginx

# Verify installations
python3 --version  # Should be 3.10+
git --version
ffmpeg -version
```

### Step 4: Set Up Firewall (UFW)

```bash
# Enable firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8501/tcp  # Streamlit

# Enable firewall
sudo ufw --force enable

# Check status
sudo ufw status
```

---

## 🤖 Ollama Installation

### Step 5: Install Ollama

#### 5.1 Download and Install

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Verify installation
ollama --version
```

#### 5.2 Pull Language Model

```bash
# Pull the llama3.2 model (this will take 5-10 minutes)
ollama pull llama3.2

# Verify model is downloaded
ollama list
```

**Expected output:**
```
NAME            ID              SIZE    MODIFIED
llama3.2:latest  abc123def456    2.0 GB  5 minutes ago
```

#### 5.3 Create Ollama Service

Create a systemd service to run Ollama on startup:

```bash
# Create service file
sudo nano /etc/systemd/system/ollama.service
```

Paste this content:
```ini
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=ubuntu
Environment="OLLAMA_HOST=0.0.0.0:11434"
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable Ollama service
sudo systemctl enable ollama

# Start Ollama
sudo systemctl start ollama

# Check status
sudo systemctl status ollama
```

**Expected output:**
```
● ollama.service - Ollama Service
     Loaded: loaded (/etc/systemd/system/ollama.service; enabled)
     Active: active (running) since ...
```

#### 5.4 Test Ollama

```bash
# Test Ollama API
curl http://localhost:11434/api/version

# Test generation
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Say hello",
  "stream": false
}'
```

---

## 📱 Application Deployment

### Step 6: Deploy the Streamlit App

#### 6.1 Clone Repository

```bash
# Create application directory
mkdir -p ~/apps
cd ~/apps

# Clone your repository
git clone https://github.com/YOUR_USERNAME/ai-diwali-wish-maker.git
cd ai-diwali-wish-maker

# Or if you haven't pushed to GitHub yet, upload files:
# Use scp from your local machine:
# scp -i ~/.ssh/diwali-wish-maker-key.pem -r /path/to/local/ai-wish-maker ubuntu@54.123.45.67:~/apps/
```

#### 6.2 Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installations
pip list | grep streamlit
pip list | grep gTTS
```

#### 6.3 Configure Environment Variables

```bash
# Create environment file
nano ~/.env_diwali
```

Add:
```bash
# Ollama Configuration
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=llama3.2

# Optional: OpenAI Fallback
# export OPENAI_API_KEY=sk-your-key-here
```

Load environment variables:
```bash
# Add to bash profile
echo "source ~/.env_diwali" >> ~/.bashrc
source ~/.bashrc
```

#### 6.4 Test the Application

```bash
# Test run (foreground)
cd ~/apps/ai-diwali-wish-maker
source venv/bin/activate
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Open in browser: `http://YOUR_EC2_PUBLIC_IP:8501`

**If it works, press Ctrl+C to stop and continue.**

#### 6.5 Create Streamlit Service

Create a systemd service for the Streamlit app:

```bash
# Create service file
sudo nano /etc/systemd/system/diwali-app.service
```

Paste:
```ini
[Unit]
Description=AI Diwali Wish Maker Streamlit App
After=network.target ollama.service
Requires=ollama.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/apps/ai-diwali-wish-maker
Environment="PATH=/home/ubuntu/apps/ai-diwali-wish-maker/venv/bin"
Environment="OLLAMA_HOST=http://localhost:11434"
Environment="OLLAMA_MODEL=llama3.2"
ExecStart=/home/ubuntu/apps/ai-diwali-wish-maker/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable diwali-app

# Start service
sudo systemctl start diwali-app

# Check status
sudo systemctl status diwali-app
```

#### 6.6 Verify Deployment

```bash
# Check if app is running
sudo systemctl status diwali-app

# Check logs
sudo journalctl -u diwali-app -f

# Check if port is listening
sudo netstat -tulpn | grep 8501
```

Visit: `http://YOUR_EC2_PUBLIC_IP:8501`

🎉 **Your app should now be live!**

---

## 🌐 Domain & SSL Setup (Optional)

### Step 7: Set Up Custom Domain with HTTPS

#### 7.1 Configure Domain

1. **Buy a domain** (from Namecheap, GoDaddy, etc.)
2. **Add DNS A Record:**
   - Host: `@` or `diwali`
   - Type: `A`
   - Value: `YOUR_EC2_PUBLIC_IP`
   - TTL: `300`

3. **Wait for DNS propagation** (5-30 minutes)

#### 7.2 Set Up Nginx Reverse Proxy

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/diwali-wish-maker
```

Paste:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

Enable the site:

```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/diwali-wish-maker /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

#### 7.3 Install SSL Certificate (Free with Let's Encrypt)

```bash
# Install SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow the prompts:
# 1. Enter email address
# 2. Agree to terms
# 3. Choose redirect (option 2)

# Test auto-renewal
sudo certbot renew --dry-run
```

**Your app is now live at:** `https://yourdomain.com` 🎉

---

## 📊 Monitoring & Maintenance

### Step 8: Set Up Monitoring

#### 8.1 View Application Logs

```bash
# Streamlit app logs
sudo journalctl -u diwali-app -f

# Ollama logs
sudo journalctl -u ollama -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System resources
htop
```

#### 8.2 Useful Management Commands

```bash
# Restart services
sudo systemctl restart diwali-app
sudo systemctl restart ollama
sudo systemctl restart nginx
sudo systemctl restart diwali-app && sleep 3 && echo "✓ Restarted. Now generate a wish in browser and watch:" && sudo journalctl -u diwali-app -f

# Stop services
sudo systemctl stop diwali-app

# Check status
sudo systemctl status diwali-app
sudo systemctl status ollama

# View resource usage
free -h          # Memory
df -h            # Disk space
top              # CPU usage
```

#### 8.3 Set Up CloudWatch (AWS Monitoring)

1. Go to AWS Console → CloudWatch
2. Create alarms for:
   - CPU Utilization > 80%
   - Disk Space > 80%
   - Network errors
3. Set up email notifications

#### 8.4 Backup Strategy

```bash
# Create backup script
nano ~/backup.sh
```

Add:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"

mkdir -p $BACKUP_DIR

# Backup application
tar -czf $BACKUP_DIR/app_$DATE.tar.gz ~/apps/ai-diwali-wish-maker

# Backup Ollama models (optional)
tar -czf $BACKUP_DIR/ollama_$DATE.tar.gz ~/.ollama

# Keep only last 7 backups
ls -t $BACKUP_DIR/*.tar.gz | tail -n +8 | xargs rm -f

echo "Backup completed: $DATE"
```

Make executable and schedule:
```bash
chmod +x ~/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /home/ubuntu/backup.sh
```

---

## 💰 Cost Optimization

### Step 9: Reduce AWS Costs

#### 9.1 Use Reserved Instances

- Save up to 70% for 1-year commitment
- AWS Console → EC2 → Reserved Instances

#### 9.2 Auto-Scaling (Advanced)

For variable traffic, set up auto-scaling:
1. Create AMI from your instance
2. Create Launch Template
3. Set up Auto Scaling Group
4. Configure scale-up/down rules

#### 9.3 Monitor Costs

```bash
# Set up billing alerts
AWS Console → Billing → Budgets → Create budget
- Set monthly budget (e.g., $50)
- Alert at 80% and 100%
```

#### 9.4 Stop Instance During Off-Hours

If this is for demo purposes only:

```bash
# Stop instance (from local machine)
aws ec2 stop-instances --instance-ids i-YOUR_INSTANCE_ID

# Start instance
aws ec2 start-instances --instance-ids i-YOUR_INSTANCE_ID
```

Or use AWS Lambda for scheduled start/stop.

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue 1: Can't Connect via SSH

**Solution:**
```bash
# Check security group allows your IP on port 22
# AWS Console → EC2 → Security Groups → Edit inbound rules

# Verify key permissions
chmod 400 ~/.ssh/diwali-wish-maker-key.pem

# Try verbose SSH
ssh -v -i ~/.ssh/diwali-wish-maker-key.pem ubuntu@YOUR_IP
```

#### Issue 2: Ollama Service Not Starting

**Solution:**
```bash
# Check logs
sudo journalctl -u ollama -n 50

# Restart service
sudo systemctl restart ollama

# Test manually
ollama serve

# Check if port is in use
sudo lsof -i :11434
```

#### Issue 3: Streamlit App Not Accessible

**Solution:**
```bash
# Check if service is running
sudo systemctl status diwali-app

# Check logs
sudo journalctl -u diwali-app -n 50

# Check if port is listening
sudo netstat -tulpn | grep 8501

# Verify security group allows port 8501
```

#### Issue 4: Out of Memory

**Solution:**
```bash
# Check memory usage
free -h

# Add swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

#### Issue 5: Ollama Model Slow

**Solution:**
1. Use smaller model: `ollama pull llama3.2:1b`
2. Upgrade to GPU instance (g4dn.xlarge)
3. Increase instance RAM

#### Issue 6: SSL Certificate Issues

**Solution:**
```bash
# Renew certificate manually
sudo certbot renew

# Check certificate status
sudo certbot certificates

# Test nginx config
sudo nginx -t
```

---

## 📝 Quick Reference Commands

### Daily Operations

```bash
# SSH into server
ssh -i ~/.ssh/diwali-wish-maker-key.pem ubuntu@YOUR_IP

# Check app status
sudo systemctl status diwali-app
sudo systemctl status ollama

# View logs
sudo journalctl -u diwali-app -f

# Restart app
sudo systemctl restart diwali-app

# Update code
cd ~/apps/ai-diwali-wish-maker
git pull
sudo systemctl restart diwali-app

# Check resources
htop
df -h
free -h
```

### Update Application

```bash
# SSH into server
ssh diwali-prod

# Navigate to app directory
cd ~/apps/ai-diwali-wish-maker

# Pull latest changes
git pull

# Activate virtual environment
source venv/bin/activate

# Update dependencies (if needed)
pip install -r requirements.txt

# Restart service
sudo systemctl restart diwali-app

# Check status
sudo systemctl status diwali-app
```

---

## 🎯 Post-Deployment Checklist

- [ ] EC2 instance running
- [ ] Security groups configured
- [ ] SSH access working
- [ ] Ollama installed and service running
- [ ] llama3.2 model downloaded
- [ ] Streamlit app installed
- [ ] App service running
- [ ] App accessible via public IP
- [ ] (Optional) Domain configured
- [ ] (Optional) SSL certificate installed
- [ ] Monitoring set up
- [ ] Backup script configured
- [ ] Cost alerts configured

---

## 📚 Additional Resources

- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Streamlit Deployment](https://docs.streamlit.io/deploy)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

---

## 🎉 Congratulations!

Your AI Diwali Wish Maker is now live on AWS EC2 with Ollama! 🚀

**Your deployment:**
- ✅ Running on dedicated server
- ✅ Dynamic AI content with Ollama
- ✅ Auto-restart on failures
- ✅ Professional setup with monitoring
- ✅ (Optional) Custom domain with SSL

**Share your app:**
```
http://YOUR_EC2_PUBLIC_IP:8501
# or
https://yourdomain.com
```

---

**Made with ❤️ for Diwali 2025** 🪔✨

Happy Diwali! May your deployments be smooth and your uptime be 100%! 🎊

