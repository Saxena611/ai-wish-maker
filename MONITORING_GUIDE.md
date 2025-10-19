# 📊 AWS Free Tier Monitoring Guide

## Traffic & Request Monitoring on Free Tier

This guide shows you how to monitor your Diwali Wish Maker app without exceeding AWS Free Tier limits.

---

## 🎯 What You Can Monitor (Free Tier)

### AWS CloudWatch (Free Tier Limits)
- ✅ 10 custom metrics
- ✅ 10 alarms
- ✅ 1 million API requests
- ✅ 5GB log ingestion
- ✅ 5GB log storage

### Application-Level Monitoring
- ✅ Request counter (unlimited)
- ✅ Nginx access logs (unlimited)
- ✅ Custom analytics (unlimited)

---

## 📈 Method 1: Simple Request Counter (Recommended)

### Add to Your App

This tracks:
- Total wishes generated
- Unique visitors (approximate)
- Peak usage times
- Most popular features

**File:** `request_tracker.py`

```python
import json
import os
from datetime import datetime
from pathlib import Path

class RequestTracker:
    def __init__(self, log_file="/home/ubuntu/apps/ai-diwali-wish-maker/analytics.json"):
        self.log_file = log_file
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        """Create log file if it doesn't exist"""
        if not os.path.exists(self.log_file):
            Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
            self._write_data({
                "total_wishes": 0,
                "daily_stats": {},
                "hourly_distribution": {},
                "wishes_by_day": []
            })
    
    def _read_data(self):
        """Read analytics data"""
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except:
            return {
                "total_wishes": 0,
                "daily_stats": {},
                "hourly_distribution": {},
                "wishes_by_day": []
            }
    
    def _write_data(self, data):
        """Write analytics data"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error writing analytics: {e}")
    
    def track_wish(self, relationship=None, language=None):
        """Track a wish generation"""
        data = self._read_data()
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        hour = now.strftime("%H:00")
        
        # Increment total
        data["total_wishes"] = data.get("total_wishes", 0) + 1
        
        # Track by day
        if today not in data["daily_stats"]:
            data["daily_stats"][today] = 0
        data["daily_stats"][today] += 1
        
        # Track by hour
        if hour not in data["hourly_distribution"]:
            data["hourly_distribution"][hour] = 0
        data["hourly_distribution"][hour] += 1
        
        # Track recent wishes
        wish_entry = {
            "timestamp": now.isoformat(),
            "relationship": relationship,
            "language": language
        }
        data["wishes_by_day"].append(wish_entry)
        
        # Keep only last 1000 entries
        data["wishes_by_day"] = data["wishes_by_day"][-1000:]
        
        self._write_data(data)
        return data["total_wishes"]
    
    def get_stats(self):
        """Get all statistics"""
        return self._read_data()
```

---

## 📊 Method 2: AWS CloudWatch Integration

### Setup CloudWatch Metrics (Free Tier Safe)

**On EC2:**

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb

# Create config
sudo nano /opt/aws/amazon-cloudwatch-agent/etc/config.json
```

**Config file:**

```json
{
  "metrics": {
    "namespace": "DiwaliWishMaker",
    "metrics_collected": {
      "cpu": {
        "measurement": [
          {"name": "cpu_usage_idle", "unit": "Percent"}
        ],
        "totalcpu": false
      },
      "mem": {
        "measurement": [
          {"name": "mem_used_percent", "unit": "Percent"}
        ]
      }
    }
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/nginx/access.log",
            "log_group_name": "/aws/ec2/diwali-app",
            "log_stream_name": "nginx-access"
          }
        ]
      }
    }
  }
}
```

**Start agent:**

```bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json -s
```

---

## 📝 Method 3: Nginx Access Logs (Best for Free Tier)

### Parse Nginx Logs for Analytics

**Create log parser script:**

```bash
nano ~/parse_logs.sh
```

```bash
#!/bin/bash
# Parse Nginx logs for analytics

LOG_FILE="/var/log/nginx/access.log"
OUTPUT="/home/ubuntu/analytics_report.txt"

echo "=== Diwali Wish Maker Analytics ===" > $OUTPUT
echo "Generated: $(date)" >> $OUTPUT
echo "" >> $OUTPUT

# Total requests
echo "📊 TOTAL REQUESTS" >> $OUTPUT
echo "Total: $(wc -l < $LOG_FILE)" >> $OUTPUT
echo "" >> $OUTPUT

# Unique visitors (approximate)
echo "👥 UNIQUE VISITORS (IPs)" >> $OUTPUT
echo "Unique IPs: $(awk '{print $1}' $LOG_FILE | sort -u | wc -l)" >> $OUTPUT
echo "" >> $OUTPUT

# Top 10 IPs
echo "🔝 TOP 10 VISITORS" >> $OUTPUT
awk '{print $1}' $LOG_FILE | sort | uniq -c | sort -rn | head -10 >> $OUTPUT
echo "" >> $OUTPUT

# Requests by hour
echo "⏰ REQUESTS BY HOUR" >> $OUTPUT
awk '{print $4}' $LOG_FILE | cut -d: -f2 | sort | uniq -c | sort -k2 >> $OUTPUT
echo "" >> $OUTPUT

# Status codes
echo "📈 HTTP STATUS CODES" >> $OUTPUT
awk '{print $9}' $LOG_FILE | sort | uniq -c | sort -rn >> $OUTPUT
echo "" >> $OUTPUT

# Most accessed pages
echo "📄 TOP PAGES" >> $OUTPUT
awk '{print $7}' $LOG_FILE | sort | uniq -c | sort -rn | head -10 >> $OUTPUT
echo "" >> $OUTPUT

cat $OUTPUT
```

**Make executable and run:**

```bash
chmod +x ~/parse_logs.sh
~/parse_logs.sh
```

**Schedule daily reports with cron:**

```bash
crontab -e
# Add: 0 23 * * * /home/ubuntu/parse_logs.sh > /home/ubuntu/daily_report_$(date +\%Y\%m\%d).txt
```

---

## 🔍 Method 4: Google Analytics (Free & Powerful)

### Add Google Analytics to Your App

**1. Get Google Analytics ID:**
- Go to analytics.google.com
- Create property
- Get tracking ID (G-XXXXXXXXXX)

**2. Add to app.py:**

```python
# In app.py, add to the <head> section:

def add_google_analytics():
    ga_id = "G-XXXXXXXXXX"  # Replace with your GA ID
    st.markdown(f"""
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{ga_id}');
      
      // Track wish generation
      function trackWishGeneration(relationship, language) {{
        gtag('event', 'generate_wish', {{
          'relationship': relationship,
          'language': language
        }});
      }}
    </script>
    """, unsafe_allow_html=True)

# Call at start of main()
add_google_analytics()
```

**Benefits:**
- ✅ Real-time visitors
- ✅ Geographic data
- ✅ Device types (mobile/desktop)
- ✅ User flow
- ✅ Bounce rate
- ✅ Session duration

---

## 📱 Method 5: Simple Counter Dashboard

### Create Analytics Dashboard

**File:** `dashboard.py`

```python
import streamlit as st
import json
from datetime import datetime, timedelta
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Analytics Dashboard", page_icon="📊")

st.title("📊 Diwali Wish Maker Analytics")

# Load data
try:
    with open('/home/ubuntu/apps/ai-diwali-wish-maker/analytics.json', 'r') as f:
        data = json.load(f)
except:
    st.error("No analytics data found")
    st.stop()

# Key metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Wishes", data.get("total_wishes", 0))

with col2:
    today = datetime.now().strftime("%Y-%m-%d")
    today_count = data.get("daily_stats", {}).get(today, 0)
    st.metric("Today's Wishes", today_count)

with col3:
    # Average per day
    daily = data.get("daily_stats", {})
    avg = sum(daily.values()) / len(daily) if daily else 0
    st.metric("Avg. Daily Wishes", f"{avg:.1f}")

# Daily chart
st.subheader("📈 Daily Wishes")
if data.get("daily_stats"):
    df_daily = pd.DataFrame([
        {"Date": k, "Wishes": v} 
        for k, v in data["daily_stats"].items()
    ])
    fig = px.bar(df_daily, x="Date", y="Wishes", 
                 title="Wishes Generated Per Day")
    st.plotly_chart(fig)

# Hourly distribution
st.subheader("⏰ Peak Hours")
if data.get("hourly_distribution"):
    df_hourly = pd.DataFrame([
        {"Hour": k, "Count": v} 
        for k, v in data["hourly_distribution"].items()
    ])
    fig2 = px.bar(df_hourly, x="Hour", y="Count",
                  title="Wishes by Hour of Day")
    st.plotly_chart(fig2)

# Recent wishes
st.subheader("🕐 Recent Wishes")
recent = data.get("wishes_by_day", [])[-20:]
if recent:
    df_recent = pd.DataFrame(recent)
    st.dataframe(df_recent)
```

**Access dashboard:**
```bash
streamlit run dashboard.py --server.port 8502
```

Then visit: `http://YOUR_EC2_IP:8502`

---

## 🚨 Method 6: Set Up Alerts (Free Tier)

### Email Alerts for High Traffic

**Create alert script:**

```bash
nano ~/check_traffic.sh
```

```bash
#!/bin/bash
# Alert if traffic exceeds threshold

THRESHOLD=100  # Alert if > 100 requests/hour
LOG_FILE="/var/log/nginx/access.log"

# Count requests in last hour
HOUR_AGO=$(date -d '1 hour ago' +"%d/%b/%Y:%H")
REQUESTS=$(grep "$HOUR_AGO" $LOG_FILE | wc -l)

if [ $REQUESTS -gt $THRESHOLD ]; then
    # Send email (requires mailutils)
    echo "High traffic detected: $REQUESTS requests in last hour" | \
    mail -s "Traffic Alert - Diwali App" your@email.com
fi
```

**Schedule check every hour:**

```bash
chmod +x ~/check_traffic.sh
crontab -e
# Add: 0 * * * * /home/ubuntu/check_traffic.sh
```

---

## 📊 Method 7: AWS Cost Explorer

Monitor your costs to stay within free tier:

**AWS Console:**
1. Go to AWS Cost Explorer
2. Set up daily cost alerts
3. Budget: Set monthly budget ($1-5)
4. Alert if approaching limit

---

## 🎯 Recommended Setup (Best for Free Tier)

### Simple & Effective Monitoring Stack:

1. **Request Tracker in App** (Method 1)
   - Tracks every wish generation
   - No AWS costs
   - Instant data

2. **Nginx Log Parser** (Method 3)
   - Daily/weekly reports
   - Free & reliable
   - Detailed analytics

3. **Google Analytics** (Method 4)
   - Real-time monitoring
   - Geographic data
   - Device tracking
   - Free forever

4. **AWS CloudWatch Basic** (Method 2)
   - EC2 health monitoring
   - Within free tier limits
   - CPU/Memory alerts

---

## 📝 Quick Setup Script

```bash
#!/bin/bash
# Setup monitoring on EC2

cd ~/apps/ai-diwali-wish-maker

# Create analytics directory
mkdir -p logs

# Create analytics file
touch analytics.json
echo '{"total_wishes":0,"daily_stats":{},"hourly_distribution":{},"wishes_by_day":[]}' > analytics.json

# Set permissions
chmod 666 analytics.json

# Install log parser
cat > parse_logs.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/nginx/access.log"
echo "Total Requests: $(wc -l < $LOG_FILE)"
echo "Unique IPs: $(awk '{print $1}' $LOG_FILE | sort -u | wc -l)"
echo "Last Hour: $(grep "$(date -d '1 hour ago' +"%d/%b/%Y:%H")" $LOG_FILE | wc -l)"
EOF

chmod +x parse_logs.sh

echo "✓ Monitoring setup complete!"
echo ""
echo "Run './parse_logs.sh' to see stats"
```

---

## 📱 View Your Stats

### Quick Commands:

```bash
# Total wishes today
grep "$(date +%d/%b/%Y)" /var/log/nginx/access.log | wc -l

# Unique visitors today
grep "$(date +%d/%b/%Y)" /var/log/nginx/access.log | awk '{print $1}' | sort -u | wc -l

# Peak hour today
grep "$(date +%d/%b/%Y)" /var/log/nginx/access.log | cut -d: -f2 | sort | uniq -c | sort -rn | head -1

# View analytics JSON
cat ~/apps/ai-diwali-wish-maker/analytics.json | python3 -m json.tool
```

---

## 🎉 Summary

**Best Free Tier Monitoring:**
1. ✅ In-app request tracker (unlimited, free)
2. ✅ Nginx log analysis (unlimited, free)
3. ✅ Google Analytics (free, powerful)
4. ✅ Basic CloudWatch (within free tier)

**Avoid:**
- ❌ Paid monitoring services
- ❌ Excessive CloudWatch metrics (>10)
- ❌ High-frequency CloudWatch logs
- ❌ Third-party paid analytics

---

**Happy Monitoring! 📊✨**

