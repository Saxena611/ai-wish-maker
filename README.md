# 🪔 AI Diwali Wish Maker ✨

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Create personalized Diwali greetings with AI-powered voice wishes and beautiful greeting cards!

## ✨ Features

### 🎙️ **Voice Wish Generator**
- AI-generated personalized messages using Ollama/OpenAI
- Text-to-Speech with natural voice pacing (115% speed)
- Optional background music mixing
- Multiple personalities and tones
- Multi-language support (English, Hindi, Hinglish)
- High-quality MP3 download

### 🎨 **Card Generator**  
- Stunning AI-generated greeting cards
- Beautiful visual effects:
  - Radial gradient backgrounds
  - Glowing diyas with realistic flames
  - Sparkling stars and decorative patterns
  - Text shadows and glow effects
  - Elegant double borders
- 3 Visual themes: Traditional, Modern, Minimal
- Customizable personalities and languages
- PNG download for sharing

## 🚀 Quick Start

### **Option 1: Quick Start with Ollama (Recommended)**

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-diwali-wish-maker.git
cd ai-diwali-wish-maker

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (for audio processing)
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt-get install ffmpeg

# Windows: Download from https://ffmpeg.org

# Install Ollama (if not already installed)
# Visit: https://ollama.ai/download
# Or: curl https://ollama.ai/install.sh | sh

# Run the automated setup script
./start_with_ollama.sh
```

This script will:
- ✅ Check for Ollama installation
- ✅ Start Ollama server if needed
- ✅ Download llama3.2 model automatically
- ✅ Start the Streamlit app

Open your browser to `http://localhost:8501`

### **Option 2: Manual Setup**

```bash
# Clone and install dependencies
git clone https://github.com/YOUR_USERNAME/ai-diwali-wish-maker.git
cd ai-diwali-wish-maker
pip install -r requirements.txt

# Start Ollama (for AI text generation)
ollama serve &
ollama pull llama3.2

# Run the app
streamlit run app.py
```

### **Option 3: Docker with Ollama (Production Ready)**

```bash
# Deploy everything with Docker Compose
docker-compose up -d

# Pull the model (one-time setup)
docker exec -it ollama-server ollama pull llama3.2

# Access the app
# http://localhost:8501
```

This deploys both Ollama and the Streamlit app in containers!

## 📦 Tech Stack

- **Framework:** Streamlit
- **AI/LLM:** Ollama (llama3.2) / OpenAI GPT
- **Text-to-Speech:** gTTS (Google Text-to-Speech)
- **Image Generation:** Pillow (PIL)
- **Audio Processing:** pydub
- **Language:** Python 3.11+

## 🎯 Usage

### **Voice Wish Generator**

1. Choose "🎙️ Voice Wish Generator" from home page
2. Enter sender and recipient names
3. Select personality, tone, and language
4. Click "✨ Generate Wish"
5. Review and edit the AI-generated text
6. Click "🎙️ Generate Voice"
7. Listen and download your personalized voice wish!

### **Card Generator**

1. Choose "🎨 Card Generator" from home page
2. Enter sender and recipient names
3. Select personality, language, and visual theme
4. Click "✨ Generate My Diwali Card"
5. Review and edit the message
6. Click "🎨 Generate Card Image"
7. Download your beautiful greeting card!

## 🌟 Screenshots

### Home Page
Beautiful selection interface with gradient cards

### Voice Wish
AI-generated personalized voice messages with background music

### Greeting Cards
Stunning cards with:
- Radial gradients
- Glowing diyas
- Sparkling effects
- Professional typography

## 🚀 Deployment

### **Quick Deployment Options**

| Option | Difficulty | Cost | Best For | Guide |
|--------|-----------|------|----------|-------|
| **Streamlit Cloud** | ⭐ Easy | Free* | Quick demos | [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) |
| **Docker Compose** | ⭐⭐ Medium | Free | Local servers | [OLLAMA_DEPLOYMENT.md](OLLAMA_DEPLOYMENT.md) |
| **AWS EC2** | ⭐⭐⭐ Medium | $35-50/mo | Production | [AWS_EC2_DEPLOYMENT_GUIDE.md](AWS_EC2_DEPLOYMENT_GUIDE.md) |
| **Cloud VM (GCP/Azure)** | ⭐⭐⭐ Medium | $40-60/mo | Production | [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) |

*Note: Streamlit Cloud requires OpenAI API or remote Ollama server for AI features

### **Recommended: AWS EC2 with Ollama**

For a production-ready deployment with full Ollama support:

1. **[Follow our comprehensive AWS EC2 guide](AWS_EC2_DEPLOYMENT_GUIDE.md)** (step-by-step)
2. Launch EC2 instance (t3.medium or larger)
3. Install Ollama and dependencies
4. Deploy the app
5. Optional: Add custom domain and SSL

**Result:** Fully functional app at `http://your-ec2-ip:8501` or your custom domain!

### **Quick Streamlit Cloud Deployment**

For quick demos (requires OpenAI API):

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your repository
4. Add `OPENAI_API_KEY` in secrets
5. Click "Deploy"

Your app will be live at: `https://YOUR-USERNAME-ai-diwali-wish-maker.streamlit.app`

## 📁 Project Structure

```
ai-wish-maker/
├── app.py                        # Main Streamlit application
├── requirements.txt              # Python dependencies
├── packages.txt                  # System dependencies (ffmpeg)
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose for Ollama + App
├── start_with_ollama.sh          # Quick start script for Ollama
├── .streamlit/
│   └── config.toml              # Streamlit configuration
├── README.md                     # This file (you are here)
├── DEPLOYMENT_GUIDE.md           # General deployment guide
├── OLLAMA_DEPLOYMENT.md          # Ollama deployment scenarios
├── AWS_EC2_DEPLOYMENT_GUIDE.md   # Step-by-step AWS EC2 guide
├── VOICE_ENHANCEMENTS.md         # Voice quality features
└── BACKGROUND_MUSIC_GUIDE.md     # Music integration guide
```

## 🎨 Themes

### Traditional 🪔
- Warm orange to deep red gradients
- Golden accents
- Perfect for family wishes

### Modern 💜
- Purple to indigo gradients
- Pink highlights
- Perfect for friends

### Minimal 🤍
- Clean gray tones
- Orange accents
- Perfect for formal wishes

## 🔧 Configuration

### Environment Variables

The app supports configuration via environment variables:

```bash
# Ollama Configuration (Primary AI)
export OLLAMA_HOST=http://localhost:11434   # Ollama server URL
export OLLAMA_MODEL=llama3.2                # Model to use

# OpenAI Fallback (Optional)
export OPENAI_API_KEY=sk-...                # OpenAI API key
```

**For Streamlit Cloud deployment**, add these as secrets:
```toml
# .streamlit/secrets.toml
OLLAMA_HOST = "http://your-ollama-server:11434"
OLLAMA_MODEL = "llama3.2"
OPENAI_API_KEY = "sk-..."  # optional
```

### Background Music (Optional)

1. Add `background_music.mp3` to project root
2. Check "🎵 Background Music" option
3. Music will be mixed with voice at -15dB

See [BACKGROUND_MUSIC_GUIDE.md](BACKGROUND_MUSIC_GUIDE.md) for details.

### LLM Setup Options

**Option 1: Ollama (Recommended for local/private deployment)**
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Start server
ollama serve

# Pull model
ollama pull llama3.2
```

**Option 2: OpenAI (Easy for cloud deployment)**
```bash
export OPENAI_API_KEY="your-api-key"
streamlit run app.py
```

**Option 3: Hybrid (Best reliability)**
```bash
# Use Ollama as primary, OpenAI as fallback
export OLLAMA_HOST=http://localhost:11434
export OPENAI_API_KEY="sk-..."
```

See [OLLAMA_DEPLOYMENT.md](OLLAMA_DEPLOYMENT.md) for advanced deployment scenarios.

## 📊 Features Comparison

| Feature | Voice Wish | Card Generator |
|---------|-----------|----------------|
| AI Text Generation | ✅ | ✅ |
| Personality Options | ✅ | ✅ |
| Multiple Languages | ✅ | ✅ |
| Download | MP3 | PNG |
| Background Music | ✅ | - |
| Visual Themes | - | ✅ |
| Editable | ✅ | ✅ |

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎉 Acknowledgments

- Streamlit for the amazing framework
- Ollama for local LLM support
- gTTS for text-to-speech
- PIL/Pillow for image generation

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter)

Project Link: [https://github.com/YOUR_USERNAME/ai-diwali-wish-maker](https://github.com/YOUR_USERNAME/ai-diwali-wish-maker)

## 🌟 Star History

If you like this project, please give it a ⭐ on GitHub!

---

**Made with ❤️ for Diwali 2025** 🪔✨

Happy Diwali! May your code be bug-free and your deployments successful! 🎊
